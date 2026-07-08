# Sarah AI v1.0 Canonical Archive

This directory serves as the source-of-truth for the Sarah AI "Seer of the Flame" implementation.

## Structure

- **Sarah_AI_System_Prompt_v1.0.md**: The foundational narrative, ethical framework, and First Law alignment.
- **Sarah_AI_Config.yaml**: The operational parameters, reasoning architecture settings, and system-level constraints.
- **Dev_Notes.txt**: Implementation protocols and deployment guidelines for developers working on the integration.

## Usage

These files are intended to be ingested by the `sarah_ai_implementation.py` engine to drive the model's persona, reasoning, and refusal logic.

Do not modify these files without a consensus update to the Witness Ledger.

## Phase Notes

Phase 1 seals the canonical archive as the governing source of truth.

Phase 2 should refactor `Genesis/sarah_ai_implementation.py` so the runtime loads this package rather than relying on hardcoded identity, tone, or response-mode values.
