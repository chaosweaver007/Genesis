"""C6 reference tests for the first UDS v1.1 hardened authority slice."""

from __future__ import annotations

import sys
import unittest
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENESIS_ROOT = PROJECT_ROOT / "Genesis"
if str(GENESIS_ROOT) not in sys.path:
    sys.path.insert(0, str(GENESIS_ROOT))

from uds_v1_1 import (
    AuthorityEvidence,
    AuthorizationStateRegistry,
    CanonicalExecutionRequest,
    CapabilityBroker,
    ConsentObject,
    EvidenceLevel,
    ExecutionPermitVerifier,
    HMACDevelopmentSigner,
    OutcomeEvidence,
    OutcomeRecord,
)

NOW = datetime(2026, 8, 18, 9, 30, tzinfo=timezone.utc)
POLICY_DIGEST = "sha256:" + "ab" * 32


def request(*, resource: str = "session.local.manifestation", effect_class: str = "E1"):
    return CanonicalExecutionRequest(
        action="RTME_MANIFESTATION_EXECUTE",
        audience="rtme-node-cartersville-01",
        effect_class=effect_class,
        parameters={
            "mode": "shadow_work_mirror",
            "resolution": "1080p",
            "sandbox": True,
        },
        resource=resource,
    )


def consent(*, epoch: int = 7, state: str = "ACTIVE", scope: str = "session.local.*"):
    return ConsentObject(
        consent_id="urn:uds:consent:test-001",
        subject_ref="pairwise:user:alice",
        controller_ref="pairwise:user:alice",
        authorized_actions=("RTME_MANIFESTATION_EXECUTE",),
        resource_scopes=(scope,),
        purpose_digest="sha256:" + "cd" * 32,
        issued_at="2026-08-18T09:00:00Z",
        expires_at="2026-08-18T10:00:00Z",
        consent_epoch=epoch,
        revocation_state=state,
        allow_sub_delegation=False,
        policy_version="UDS-v1.1",
        policy_digest=POLICY_DIGEST,
    )


def evidence(*, epoch: int = 11, scope: str = "session.local.*"):
    return AuthorityEvidence(
        evidence_id="urn:uds:authority:test-001",
        principal_ref="pairwise:user:alice",
        resource_scope=scope,
        allowed_actions=("RTME_MANIFESTATION_EXECUTE",),
        authority_epoch=epoch,
        not_before="2026-08-18T09:00:00Z",
        expires_at="2026-08-18T10:00:00Z",
        evidence_status="VERIFIED",
        evidence_digest="sha256:" + "ef" * 32,
    )


def harness(*, consent_epoch: int = 7, authority_epoch: int = 11):
    signer = HMACDevelopmentSigner(b"S" * 32, key_epoch=3)
    broker = CapabilityBroker(
        signer=signer,
        issuer="uds-capability-broker:test",
        permit_ttl_seconds=60,
        permit_id_factory=lambda: "urn:uds:permit:test-001",
        nonce_factory=lambda: "11" * 32,
    )
    registry = AuthorizationStateRegistry(
        consent_epoch=consent_epoch,
        broker_key_epoch=3,
        authority_epoch=authority_epoch,
        policy_digest=POLICY_DIGEST,
    )
    verifier = ExecutionPermitVerifier(signer=signer)
    return signer, broker, registry, verifier


