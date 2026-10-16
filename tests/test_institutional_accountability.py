"""Conformance tests for the Synthsara institutional-accountability reference kernel."""

from __future__ import annotations

import hashlib
import json
import unittest

from Genesis.institutional_accountability import (
    AccountabilityError,
    AccountabilityKernel,
    Principal,
)


def fingerprint(content: bytes = b"nonidentifying-test-evidence") -> str:
    return hashlib.sha256(content).hexdigest()


def actor(name: str, *roles: str) -> Principal:
    return Principal(name, frozenset(roles), authenticated=True)


class InstitutionalAccountabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.kernel = AccountabilityKernel(commitment_key=b"x" * 32)
        self.claimant = actor("ordinary-person", "participant")
        self.respondent = "community-institution"
        self.first = actor("first-reviewer", "reviewer")
        self.appeals = actor("appeal-reviewer", "reviewer")
        self.auditor = actor("independent-auditor", "auditor")

    def begin(self) -> str:
        case_id, _ = self.kernel.open_case(
            self.claimant, self.respondent, "access", fingerprint()
        )
        return case_id

    def adjudicate(self, decision: str = "RESTORE") -> str:
        case_id = self.begin()
        self.kernel.assign_reviewer(case_id, self.first)
        self.kernel.decide(case_id, self.first, decision)
        return case_id

    def test_ordinary_person_can_enter_without_money_or_worth(self):
        case_id = self.begin()
        self.assertEqual(self.kernel.receipts(case_id)[0]["state"], "OPEN")
        self.assertTrue(self.kernel.verify_chain(case_id))
        # No WORTH, financial threshold, token, social credit, or fee exists
        # in the open_case API or the public receipt.
        self.assertNotIn("worth", json.dumps(self.kernel.receipts(case_id)).lower())
        self.assertNotIn("fee", json.dumps(self.kernel.receipts(case_id)).lower())

    def test_anonymous_actor_cannot_create_case(self):
        with self.assertRaises(AccountabilityError):
            self.kernel.open_case(
                Principal("anonymous", frozenset({"participant"}), False),
                self.respondent, "access", fingerprint(),
            )

    def test_evidence_must_be_digest_not_raw_narrative(self):
        with self.assertRaises(AccountabilityError):
            self.kernel.open_case(
                self.claimant, self.respondent, "access", "my private story"
            )

    def test_unrecognized_category_fails_closed(self):
        with self.assertRaises(AccountabilityError):
            self.kernel.open_case(
                self.claimant, self.respondent, "worthiness", fingerprint()
            )

    def test_subject_institution_cannot_review_its_own_complaint(self):
        case_id = self.begin()
        with self.assertRaises(AccountabilityError):
            self.kernel.assign_reviewer(
                case_id, actor(self.respondent, "reviewer"),
            )

    def test_claimant_cannot_self_adjudicate(self):
        case_id = self.begin()
        with self.assertRaises(AccountabilityError):
            self.kernel.assign_reviewer(
                case_id, actor(self.claimant.subject_id, "reviewer")
            )

    def test_unassigned_reviewer_cannot_decide(self):
        case_id = self.begin()
        self.kernel.assign_reviewer(case_id, self.first)
        with self.assertRaises(AccountabilityError):
            self.kernel.decide(case_id, self.appeals, "DISMISS")

    def test_appeal_reviewer_must_differ_from_initial(self):
        case_id = self.adjudicate("DISMISS")
        self.kernel.appeal(case_id, self.claimant, fingerprint(b"appeal"))
        with self.assertRaises(AccountabilityError):
            self.kernel.resolve_appeal(case_id, self.first, "RESTORE")

    def test_appeal_corrects_decision_without_erasing_history(self):
        case_id = self.adjudicate("DISMISS")
        self.kernel.appeal(case_id, self.claimant, fingerprint(b"appeal"))
        self.kernel.resolve_appeal(case_id, self.appeals, "CORRECT")
        receipts = self.kernel.receipts(case_id)
        self.assertEqual(receipts[2]["details"]["decision"], "DISMISS")
        self.assertEqual(receipts[-1]["details"]["decision"], "CORRECT")
        self.assertTrue(self.kernel.verify_chain(case_id))

    def test_no_duplicate_appeals(self):
        case_id = self.adjudicate("DISMISS")
        self.kernel.appeal(case_id, self.claimant, fingerprint(b"appeal"))
        self.kernel.resolve_appeal(case_id, self.appeals, "CORRECT")
        with self.assertRaises(AccountabilityError):
            self.kernel.appeal(case_id, self.claimant, fingerprint(b"repeat"))

    def test_remedy_not_marked_done_without_independent_attestation(self):
        case_id = self.adjudicate("RESTORE")
        with self.assertRaises(AccountabilityError):
            self.kernel.close(case_id, self.auditor)
        with self.assertRaises(AccountabilityError):
            self.kernel.verify_remedy(
                case_id, actor(self.first.subject_id, "auditor"), fingerprint()
            )
        self.kernel.verify_remedy(case_id, self.auditor, fingerprint(b"completed"))
        with self.assertRaises(AccountabilityError):
            self.kernel.close(case_id, self.auditor)
        self.kernel.accept_resolution(case_id, self.claimant)
        self.kernel.close(case_id, self.auditor)
        self.assertEqual(self.kernel.receipts(case_id)[-1]["state"], "CLOSED")

    def test_appeal_remains_available_after_remedy_attestation(self):
        case_id = self.adjudicate("RESTORE")
        self.kernel.verify_remedy(case_id, self.auditor, fingerprint(b"insufficient"))
        self.kernel.appeal(case_id, self.claimant, fingerprint(b"not-satisfied"))
        self.kernel.resolve_appeal(case_id, self.appeals, "CORRECT")
        self.assertEqual(self.kernel.receipts(case_id)[-1]["details"]["decision"], "CORRECT")

    def test_only_claimant_can_accept_verified_remedy(self):
        case_id = self.adjudicate("RESTORE")
        self.kernel.verify_remedy(case_id, self.auditor, fingerprint(b"done"))
        with self.assertRaises(AccountabilityError):
            self.kernel.accept_resolution(case_id, actor(self.respondent, "participant"))
        self.kernel.accept_resolution(case_id, self.claimant)
        self.assertEqual(self.kernel.receipts(case_id)[-1]["state"], "ACCEPTED")

    def test_initial_dismissal_cannot_silently_close_appeal_right(self):
        case_id = self.adjudicate("DISMISS")
        with self.assertRaises(AccountabilityError):
            self.kernel.close(case_id, self.auditor)

    def test_evidence_commitments_hide_submitted_digests(self):
        case_id = self.begin()
        published = json.dumps(self.kernel.receipts(case_id))
        self.assertNotIn(fingerprint(), published)
        self.assertNotIn(self.claimant.subject_id, published)
        self.assertNotIn(self.respondent, published)

    def test_receipt_copy_cannot_mutate_original(self):
        case_id = self.begin()
        external = self.kernel.receipts(case_id)
        external[0]["details"]["category"] = "tampered"
        external[0]["sha256"] = "0" * 64
        self.assertEqual(self.kernel.receipts(case_id)[0]["details"]["category"], "access")
        self.assertTrue(self.kernel.verify_chain(case_id))

    def test_hash_chain_detects_tampering_and_external_head_mismatch(self):
        case_id = self.adjudicate()
        head = self.kernel.receipts(case_id)[-1]["sha256"]
        self.assertTrue(self.kernel.verify_chain(case_id, expected_head=head))
        self.assertFalse(self.kernel.verify_chain(case_id, expected_head="0" * 64))
        self.kernel._events[case_id][1]["action"] = "FORGED"  # controlled test corruption
        self.assertFalse(self.kernel.verify_chain(case_id, expected_head=head))

    def test_public_receipts_cannot_trigger_external_actions(self):
        case_id = self.adjudicate("RESTITUTION")
        receipt = self.kernel.receipts(case_id)[-1]
        self.assertEqual(receipt["action"], "DECISION_RECORDED")
        self.assertNotIn("funds_transferred", receipt)
        self.assertNotIn("access_changed", receipt)


if __name__ == "__main__":
    unittest.main()
