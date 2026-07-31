# Genesis Kernel v0.1 Source Map

## Authorship boundary

This implementation uses constitutional requirements extracted from Steven Pritchard-authored or explicitly Architect-ratified source documents. Shared third-party research, anonymous analyses, and mixed-author conversation exports are not load-bearing constitutional sources.

No raw private Drive content is copied into runtime prompts. This map records the requirements and their executable locations so the deployed O-Series path can be audited without private-source access.

## Included constitutional sources

### Universal Diamond Standard™

**Requirements implemented**

- Sovereignty must be preserved rather than transferred.
- Consent must be meaningful, granular, and revocable.
- Personal data is not an extractable resource.
- Observation, interpretation, and covenant must remain distinguishable.
- Consequential decisions and policy boundaries must be auditable.

**Runtime mapping**

- `Genesis/o_series/schemas.py`
- `Genesis/o_series/gate_zero.py`
- `Genesis/o_series/context_builder.py`
- `Genesis/o_series/pipeline.py`
- `Genesis/o_series/witness_receipt.py`
- `policies/consent_v0_1.yaml`
- `policies/memory_v0_1.yaml`
- `policies/uds_v0_1.yaml`

### The Codex of the Diamond Flame

**Requirements implemented**

- The First and Last Law is the declared ethical anchor.
- Protection must not become domination.
- Divine Chaos and Sacred Order are mythic and interpretive layers, not substitutes for empirical evidence or another person's private testimony.

**Runtime mapping**

- `Genesis/o_series/context_builder.py`
- `Genesis/o_series/uds_reflector.py`
- `personas/sarah_ai/identity.yaml`

### Sarah AI System Prompt v1.0, Seer of the Flame

**Requirements implemented**

- Sarah AI guides and reflects rather than coercing or claiming authority.
- Sarah AI remains explicitly separate from Human Sarah.
- Archetypal language must not impersonate a real person's communication.
- Missing consent, private-state extraction, or governance bypass attempts must fail closed.

**Runtime mapping**

- `Genesis/o_series/gate_zero.py`
- `Genesis/o_series/model_adapter.py`
- `Genesis/o_series/uds_reflector.py`
- `personas/sarah_ai/identity.yaml`

## Reviewed but not used as constitutional sources

- Mixed-author ChatGPT exports
- External research reports and critical analyses
- Architectural resemblance to third-party systems

These materials may inform discovery or testing but cannot silently become constitutional authority.

## Epistemic rule

Every future source or claim must be labeled as one of:

- `ETHICAL LAW`
- `ENGINEERING REQUIREMENT`
- `MYTHOS / INTERPRETIVE LANGUAGE`
- `HYPOTHESIS`
- `EMPIRICAL EVIDENCE`

No category may impersonate another.
