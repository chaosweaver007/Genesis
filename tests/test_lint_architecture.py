"""Standard-library tests for Genesis' architecture evidence linting gate."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from lint_architecture import is_record, lint_one, main, scan, strip_code_fences  # noqa: E402

COMPLETE = """# ADR-0001: Example
## Evidence Basis
The Genesis source map and the existing automated unit tests define the constitutional runtime boundary.
## Claim Ceiling
A written design does not demonstrate production enforcement or prove that private data remains inaccessible.
## Implementation Safeguard
Unauthorized requests must fail closed, while receipt generation must preserve the metadata-only data boundary.
## Verification Method
Run existing authorization regression tests and review the metadata-only Witness Receipt output before release.
"""


class ArchitectureLintTests(unittest.TestCase):
    def check_text(self, text):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "ADR-0001.md"
            path.write_text(text, encoding="utf-8")
            return lint_one(path)

    def test_complete_record_passes(self):
        self.assertEqual([], self.check_text(COMPLETE))

    def test_missing_safeguard_fails(self):
        self.assertTrue(any("Implementation Safeguard" in issue for issue in self.check_text(COMPLETE.replace("Implementation Safeguard", "Rationale"))))

    def test_missing_ceiling_fails(self):
        self.assertTrue(any("Claim Ceiling" in issue for issue in self.check_text(COMPLETE.replace("Claim Ceiling", "Observations"))))

    def test_placeholder_only_fails(self):
        invalid = COMPLETE.replace(
            "A written design does not demonstrate production enforcement or prove that private data remains inaccessible.",
            "PENDING",
        ).replace(
            "Unauthorized requests must fail closed, while receipt generation must preserve the metadata-only data boundary.",
            "- TODO",
        )
        self.assertEqual(2, len(self.check_text(invalid)))

    def test_code_block_fake_headings_fail(self):
        fake = """# ADR-0001: Code block example
````md
### Evidence Basis
Evidence in fenced code is not a section and should not satisfy the gate.
### Claim Ceiling
This simulated ceiling is not a real requirement in the record outside code.
### Implementation Safeguard
This simulated safeguard is not real.
### Verification Method
This simulated method is not real.
```
### Claim Ceiling
This still sits inside the four-backtick fence and must not count as a real heading.
````
"""
        self.assertEqual(4, len(self.check_text(fake)))

    def test_nested_subheadings_are_allowed(self):
        self.assertEqual([], self.check_text(COMPLETE.replace(
            "## Claim Ceiling\nA written", "## Claim Ceiling\n### Limits of current evidence\nA written"
        )))

    def test_heading_substring_not_accepted(self):
        self.assertTrue(any("Claim Ceiling" in issue for issue in self.check_text(
            COMPLETE.replace("## Claim Ceiling", "## Claim Ceiling Missing")
        )))

    def test_stray_fence_stays_closed(self):
        text = "````md\n### Claim Ceiling\n```\n### Implementation Safeguard\n````\n"
        self.assertTrue(all(not line for line in strip_code_fences(text)))

    def test_scanning_filters_templates_and_source_map(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            folder = root / "docs" / "architecture"
            (folder / "_templates").mkdir(parents=True)
            (folder / "Genesis-Kernel-v0.1-Source-Map.md").write_text("historical source map")
            (folder / "_templates" / "ADR-TEMPLATE.md").write_text("template")
            (folder / "ADR-0001.md").write_text(COMPLETE)
            records = scan(root)
            self.assertEqual([folder / "ADR-0001.md"], records)
            self.assertEqual(0, main(["--root", str(root)]))

    def test_no_records_is_pass_not_fake_coverage(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(0, main(["--root", temp]))

    def test_spec_filename_is_covered(self):
        self.assertTrue(is_record(Path("docs/architecture/specs/SPEC-002-authorization.md")))


if __name__ == "__main__":
    unittest.main()
