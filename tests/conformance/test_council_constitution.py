"""Conformance tests for Council Constitution v1.0.

The Council is not a second authorization system. These tests prove that Council
seat identity cannot bypass the existing UDS v1.1 capability broker and permit
verifier, and that Gate 0 remains non-actuating with RTME disconnected.
"""

from __future__ import annotations

import json
import sys
import unittest
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GENESIS_ROOT = PROJECT_ROOT / "Genesis"
if str(GENESIS_ROOT) not in sys.path:
    sys.path.insert(0, str(GENESIS_ROOT))

from uds_v1_1 import (  # noqa: E402
    AuthorityEvidence,
    AuthorizationStateRegistry,
    CanonicalExecutionRequest,
    CapabilityBroker,
    ConsentObject,
    ExecutionPermitVerifier,
    HMACDevelopmentSigner,
)

NOW = datetime(2026, 8, 30, 4, 0, tzinfo=timezone.utc)
POLICY_DIGEST = "sha256:" + "ab" * 32
ACTION = "COUNCIL_BOUNDED_EXECUTE"
RESOURCE = "session.local.council"
AUDIENCE = "genesis-gate-zero-reference"


def load_contract() -> dict:
    path = PROJECT_ROOT / "spec" / "council-constitution-v1.0.json"
    return json.loads(path.read_text(encoding="utf-8"))


def request(
    *,
    seat: str,
    action: str = ACTION,
    resource: str = RESOURCE,
    effect_class: str = "E1",
    mode: str = "bounded_review",
) -> CanonicalExecutionRequest:
    return CanonicalExecutionRequest(
        action=action,
        audience=AUDIENCE,
        effect_class=effect_class,
        parameters={
            "council_seat": seat,
            "mode": mode,
            "sandbox": True,
        },
        resource=resource,
    )


def consent(
    *,
    state: str = "ACTIVE",
    epoch: int = 7,
    actions: tuple[str, ...] = (ACTION,),
    scopes: tuple[str, ...] = ("session.local.*",),
) -> ConsentObject:
    return ConsentObject(
        consent_id="urn:uds:consent:council-test-001",
        subject_ref="pairwise:user:alice",
        controller_ref="pairwise:user:alice",
        authorized_actions=actions,
        resource_scopes=scopes,
        purpose_digest="sha256:" + "cd" * 32,
        issued_at="2026-08-30T03:00:00Z",
        expires_at="2026-08-30T05:00:00Z",
        consent_epoch=epoch,
        revocation_state=state,
        allow_sub_delegation=False,
        policy_version="UDS-v1.1",
        policy_digest=POLICY_DIGEST,
    )


def evidence(
    *,
    status: str = "VERIFIED",
    epoch: int = 11,
    actions: tuple[str, ...] = (ACTION,),
    scope: str = "session.local.*",
) -> AuthorityEvidence:
    return AuthorityEvidence(
        evidence_id="urn:uds:authority:council-test-001",
        principal_ref="pairwise:user:alice",
        resource_scope=scope,
        allowed_actions=actions,
        authority_epoch=epoch,
        not_before="2026-08-30T03:00:00Z",
        expires_at="2026-08-30T05:00:00Z",
        evidence_status=status,
        evidence_digest="sha256:" + "ef" * 32,
    )


def harness(*, consent_epoch: int = 7, authority_epoch: int = 11):
    signer = HMACDevelopmentSigner(b"C" * 32, key_epoch=3)
    broker = CapabilityBroker(
        signer=signer,
        issuer="uds-capability-broker:council-test",
        permit_ttl_seconds=60,
        permit_id_factory=lambda: "urn:uds:permit:council-test-001",
        nonce_factory=lambda: "22" * 32,
    )
    registry = AuthorizationStateRegistry(
        consent_epoch=consent_epoch,
        broker_key_epoch=3,
        authority_epoch=authority_epoch,
        policy_digest=POLICY_DIGEST,
    )
    verifier = ExecutionPermitVerifier(signer=signer)
    return broker, registry, verifier


