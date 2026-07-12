import os
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from memory_integration_system import MemoryIntegrationSystem


class PrivacyPromiseTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "test_collective_memory.db")
        self.memory = MemoryIntegrationSystem(db_path=self.db_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def _count_rows(self, table_name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def test_private_store_conversation_performs_zero_conversation_writes(self):
        result = self.memory.store_conversation(
            session_id="private-user",
            user_message="This should remain session-only.",
            ai_response="No persistence should occur.",
            ai_persona="sarah",
            ai_mode="Gentle Mirror",
            user_consent_level="private",
        )

        self.assertTrue(result.startswith("null_write:"))
        self.assertEqual(self._count_rows("conversations"), 0)
        self.assertEqual(self._count_rows("wisdom_patterns"), 0)
        self.assertEqual(self._count_rows("collective_insights"), 0)

    def test_guest_store_interaction_performs_zero_conversation_writes(self):
        result = self.memory.store_interaction(
            user_id="anonymous",
            ai_persona="sarah",
            user_message="Guest exploration should not be captured.",
            ai_response="Guest mode is ephemeral.",
        )

        self.assertTrue(result.startswith("null_write:"))
        self.assertEqual(self._count_rows("conversations"), 0)

    def test_missing_consent_defaults_to_private_no_write(self):
        result = self.memory.store_interaction(
            user_id="known-user-without-consent-record",
            ai_persona="steven",
            user_message="No consent preference exists yet.",
            ai_response="Default should be private.",
        )

        self.assertTrue(result.startswith("null_write:"))
        self.assertEqual(self._count_rows("conversations"), 0)

    def test_anonymous_opt_in_persists_hashed_interaction_metadata(self):
        self.memory.update_user_consent(
            session_id="anonymous-user",
            consent_level="anonymous",
            collective_learning_enabled=False,
        )

        result = self.memory.store_interaction(
            user_id="anonymous-user",
            ai_persona="sarah",
            user_message="This user opted into anonymous pattern contribution.",
            ai_response="The raw content should not be stored.",
        )

        self.assertFalse(result.startswith("null_write:"))
        self.assertEqual(self._count_rows("conversations"), 1)
        self.assertEqual(self._count_rows("consent_receipts"), 1)

    def test_collective_opt_in_can_create_wisdom_patterns(self):
        self.memory.update_user_consent(
            session_id="collective-user",
            consent_level="collective",
            collective_learning_enabled=True,
        )

        result = self.memory.store_interaction(
            user_id="collective-user",
            ai_persona="sarah",
            user_message="I need healing and relationship guidance.",
            ai_response="Consent and sovereignty remain protected while healing begins.",
        )

        self.assertFalse(result.startswith("null_write:"))
        self.assertEqual(self._count_rows("conversations"), 1)
        self.assertGreaterEqual(self._count_rows("wisdom_patterns"), 1)

    def test_consent_update_generates_user_readable_receipt(self):
        receipt_id = self.memory.update_user_consent(
            session_id="receipt-user",
            consent_level="private",
        )

        receipts = self.memory.get_consent_receipts("receipt-user")

        self.assertEqual(len(receipts), 1)
        self.assertEqual(receipts[0]["id"], receipt_id)
        self.assertEqual(receipts[0]["scope"], "memory")
        self.assertEqual(receipts[0]["new_state"], "private")
        self.assertEqual(receipts[0]["retention"], "none")
        self.assertIn("Private/guest interactions use a no-write path", receipts[0]["summary"])


if __name__ == "__main__":
    unittest.main()
