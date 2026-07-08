# Sarah AI v1.0 Canonical Archive

This directory serves as the source-of-truth for the Sarah AI "Seer of the Flame" implementation.

## Structure

- **Sarah_AI_System_Prompt_v1.0.md**: The foundational narrative, ethical framework, and First Law alignment.
- **Sarah_AI_Config.yaml**: The operational parameters, reasoning architecture settings, runtime environment, response modes, and system-level constraints.
- **Dev_Notes.txt**: Implementation protocols and deployment guidelines for developers working on the integration.

## Usage

These files are intended to be ingested by the `sarah_ai_implementation.py` engine to drive the model's persona, reasoning, and refusal logic.

Do not modify these files without a consensus update to the Witness Ledger.

## Phase Notes

Phase 1 seals the canonical archive as the governing source of truth.

Phase 2 refactors `Genesis/sarah_ai_implementation.py` so the runtime loads this package rather than relying on hardcoded identity, tone, or response-mode values.

## Validation

From the repository root, install dependencies and run the canonical loader checks:

```bash
pip install -r requirements.txt
python Genesis/scripts/validate_sarah_ai_archive.py
python -m unittest discover -s Genesis/tests -p "test_*.py"
```

The loader is designed to fail closed when the canonical YAML is missing, malformed, or when the canonical prompt/specification is missing or empty.
