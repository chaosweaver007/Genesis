"""Live integrity tests for the Genesis privacy and consent boundary.

These tests implement the minimum promises named in
``docs/privacy/Genesis-Privacy-Trinity-Binding.md``. Each test uses a temporary
SQLite database so the suite never reads from or writes to production memory.
"""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
APPLICATION_ROOT = REPOSITORY_ROOT / "Genesis"
sys.path.insert(0, str(APPLICATION_ROOT))

from memory_integration_system import MemoryIntegrationSystem  # noqa: E402


class PrivacyIntegrityTests(unittest.TestCase):
    """Verify that privacy promises are executable, not merely descriptive."""

    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.db_path = Path(self._temporary_directory.name) / "integrity.db"
        self.memory = MemoryIntegrationSystem(db_path=str(self.db_path))

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def _conversation_rows(self) -> list[tuple]:
        with sqlite3.connect(self.db_path) as connection:
            return connection.execute(
                """
                SELECT session_id, user_message_hash, ai_response_hash,
                       user_consent_level, anonymized_hash, extracted_patterns,
                       wisdom_contribution
                FROM conversations
                ORDER BY created_at ASC
                """
            ).fetchall()

    def test_private_mode_creates_zero_conversation_metadata_writes(self) -> None:
        self.memory.update_user_consent(
            session_id="private-user",
            consent_level="private",
        )

        result = self.memory.store_interaction(
            user_id="private-user",
            ai_persona="steven",
            user_message="This must remain private.",
            ai_response="Boundary honored.",
        )

        self.assertTrue(result.startswith("null_write:"))
        self.assertEqual([], self._conversation_rows())

    def test_guest_and_no_consent_modes_create_zero_metadata_writes(self) -> None:
        cases = (
            (None, "guest"),
            ("guest-user", "guest"),
            ("none-user", "none"),
            ("no-consent-user", "no_consent"),
            ("blank-user", ""),
        )

        for session_id, consent_level in cases:
            with self.subTest(consent_level=consent_level):
                result = self.memory.store_conversation(
                    session_id=session_id,
                    user_message="Do not retain me.",
                    ai_response="Nothing retained.",
                    ai_persona="steven",
                    ai_mode="Chaos Weaver",
                    user_consent_level=consent_level,
                )
                self.assertTrue(result.startswith("null_write:"))

        self.assertEqual([], self._conversation_rows())

    def test_anonymous_mode_persists_only_after_explicit_opt_in(self) -> None:
        before_opt_in = self.memory.store_interaction(
            user_id="anonymous-user",
            ai_persona="steven",
            user_message="Before consent.",
            ai_response="No persistence.",
        )
        self.assertTrue(before_opt_in.startswith("null_write:"))
        self.assertEqual([], self._conversation_rows())

        self.memory.update_user_consent(
            session_id="anonymous-user",
            consent_level="anonymous",
        )
        after_opt_in = self.memory.store_interaction(
            user_id="anonymous-user",
            ai_persona="steven",
            user_message="After explicit anonymous opt-in.",
            ai_response="Persist only anonymized metadata.",
        )

        rows = self._conversation_rows()
        self.assertFalse(after_opt_in.startswith("null_write:"))
        self.assertEqual(1, len(rows))
        self.assertEqual("anonymous", rows[0][3])
        self.assertIsNotNone(rows[0][4])
        self.assertIsNone(rows[0][5])
        self.assertIsNone(rows[0][6])

    def test_collective_mode_persists_only_after_explicit_opt_in(self) -> None:
        before_opt_in = self.memory.store_interaction(
            user_id="collective-user",
            ai_persona="collective",
            user_message="Before collective consent.",
            ai_response="No collective learning.",
        )
        self.assertTrue(before_opt_in.startswith("null_write:"))
        self.assertEqual([], self._conversation_rows())

        self.memory.update_user_consent(
            session_id="collective-user",
            consent_level="collective",
            collective_learning_enabled=True,
        )
        after_opt_in = self.memory.store_interaction(
            user_id="collective-user",
            ai_persona="collective",
            user_message="I explicitly contribute this healing insight.",
            ai_response="The contribution is processed under collective consent.",
        )

        rows = self._conversation_rows()
        self.assertFalse(after_opt_in.startswith("null_write:"))
        self.assertEqual(1, len(rows))
        self.assertEqual("collective", rows[0][3])
        self.assertIsNotNone(rows[0][4])
        self.assertIsNotNone(rows[0][5])
        self.assertIsNotNone(rows[0][6])

    def test_consent_updates_generate_human_readable_receipts(self) -> None:
        receipt_id = self.memory.update_user_consent(
            session_id="receipt-user",
            consent_level="anonymous",
            data_retention_days=14,
        )

        receipts = self.memory.get_consent_receipts("receipt-user")
        self.assertEqual(1, len(receipts))
        receipt = receipts[0]

        self.assertEqual(receipt_id, receipt["id"])
        self.assertEqual("memory", receipt["scope"])
        self.assertEqual("granted", receipt["action"])
        self.assertEqual("anonymous", receipt["new_state"])
        self.assertEqual([], receipt["shared_with"])
        self.assertEqual("14 days", receipt["retention"])
        self.assertIn("Consent level set to anonymous", receipt["summary"])
        self.assertTrue(receipt["revoke_path"])
        self.assertTrue(receipt["export_path"])

    def test_receipt_exports_are_user_readable_json(self) -> None:
        self.memory.update_user_consent(
            session_id="export-user",
            consent_level="private",
        )

        export = self.memory.export_consent_receipts("export-user")
        encoded = json.dumps(export)

        self.assertIn('"user_id": "export-user"', encoded)
        self.assertIn("exported_at", export)
        self.assertEqual(1, len(export["receipts"]))
        receipt = export["receipts"][0]
        self.assertEqual("private", receipt["new_state"])
        self.assertIn("summary", receipt)
        self.assertIn("retention", receipt)
        self.assertIn("revoke_path", receipt)
        self.assertIn("export_path", receipt)


if __name__ == "__main__":
    unittest.main()