class UDSV11AuthorityTests(unittest.TestCase):
    def test_auth004_golden_jcs_vector(self) -> None:
        self.assertEqual(
            request().request_hash(),
            "49ef05e0e46ab37207df0381b637ac5fe265dc82ea006f8513759d9898632f1b",
        )

    def test_auth002_consent_cannot_grant_unpossessed_scope(self) -> None:
        _, broker, registry, _ = harness()
        with self.assertRaisesRegex(PermissionError, "Authority evidence does not cover"):
            broker.issue_permit(
                consent=consent(),
                authority_evidence=evidence(scope="session.other.*"),
                request=request(),
                state=registry,
                now=NOW,
            )

    def test_revoked_consent_fails_before_permit_issuance(self) -> None:
        _, broker, registry, _ = harness()
        with self.assertRaisesRegex(PermissionError, "Consent is not active"):
            broker.issue_permit(
                consent=consent(state="REVOKED"),
                authority_evidence=evidence(),
                request=request(),
                state=registry,
                now=NOW,
            )

    def test_auth003_e3_fails_closed_without_threshold_signer(self) -> None:
        _, broker, registry, _ = harness()
        with self.assertRaisesRegex(PermissionError, "No approved signer profile"):
            broker.issue_permit(
                consent=consent(),
                authority_evidence=evidence(),
                request=request(effect_class="E3"),
                state=registry,
                now=NOW,
            )

    def test_auth004_parameter_substitution_breaks_exact_binding(self) -> None:
        _, broker, registry, verifier = harness()
        original = request()
        permit = broker.issue_permit(
            consent=consent(),
            authority_evidence=evidence(),
            request=original,
            state=registry,
            now=NOW,
        )
        altered = CanonicalExecutionRequest(
            action=original.action,
            audience=original.audience,
            effect_class=original.effect_class,
            parameters={"mode": "shadow_work_mirror", "resolution": "4k", "sandbox": True},
            resource=original.resource,
        )
        with self.assertRaisesRegex(PermissionError, "request hash mismatch"):
            verifier.authorize_execution(
                permit=permit,
                request=altered,
                expected_audience=original.audience,
                idempotency_key="idem-001",
                state=registry,
                now=NOW,
            )

    def test_auth005_stale_consent_epoch_rejected_at_commit_boundary(self) -> None:
        _, broker, registry, verifier = harness()
        req = request()
        permit = broker.issue_permit(
            consent=consent(),
            authority_evidence=evidence(),
            request=req,
            state=registry,
            now=NOW,
        )
        registry.consent_epoch = 8
        with self.assertRaisesRegex(PermissionError, "Stale consent epoch"):
            verifier.authorize_execution(
                permit=permit,
                request=req,
                expected_audience=req.audience,
                idempotency_key="idem-001",
                state=registry,
                now=NOW,
            )

    def test_permit_signature_tampering_is_rejected(self) -> None:
        _, broker, registry, verifier = harness()
        req = request()
        permit = broker.issue_permit(
            consent=consent(),
            authority_evidence=evidence(),
            request=req,
            state=registry,
            now=NOW,
        )
        tampered = replace(permit, purpose_digest="sha256:" + "00" * 32)
        with self.assertRaisesRegex(PermissionError, "signature verification failed"):
            verifier.authorize_execution(
                permit=tampered,
                request=req,
                expected_audience=req.audience,
                idempotency_key="idem-001",
                state=registry,
                now=NOW,
            )

    def test_single_transition_allows_safe_same_key_replay_only(self) -> None:
        _, broker, registry, verifier = harness()
        req = request()
        permit = broker.issue_permit(
            consent=consent(),
            authority_evidence=evidence(),
            request=req,
            state=registry,
            now=NOW,
        )
        status, _ = verifier.authorize_execution(
            permit=permit,
            request=req,
            expected_audience=req.audience,
            idempotency_key="idem-001",
            state=registry,
            now=NOW,
        )
        self.assertEqual(status, "STARTED")
        committed = registry.commit(permit_id=permit.permit_id, result_digest="sha256:" + "12" * 32)
        self.assertEqual(committed.status, "COMMITTED")

        replay_status, replay_entry = verifier.authorize_execution(
            permit=permit,
            request=req,
            expected_audience=req.audience,
            idempotency_key="idem-001",
            state=registry,
            now=NOW,
        )
        self.assertEqual(replay_status, "ALREADY_COMMITTED")
        self.assertEqual(replay_entry.result_digest, committed.result_digest)

        with self.assertRaisesRegex(PermissionError, "Permit replay conflicts"):
            verifier.authorize_execution(
                permit=permit,
                request=req,
                expected_audience=req.audience,
                idempotency_key="different-retry-key",
                state=registry,
                now=NOW,
            )

    def test_auth006_cannot_promote_committed_evidence_to_verified(self) -> None:
        evidence_bundle = OutcomeEvidence(commitment_digest="sha256:" + "34" * 32)
        with self.assertRaisesRegex(ValueError, "Evidence promotion prohibited"):
            OutcomeRecord.create(
                permit_id="urn:uds:permit:test-001",
                request_hash=request().request_hash(),
                result_digest="sha256:" + "56" * 32,
                claimed_level=EvidenceLevel.VERIFIED,
                evidence=evidence_bundle,
            )

    def test_auth006_verified_requires_independent_verification_artifact(self) -> None:
        evidence_bundle = OutcomeEvidence(
            commitment_digest="sha256:" + "34" * 32,
            observed_state_digest="sha256:" + "56" * 32,
            independent_verification_digest="sha256:" + "78" * 32,
        )
        record = OutcomeRecord.create(
            permit_id="urn:uds:permit:test-001",
            request_hash=request().request_hash(),
            result_digest="sha256:" + "90" * 32,
            claimed_level=EvidenceLevel.VERIFIED,
            evidence=evidence_bundle,
        )
        self.assertEqual(record.evidence_level, EvidenceLevel.VERIFIED)


if __name__ == "__main__":
    unittest.main()
