"""UDS-AUTH-PREVIEW receiver conformance and adversarial tests.

These tests never authorize or invoke a real-world executor.
"""
from __future__ import annotations

import concurrent.futures
import copy
import json
import secrets
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for folder in (ROOT, ROOT / "Genesis"):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

from Genesis.auth.broker import (
    PermitError, PermitIssuer, ReceiverBroker, jcs_bytes, plan_digest,
)
from rtme_parser import compile_intent


class ReceiverBrokerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = str(Path(self.tmp.name) / "registry.sqlite")
        self.now = 2_000_000_000
        self.secret = secrets.token_bytes(32)
        self.issuer = PermitIssuer(issuer="trusted-service", key_id="k1", secret=self.secret)
        self.broker = ReceiverBroker(
            self.db, trusted_keys={("trusted-service", "k1"): self.secret},
            clock=lambda: self.now,
        )
        self.plan = compile_intent({
            "intent": "Build an opt-in neighborhood skill-sharing exchange.",
            "success_criterion": "Five people review the draft voluntarily.",
            "horizon_days": 30,
            "consent_to_draft": True,
        })
        self.grant("consent")
        self.grant("possession")

    def grant(self, kind, **options):
        self.broker.set_trusted_grant(
            kind, subject="alice", scope="local:draft:inspect",
            authority="draft:review", expires_at=self.now + 3600, **options,
        )

    def claims(self, **changed):
        return {
            **{
                "version": "1", "issuer": "trusted-service", "key_id": "k1",
                "plan_digest": plan_digest(self.plan), "step_id": "6:1",
                "subject_id": "alice", "resource_scope": "local:draft:inspect",
                "requested_authority": ["draft:review"], "effect_class": "E0",
                "nonce": secrets.token_hex(16), "issued_at": self.now - 1,
                "expires_at": self.now + 120,
            },
            **changed,
        }

    def authorize(self, permit, **changed):
        return self.broker.authorize_preview(**{
            "plan": self.plan, "permit": permit,
            "authenticated_subject": "alice", "step_id": "6:1",
            "resource_scope": "local:draft:inspect",
            **changed,
        })

    def test_success_is_only_an_inert_preview(self):
        result = self.authorize(self.issuer.sign(self.claims()))
        self.assertEqual(result.decision_class, "ALLOW_PREVIEW")
        self.assertTrue(result.permitted)
        self.assertFalse(result.receipt["executed"])
        self.assertEqual(result.receipt["plan_digest"], plan_digest(self.plan))

    def test_effects_e1_and_higher_fail_even_for_valid_signed_permits(self):
        signed = self.issuer.sign(self.claims())
        for effect in ("E1", "E2", "E9", "execute", None):
            with self.subTest(effect=effect):
                r = self.authorize(signed, requested_effect=effect)
                self.assertFalse(r.permitted)
                self.assertEqual(r.decision_class, "DENY_EXTERNAL_EFFECT_UNAVAILABLE")
        self.assertTrue(self.authorize(signed).permitted)

    def test_atomic_nonce_prevents_parallel_double_allow(self):
        signed = self.issuer.sign(self.claims())
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
            results = list(pool.map(lambda _: self.authorize(signed), range(14)))
        self.assertEqual(sum(r.permitted for r in results), 1)
        self.assertTrue(all(
            r.decision_class in ("ALLOW_PREVIEW", "DENY_REPLAY") for r in results
        ))

    def test_replay_persists_across_broker_restart(self):
        signed = self.issuer.sign(self.claims())
        self.assertTrue(self.authorize(signed).permitted)
        second = ReceiverBroker(
            self.db, trusted_keys={("trusted-service", "k1"): self.secret},
            clock=lambda: self.now,
        )
        result = second.authorize_preview(
            plan=self.plan, permit=signed, authenticated_subject="alice",
            step_id="6:1", resource_scope="local:draft:inspect",
        )
        self.assertEqual(result.decision_class, "DENY_REPLAY")

    def test_changed_criterion_invalidates_exact_plan_digest(self):
        signed = self.issuer.sign(self.claims())
        other = compile_intent({
            "intent": self.plan.intent,
            "success_criterion": "Ten people review the draft voluntarily.",
            "horizon_days": 30, "consent_to_draft": True,
        })
        self.assertNotEqual(plan_digest(self.plan), plan_digest(other))
        self.assertEqual(self.authorize(signed, plan=other).decision_class, "DENY_PERMIT")

    def test_changed_step_invalidates_exact_plan_digest(self):
        signed = self.issuer.sign(self.claims())
        nodes = (replace(self.plan.nodes[0], instruction="Altered"), *self.plan.nodes[1:])
        other = replace(self.plan, nodes=nodes)
        self.assertNotEqual(plan_digest(self.plan), plan_digest(other))
        self.assertEqual(self.authorize(signed, plan=other).decision_class, "DENY_PERMIT")

    def test_signed_scope_subject_and_step_are_exact(self):
        signed = self.issuer.sign(self.claims())
        for key, value in (
            ("authenticated_subject", "mallory"),
            ("resource_scope", "some:other:scope"),
            ("step_id", "6:2"),
        ):
            with self.subTest(key=key):
                self.assertEqual(self.authorize(signed, **{key: value}).decision_class,
                                 "DENY_PERMIT")
        self.assertTrue(self.authorize(signed).permitted)

    def test_signature_and_claim_tampering_fail_closed(self):
        signed = self.issuer.sign(self.claims())
        bad = copy.deepcopy(signed)
        bad["signature"] = "0" * 64
        self.assertEqual(self.authorize(bad).decision_class, "DENY_PERMIT")
        bad = copy.deepcopy(signed)
        bad["claims"]["expires_at"] += 1
        self.assertEqual(self.authorize(bad).decision_class, "DENY_PERMIT")

    def test_unknown_issuer_fails_closed(self):
        other = PermitIssuer(issuer="impostor", key_id="k1", secret=secrets.token_bytes(32))
        signed = other.sign(self.claims(issuer="impostor"))
        self.assertEqual(self.authorize(signed).decision_class, "DENY_PERMIT")

    def test_expired_and_future_permits_fail_closed(self):
        expired = self.issuer.sign(self.claims(
            issued_at=self.now - 201, expires_at=self.now - 1,
        ))
        future = self.issuer.sign(self.claims(
            issued_at=self.now + 1, expires_at=self.now + 100,
        ))
        self.assertEqual(self.authorize(expired).decision_class, "DENY_EXPIRED")
        self.assertEqual(self.authorize(future).decision_class, "DENY_EXPIRED")

    def test_revocation_is_checked_at_nonce_commit_time(self):
        signed = self.issuer.sign(self.claims())
        self.grant("consent", revoked=True)
        self.assertEqual(self.authorize(signed).decision_class, "DENY_SCOPE_OR_CONSENT")

    def test_expired_consent_and_revoked_possession_fail(self):
        signed = self.issuer.sign(self.claims())
        self.grant("consent", expires_at=self.now)
        self.assertEqual(self.authorize(signed).decision_class, "DENY_SCOPE_OR_CONSENT")
        self.grant("consent")
        self.grant("possession", revoked=True)
        self.assertEqual(self.authorize(signed).decision_class, "DENY_SCOPE_OR_CONSENT")

    def test_missing_scoped_grants_fail(self):
        signed = self.issuer.sign(self.claims(resource_scope="ungranted:scope"))
        self.assertEqual(
            self.authorize(signed, resource_scope="ungranted:scope").decision_class,
            "DENY_SCOPE_OR_CONSENT",
        )

    def test_extra_envelope_and_claim_fields_fail(self):
        signed = self.issuer.sign(self.claims())
        bad = copy.deepcopy(signed)
        bad["execute"] = True
        self.assertEqual(self.authorize(bad).decision_class, "DENY_PERMIT")
        bad = copy.deepcopy(signed)
        bad["claims"]["override"] = True
        self.assertEqual(self.authorize(bad).decision_class, "DENY_PERMIT")

    def test_invalid_nonce_effect_and_authorities_rejected_by_issuer(self):
        for change in (
            {"nonce": "bad"}, {"effect_class": "E1"},
            {"requested_authority": ["root"]},
            {"requested_authority": ["draft:review", "draft:review"]},
            {"plan_digest": "a" * 65},
            {"issued_at": "now"},
        ):
            with self.subTest(change=change), self.assertRaises(PermitError):
                self.issuer.sign(self.claims(**change))

    def test_receipts_are_metadata_only_and_unsigned(self):
        signed = self.issuer.sign(self.claims())
        receipts = [self.authorize(signed).receipt, self.authorize(signed).receipt]
        expected = {"plan_digest", "decision_class", "policy_version",
                    "timestamp_bucket", "zk_proof", "receipt_kind", "executed"}
        for receipt in receipts:
            self.assertEqual(set(receipt), expected)
            self.assertEqual(receipt["receipt_kind"], "UNSIGNED_LOCAL_DECISION_METADATA")
            self.assertIsNone(receipt["zk_proof"])
            self.assertFalse(receipt["executed"])
            raw = json.dumps(receipt)
            for secret in (self.plan.intent, self.plan.success_criterion, "alice",
                           signed["signature"], signed["claims"]["nonce"]):
                self.assertNotIn(secret, raw)

    def test_jcs_utf16_lexicographic_order(self):
        data = {"\ue000": 1, "😀": 2, "z": 3}
        self.assertEqual(jcs_bytes(data), '{"z":3,"😀":2,"\ue000":1}'.encode("utf-8"))
        self.assertEqual(jcs_bytes({"b": [True, None, "é"], "a": 7}),
                         '{"a":7,"b":[true,null,"é"]}'.encode("utf-8"))

    def test_jcs_preserves_unicode_without_normalizing(self):
        self.assertEqual(jcs_bytes({"b": 1, "a": 2}), jcs_bytes({"a": 2, "b": 1}))
        self.assertNotEqual(jcs_bytes("café"), jcs_bytes("cafe\u0301"))

    def test_jcs_rejects_unsupported_or_unsafe_values(self):
        for value in (1.25, float("nan"), 2 ** 53, "\ud800", {1: "bad"}):
            with self.subTest(value=repr(value)), self.assertRaises(PermitError):
                jcs_bytes(value)

    def test_jcs_escape_behavior_and_byte_limit(self):
        self.assertEqual(jcs_bytes("a\tb\nc"), b'"a\\tb\\nc"')
        with self.assertRaises(PermitError):
            jcs_bytes("x" * 65536)

    def test_invalid_plan_fails_without_digest(self):
        result = self.authorize(self.issuer.sign(self.claims()), plan={"forged": True})
        self.assertEqual(result.decision_class, "DENY_PLAN")
        self.assertIsNone(result.receipt["plan_digest"])

    def test_short_signer_key_rejected(self):
        with self.assertRaises(PermitError):
            PermitIssuer(issuer="example", key_id="k1", secret=b"password")


if __name__ == "__main__":
    unittest.main()
