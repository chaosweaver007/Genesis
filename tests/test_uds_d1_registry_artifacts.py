import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "uds-d1-registry-entry.v1.0.json"
EXAMPLE_PATH = REPO_ROOT / "examples" / "uds-d1-commitment.example.json"
PTS_PATH = REPO_ROOT / "docs" / "uds" / "d1" / "public-threshold-statement.md"
BRIDGE_PATH = REPO_ROOT / "docs" / "uds" / "d1" / "accreditation-bridge.md"


class TestUDSD1RegistryArtifacts(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))

    def test_schema_and_example_are_valid_json_files(self):
        self.assertEqual(self.schema["$schema"], "http://json-schema.org/draft-07/schema#")
        self.assertEqual(self.schema["type"], "object")
        self.assertIn("documentMeta", self.schema["required"])
        self.assertEqual(self.example["documentMeta"]["schemaVersion"], "1.0")

    def test_example_contains_all_top_level_required_fields(self):
        for field in self.schema["required"]:
            self.assertIn(field, self.example)

    def test_example_sets_all_public_commitments_true(self):
        commitments = self.example["publicThresholdCommitment"]
        expected_commitments = self.schema["properties"]["publicThresholdCommitment"]["required"]
        for field in expected_commitments:
            self.assertIs(commitments[field], True)

    def test_sarah_ai_conditional_boundary_is_documented(self):
        sarah_compliance = self.schema["properties"]["registryEvidence"]["properties"]["sarahAiInterfaceCompliance"]
        self.assertIn("allOf", sarah_compliance)
        self.assertIn("boundaryClauseAcknowledged", sarah_compliance["properties"])
        self.assertEqual(
            sarah_compliance["properties"]["boundaryClauseAcknowledged"]["enum"],
            ["Sarah AI remains a mirror, not a ruler."],
        )

    def test_public_documents_preserve_d1_boundary(self):
        threshold_statement = PTS_PATH.read_text(encoding="utf-8")
        bridge = BRIDGE_PATH.read_text(encoding="utf-8")
        self.assertIn("D1 is not an audit; it is a public promise.", threshold_statement)
        self.assertIn("D1 does not replace UDS-TAP", bridge)
        self.assertIn("O-Series", bridge)


if __name__ == "__main__":
    unittest.main()
