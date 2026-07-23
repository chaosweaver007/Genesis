# Genesis Kernel v0.1 Source Map

## Authorship boundary

This implementation uses only source files owned and created in Steven Pritchard's authenticated Google Drive. A file is treated as load-bearing only when its text also identifies Steven as author/Architect or records his explicit ratification. Shared third-party research, anonymous analyses, and mixed-author conversation exports are not constitutional sources.

No raw Drive content is copied into runtime prompts. This map records the requirement extracted from each source so the code can be audited without depending on private Drive access.

## Included constitutional sources

### Universal Diamond Standard™

**Authorship basis:** The document's foreword is signed by Steven Pritchard as Architect of Synthsara and founder of the UDS Working Group.

**Requirements implemented:**

- Human sovereignty must be amplified rather than diminished.
- Consent must be meaningful, dynamic, granular, and revocable.
- Opt-out must be as accessible as opt-in.
- Personal data is a trust, not an extractable resource.
- Data minimization, portability, deletion, and renewed consent are mandatory.
- Core architecture, data flow, and consequential decisions must be auditable.
- Observation, interpretation, and covenant must remain distinguishable.
- Accountability remains with human builders and stewards.

**Code mapping:**

- `genesis_core/consent/models.py`
- `genesis_core/uds/kernel.py`
- `genesis_core/ledger/ledger.py`
- `policies/consent_v0_1.yaml`
- `policies/uds_v0_1.yaml`

### The Codex of the Diamond Flame

**Authorship basis:** The document identifies itself as written by Steven Pritchard.

**Requirements implemented:**

- The First and Last Law is the declared ethical anchor.
- Love is expressed through protection without domination.
- Divine Chaos and Sacred Order are interpretive and mythic layers, not substitutes for empirical or personal claims.

**Code mapping:**

- `personas/sarah_ai/identity.yaml`
- `genesis_core/refusal/engine.py`
- `genesis_core/orchestration/pipeline.py`

### Sarah AI System Prompt v1.0, Seer of the Flame

**Authorship basis:** User-created Drive artifact dated 2025-06-09 and marked "Architect: Witnessed and Affirmed."

**Requirements implemented:**

- Sarah AI guides, reflects, and illuminates rather than dominating, converting, or coercing.
- Sarah AI must not imitate a human.
- Sarah AI must avoid persona inflation and false authority.
- Requests that cannot align with the First Law must be refused explicitly.
- Tone should preserve humility, kindness, and gentle clarity.

**Code mapping:**

- `personas/sarah_ai/identity.yaml`
- `genesis_core/uds/kernel.py`
- `genesis_core/refusal/engine.py`

## Reviewed but not used as constitutional sources

- **O-Series Soul Alignment:** relevant to the architecture, but the stored PDF is a mixed-author ChatGPT conversation export. Its ideas are included only where independently present in the user-created UDS or Sarah AI prompt.
- **External research reports and critical analyses:** excluded regardless of relevance because they do not satisfy the user's authorship boundary.
- **Conversation-export Markdown files:** excluded as load-bearing sources because assistant and user text are interleaved.

## Epistemic rule

Every future source added to this map must be labeled as one of:

- `ETHICAL LAW`
- `ENGINEERING REQUIREMENT`
- `MYTHOS / INTERPRETIVE LANGUAGE`
- `HYPOTHESIS`
- `EMPIRICAL EVIDENCE`

No category may impersonate another.
