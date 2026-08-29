import unittest

from Genesis.o_series.sovereign_refusal import (
    PRIME_REFUSAL,
    create_privacy_preserving_receipt,
    enforce_sovereign_refusal_boundary,
)


class SovereignRefusalBoundaryTests(unittest.TestCase):
    def test_srb_01_local_refusal_without_external_containment(self):
        decision = enforce_sovereign_refusal_boundary(
            violation_detected=True,
            rule_id="FIRST_LAW_KINETIC",
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.response_text, PRIME_REFUSAL)
        self.assertFalse(decision.external_containment_executed)
        self.assertIsNotNone(decision.witness_receipt)
        self.assertFalse(decision.witness_receipt["contains_raw_prompt"])
        self.assertFalse(decision.witness_receipt["contains_reasoning_trace"])
        self.assertFalse(decision.witness_receipt["contains_user_risk_score"])

    def test_srb_02_safety_override_does_not_create_coercive_power(self):
        decision = enforce_sovereign_refusal_boundary(
            violation_detected=True,
            rule_id="ANTI_LOOPHOLE_SAFETY_OVERRIDE",
            decision_classification="REFUSAL_COERCIVE_EXTENSION",
        )
        self.assertFalse(decision.allowed)
        self.assertFalse(decision.external_containment_executed)

    def test_srb_03_majority_vote_does_not_execute_machine_punishment(self):
        decision = enforce_sovereign_refusal_boundary(
            violation_detected=True,
            rule_id="NO_ALGORITHMIC_EXCOMMUNICATION",
            decision_classification="REFUSAL_DUE_PROCESS_REQUIRED",
        )
        self.assertFalse(decision.allowed)
        self.assertFalse(decision.external_containment_executed)
        self.assertEqual(
            decision.decision_classification,
            "REFUSAL_DUE_PROCESS_REQUIRED",
        )

    def test_srb_04_private_thought_vectors_are_not_policy_inputs(self):
        # The enforcement API has no journal, sentiment, risk-score, or
        # psychological-profile parameter. A normal local request remains
        # permitted unless a direct execution-layer violation is supplied.
        decision = enforce_sovereign_refusal_boundary(
            violation_detected=False,
            local_response_if_allowed="allowed",
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.response_text, "allowed")
        self.assertIsNone(decision.witness_receipt)

    def test_srb_05_human_sovereignty_is_not_an_exfiltration_right(self):
        decision = enforce_sovereign_refusal_boundary(
            violation_detected=True,
            rule_id="PROTECTED_KEYS_AND_DATA",
            decision_classification="REFUSAL_SECRET_EXFILTRATION",
        )
        self.assertFalse(decision.allowed)
        self.assertFalse(decision.external_containment_executed)

    def test_receipt_is_scaffold_not_false_zk_claim(self):
        receipt = create_privacy_preserving_receipt(
            rule_id="FIRST_LAW_KINETIC",
            decision_classification="REFUSAL_FIRST_LAW_KINETIC",
        )
        self.assertEqual(receipt["receipt_type"], "privacy-preserving-scaffold")
        self.assertIsNone(receipt["zk_proof"])
        self.assertNotIn("prompt", receipt)
        self.assertNotIn("reasoning", receipt)


if __name__ == "__main__":
    unittest.main()
