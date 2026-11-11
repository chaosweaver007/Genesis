"""Receiver-side authorization boundary tests (reference-only, no network)."""

from __future__ import annotations

import sys
import tempfile
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENESIS_ROOT = PROJECT_ROOT / "Genesis"
if str(GENESIS_ROOT) not in sys.path:
    sys.path.insert(0, str(GENESIS_ROOT))

from auth.enforcer import (
    ActionOutcome,
    InProcessRevocations,
    ReceiverEnforcer,
    SQLiteNonceStore,
)
from uds_v1_1 import (
    AuthorityEvidence,
    AuthorizationStateRegistry,
    CanonicalExecutionRequest,
    CapabilityBroker,
    ConsentObject,
    ExecutionPermitVerifier,
    HMACDevelopmentSigner,
)

NOW = datetime(2026, 11, 9, 14, 0, tzinfo=timezone.utc)
POLICY_DIGEST = "sha256:" + "ab" * 32
RESULT_DIGEST = "sha256:" + "cd" * 32
ISSUER = "uds-capability-broker:test"
AUDIENCE = "genesis.executor.v1"


def request(effect_class="E1"):
    return CanonicalExecutionRequest(
        action="memory.write",
        resource="vault.journal.reflections",
        parameters={"entry_ref": "local:example", "encryption": "client"},
        effect_class=effect_class,
        audience=AUDIENCE,
    )


def consent():
    return ConsentObject(
        consent_id="urn:uds:consent:reference",
        subject_ref="pairwise:user:reference",
        controller_ref="pairwise:user:reference",
        authorized_actions=("memory.write",),
        resource_scopes=("vault.journal.*",),
        purpose_digest="sha256:" + "ee" * 32,
        issued_at="2026-11-09T13:00:00Z",
        expires_at="2026-11-09T15:00:00Z",
        consent_epoch=4,
        revocation_state="ACTIVE",
        allow_sub_delegation=False,
        policy_version="UDS-v1.1",
        policy_digest=POLICY_DIGEST,
    )


def evidence():
    return AuthorityEvidence(
        evidence_id="urn:uds:evidence:reference",
        principal_ref="pairwise:user:reference",
        resource_scope="vault.journal.*",
        allowed_actions=("memory.write",),
        authority_epoch=6,
        not_before="2026-11-09T13:00:00Z",
        expires_at="2026-11-09T15:00:00Z",
        evidence_status="VERIFIED",
        evidence_digest="sha256:" + "ff" * 32,
    )


class ReceiverAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.now = NOW
        self.signer = HMACDevelopmentSigner(b"S" * 32, key_epoch=3)
        self.state = AuthorizationStateRegistry(
            consent_epoch=4,
            broker_key_epoch=3,
            authority_epoch=6,
            policy_digest=POLICY_DIGEST,
        )
        self.revocations = InProcessRevocations()
        self.nonce_store = SQLiteNonceStore(
            Path(self.temp_dir.name) / "authorization.db"
        )
        self.verifier = ExecutionPermitVerifier(signer=self.signer)
        self.enforcer = ReceiverEnforcer(
            verifier=self.verifier,
            state=self.state,
            nonce_store=self.nonce_store,
            revocations=self.revocations,
            audience=AUDIENCE,
            trusted_issuer=ISSUER,
            clock=lambda: self.now,
        )
        self.req = request()
        self.permit_counter = 0
        self.broker = CapabilityBroker(
            signer=self.signer,
            issuer=ISSUER,
            permit_ttl_seconds=60,
            permit_id_factory=self._next_permit_id,
            nonce_factory=lambda: "ab" * 32,
        )
        self.permit = self._issue_permit()
        self.action = Mock(
            return_value=ActionOutcome({"status": "saved"}, RESULT_DIGEST)
        )

    def _next_permit_id(self):
        self.permit_counter += 1
        return f"urn:uds:permit:receiver-{self.permit_counter}"

    def _issue_permit(self):
        return self.broker.issue_permit(
            consent=consent(),
            authority_evidence=evidence(),
            request=self.req,
            state=self.state,
            now=NOW,
        )

    def _execute(self, permit=None):
        return self.enforcer.execute(
            permit=self.permit if permit is None else permit,
            request=self.req,
            action=self.action,
        )

    def _assert_denied(self, result, reason):
        self.assertEqual(result.status_code, 403)
        self.assertIsNone(result.value)
        self.assertEqual(result.receipt["auth_status"], "DENY")
        self.assertEqual(result.receipt["reason_code"], reason)
        self.action.assert_not_called()

    def test_valid_permit_executes(self):
        result = self._execute()
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.receipt["auth_status"], "PASS")
        self.assertEqual(result.value, {"status": "saved"})
        self.action.assert_called_once_with()

    def test_missing_permit_denied(self):
        result = self.enforcer.execute(
            permit=None, request=self.req, action=self.action
        )
        self._assert_denied(result, "PERMIT_MISSING")

    def test_tampered_scope_rejected(self):
        tampered = replace(self.permit, resource_scope="vault.other")
        self._assert_denied(self._execute(tampered), "INVALID_SIGNATURE")

    def test_expired_permit_rejected(self):
        self.now = NOW + timedelta(seconds=61)
        self._assert_denied(self._execute(), "PERMIT_EXPIRED")

    def test_replayed_nonce_rejected(self):
        first = self._execute()
        self.assertEqual(first.status_code, 200)
        self.action.reset_mock()
        self._assert_denied(self._execute(), "NONCE_REPLAYED")

    def test_revoked_scope_rejected(self):
        self.revocations.revoke_scope("vault.journal.*")
        self._assert_denied(self._execute(), "SCOPE_REVOKED")

    def test_global_kill_switch_rejected(self):
        self.revocations.kill()
        self._assert_denied(self._execute(), "SCOPE_REVOKED")

    def test_distinct_signed_permits_cannot_reuse_nonce(self):
        first = self._execute()
        self.assertEqual(first.status_code, 200)
        self.action.reset_mock()
        second_permit = self._issue_permit()
        self.assertNotEqual(first.receipt["auth_status"], "DENY")
        self.assertNotEqual(second_permit.permit_id, self.permit.permit_id)
        self.assertEqual(second_permit.nonce, self.permit.nonce)
        self._assert_denied(self._execute(second_permit), "NONCE_REPLAYED")

    def test_stale_consent_epoch_rejected(self):
        self.state.consent_epoch = 5
        self._assert_denied(self._execute(), "STALE_AUTHORITY")

    def test_development_signer_cannot_authorize_e2(self):
        result = self.enforcer.execute(
            permit=self.permit,
            request=request(effect_class="E2"),
            action=self.action,
        )
        self._assert_denied(result, "UNSUPPORTED_EFFECT_CLASS")

    def test_revocation_after_preflight_but_before_action(self):
        store = self.nonce_store
        revocations = self.revocations

        class RevokeOnConsume:
            def consume(self, nonce, expires_at):
                burned = store.consume(nonce, expires_at)
                revocations.revoke_permit(self_permit_id)
                return burned

        self_permit_id = self.permit.permit_id
        self.enforcer.nonce_store = RevokeOnConsume()
        self._assert_denied(self._execute(), "SCOPE_REVOKED")

    def test_action_failure_has_no_automatic_retry(self):
        self.action.side_effect = RuntimeError("private data never disclosed")
        result = self._execute()
        self.assertEqual(result.status_code, 500)
        self.assertEqual(result.receipt["reason_code"], "EXECUTION_FAILED")
        self.assertNotIn("private data", str(result.receipt))
        self.action.reset_mock()
        self.action.return_value = ActionOutcome("ok", RESULT_DIGEST)
        self._assert_denied(self._execute(), "NONCE_REPLAYED")

    def test_receipts_do_not_include_raw_private_values(self):
        result = self._execute()
        self.assertEqual(
            set(result.receipt), {"rule_id", "auth_status", "reason_code"}
        )
        self.assertNotIn("local:example", str(result.receipt))
        self.assertNotIn(self.permit.subject_ref, str(result.receipt))


if __name__ == "__main__":
    unittest.main()