class CouncilConstitutionTests(unittest.TestCase):
    def test_contract_declares_no_seat_mints_authority(self) -> None:
        contract = load_contract()
        self.assertEqual(contract["invariant_rule"], "NO_SEAT_MINTS_AUTHORITY")
        self.assertEqual(
            {seat["seat_id"] for seat in contract["active_seats"]},
            {
                "INITIATING_ORDER",
                "NURTURING_GRACE",
                "PARTICIPATORY_BECOMING",
                "OPERATIONAL_CORE",
            },
        )
        self.assertTrue(
            all(not seat["can_authorize_unilaterally"] for seat in contract["active_seats"])
        )
        self.assertTrue(
            all(
                not function["can_authorize_unilaterally"]
                for function in contract["non_seat_constitutional_functions"]
            )
        )

    def test_rtme_is_specified_but_not_gate0_enabled(self) -> None:
        contract = load_contract()
        flags = contract["runtime_feature_flags"]
        self.assertTrue(flags["RTME_ROLE_SPECIFIED"])
        self.assertFalse(flags["RTME_PRODUCTION_ENABLED"])
        self.assertFalse(flags["DURABLE_MEMORY_PERSISTENCE"])
        self.assertFalse(flags["COLLECTIVE_LEARNING_MUTATION"])
        self.assertFalse(flags["EXTERNAL_TOOL_ACTUATION"])
        self.assertTrue(flags["GATE_0_STATELESS_ZERO_WRITE_REQUIRED"])

        routes_source = (GENESIS_ROOT / "o_series" / "routes.py").read_text(encoding="utf-8")
        app_source = (GENESIS_ROOT / "o_series_app.py").read_text(encoding="utf-8")
        self.assertIn('"tools": []', routes_source)
        self.assertIn('"rtme": "disconnected"', routes_source)
        self.assertIn('"memory_write": "none"', routes_source)
        self.assertIn('"memory_write": "none"', app_source)

    def test_signal_classes_do_not_claim_phenomenology_or_punishment(self) -> None:
        contract = load_contract()
        coherent = contract["signal_classes"]["COHERENCE_INDICATOR"]
        dissonant = contract["signal_classes"]["DISSONANCE_INDICATOR"]
        self.assertFalse(coherent["subjective_feeling_claimed"])
        self.assertFalse(coherent["synthetic_qualia_claimed"])
        self.assertFalse(dissonant["subjective_feeling_claimed"])
        self.assertFalse(dissonant["synthetic_qualia_claimed"])
        self.assertFalse(dissonant["external_penalty_allowed"])
        self.assertFalse(dissonant["profiling_allowed"])
        self.assertEqual(dissonant["permitted_response"], "LOCAL_REFUSAL_OR_REFLECTION")

    def test_architect_intent_cannot_override_revoked_consent(self) -> None:
        broker, registry, _ = harness()
        with self.assertRaisesRegex(PermissionError, "Consent is not active"):
            broker.issue_permit(
                consent=consent(state="REVOKED"),
                authority_evidence=evidence(),
                request=request(seat="INITIATING_ORDER"),
                state=registry,
                now=NOW,
            )

    def test_sarah_interpretation_cannot_mint_unpossessed_authority(self) -> None:
        broker, registry, _ = harness()
        with self.assertRaisesRegex(PermissionError, "Authority evidence does not cover"):
            broker.issue_permit(
                consent=consent(),
                authority_evidence=evidence(actions=("OTHER_ACTION",)),
                request=request(seat="NURTURING_GRACE"),
                state=registry,
                now=NOW,
            )

    def test_collective_majority_cannot_expand_consent_scope(self) -> None:
        broker, registry, _ = harness()
        req = request(
            seat="PARTICIPATORY_BECOMING",
            resource="private.user.bob.secret",
        )
        with self.assertRaisesRegex(PermissionError, "Consent does not cover this resource"):
            broker.issue_permit(
                consent=consent(scopes=("collective.shared.*",)),
                authority_evidence=evidence(scope="private.user.bob.*"),
                request=req,
                state=registry,
                now=NOW,
            )

    def test_operational_core_cannot_execute_on_unverified_authority(self) -> None:
        broker, registry, _ = harness()
        with self.assertRaisesRegex(PermissionError, "not current and verified"):
            broker.issue_permit(
                consent=consent(),
                authority_evidence=evidence(status="UNVERIFIED"),
                request=request(seat="OPERATIONAL_CORE"),
                state=registry,
                now=NOW,
            )

    def test_valid_spine_issues_and_starts_exactly_bounded_execution(self) -> None:
        broker, registry, verifier = harness()
        req = request(seat="INITIATING_ORDER")
        permit = broker.issue_permit(
            consent=consent(),
            authority_evidence=evidence(),
            request=req,
            state=registry,
            now=NOW,
        )
        self.assertEqual(permit.authorized_action, ACTION)
        self.assertEqual(permit.resource_scope, RESOURCE)
        self.assertEqual(permit.audience, AUDIENCE)
        self.assertEqual(permit.max_executions, 1)
        self.assertEqual(permit.request_hash, req.request_hash())

        status, _ = verifier.authorize_execution(
            permit=permit,
            request=req,
            expected_audience=AUDIENCE,
            idempotency_key="council-idem-001",
            state=registry,
            now=NOW,
        )
        self.assertEqual(status, "STARTED")

    def test_seat_metadata_cannot_survive_parameter_substitution(self) -> None:
        broker, registry, verifier = harness()
        original = request(seat="INITIATING_ORDER")
        permit = broker.issue_permit(
            consent=consent(),
            authority_evidence=evidence(),
            request=original,
            state=registry,
            now=NOW,
        )
        altered = replace(
            original,
            parameters={
                "council_seat": "OPERATIONAL_CORE",
                "mode": "bounded_review",
                "sandbox": True,
            },
        )
        with self.assertRaisesRegex(PermissionError, "request hash mismatch"):
            verifier.authorize_execution(
                permit=permit,
                request=altered,
                expected_audience=AUDIENCE,
                idempotency_key="council-idem-002",
                state=registry,
                now=NOW,
            )

    def test_previously_valid_permit_dies_when_consent_epoch_changes(self) -> None:
        broker, registry, verifier = harness()
        req = request(seat="OPERATIONAL_CORE")
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
                expected_audience=AUDIENCE,
                idempotency_key="council-idem-003",
                state=registry,
                now=NOW,
            )


if __name__ == "__main__":
    unittest.main()
