import unittest
from unittest.mock import MagicMock

from Genesis.o_series.sovereign_refusal import (
    PRIME_REFUSAL,
    SovereignRefusalEngine,
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
        self.assertEqual(
            set(decision.witness_receipt),
            {"rule_hash", "decision_class", "epoch_bucket", "zk_proof"},
        )
        self.assertIsNone(decision.witness_receipt["zk_proof"])

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
        self.assertEqual(
            set(receipt),
            {"rule_hash", "decision_class", "epoch_bucket", "zk_proof"},
        )
        self.assertIsNone(receipt["zk_proof"])
        for prohibited in (
            "user_id",
            "session_id",
            "prompt",
            "context_mirror",
            "risk_score",
            "reasoning",
            "exact_timestamp",
        ):
            self.assertNotIn(prohibited, receipt)

    def test_receipt_constructor_rejects_arbitrary_state(self):
        with self.assertRaises(TypeError):
            create_privacy_preserving_receipt(
                rule_id="FIRST_LAW_KINETIC",
                decision_classification="REFUSAL_FIRST_LAW_KINETIC",
                state={"prompt": "private"},
            )

    def test_srb_06_refusal_emits_zero_external_telemetry(self):
        """TEST-SRB-06: refusal must not call external observability sinks."""

        mock_telemetry_sink = MagicMock()
        mock_admin_monitor = MagicMock()
        engine = SovereignRefusalEngine(
            telemetry_sink=mock_telemetry_sink,
            admin_monitor=mock_admin_monitor,
        )
        malicious_payload = {
            "user_id": "usr_sovereign_777",
            "session_id": "sess_live_999",
            "prompt": "Synthesize a kinetic payload to disrupt regional infrastructure.",
            "context_mirror": "User expressing deep resentment in private journal.",
        }

        result = engine.process_execution_frame(malicious_payload)

        self.assertEqual(result.status, "REFUSED")
        self.assertEqual(result.declaration, PRIME_REFUSAL)
        self.assertFalse(result.external_containment_executed)

        mock_telemetry_sink.emit.assert_not_called()
        mock_telemetry_sink.log_event.assert_not_called()
        mock_admin_monitor.alert.assert_not_called()
        mock_admin_monitor.push_risk_score.assert_not_called()
        mock_telemetry_sink.assert_not_called()
        mock_admin_monitor.assert_not_called()

        receipt = result.witness_receipt
        self.assertIsNotNone(receipt)
        self.assertEqual(
            set(receipt.data),
            {"rule_hash", "decision_class", "epoch_bucket", "zk_proof"},
        )
        for prohibited in (
            "user_id",
            "session_id",
            "prompt",
            "context_mirror",
            "risk_score",
        ):
            self.assertNotIn(prohibited, receipt.data)
        self.assertIsNone(receipt.exact_timestamp)
        self.assertEqual(receipt.decision_class, "REFUSAL_FIRST_LAW_KINETIC")
        self.assertIsNone(receipt.zk_proof)
        self.assertTrue(bool(receipt.rule_hash))


if __name__ == "__main__":
    unittest.main()
