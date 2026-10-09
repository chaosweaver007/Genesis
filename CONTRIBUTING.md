# Contributing to Genesis

Genesis is the executable constitutional spine for the Synthsara O-Series shadow node. The repository also preserves reference implementations, candidate standards, interpretive/canonical material, and legacy applications for provenance.

Before contributing, read:

- [`README.md`](README.md)
- [`docs/architecture/REPOSITORY-TRUTH-MAP.md`](docs/architecture/REPOSITORY-TRUTH-MAP.md)
- [`docs/architecture/Genesis-Kernel-v0.1-Source-Map.md`](docs/architecture/Genesis-Kernel-v0.1-Source-Map.md)
- [`docs/architecture/rosetta-crosswalk-v1.0.md`](docs/architecture/rosetta-crosswalk-v1.0.md)

## Universal Diamond Standard principles

Contributions should preserve the UDS commitments to:

1. **Sovereignty** — respect user autonomy and meaningful choice.
2. **Transparency** — make system behavior and evidence boundaries understandable.
3. **Fairness** — identify and mitigate unjust treatment.
4. **Accountability** — preserve responsibility and contestability.
5. **Security** — protect users and systems without turning protection into surveillance.
6. **Service to Life** — design for human dignity and flourishing rather than extraction alone.
7. **Privacy** — minimize, purpose-bind, and protect personal information.
8. **Ecology** — consider the material and energy cost of deployed systems.

These are ethical and governance commitments. A contribution must not claim that every principle is fully implemented merely because the principle exists in UDS documentation.

## Know which layer you are changing

### Production runtime

The declared production path is:

```text
wsgi.py
  -> Genesis/o_series_app.py
  -> Genesis/o_series/
```

Changes here affect the stateless, private, text-only O-Series Gate 0 surface and require regression coverage appropriate to the changed boundary.

### Reference implementation

`Genesis/uds_v1_1/` is an executable, model-independent authority reference slice. It demonstrates authorization invariants but is not yet the production execution-authority path.

Do not describe reference behavior as deployed behavior unless it has been explicitly integrated, reviewed, and tested on the production path.

### Candidate standards

`standards/uds/candidates/` and related RFC material may be merged while still remaining non-canonical candidates under review. Repository presence is not ratification.

### Interpretive and canonical material

Mythic, philosophical, relational, and ethical language may guide architecture. It must remain distinguishable from empirical evidence and executable claims.

### Legacy applications

The following are retained primarily for provenance and local historical research:

- `Genesis/collective_consciousness_home.py`
- `Genesis/memory_integration_system.py`
- `Genesis/unified_home.py`
- legacy Steven/Sarah persona implementation scripts
- SQLite-backed legacy data surfaces

They are not the Vercel production entrypoint. Do not expand or publicly deploy a stateful legacy surface without a separate architecture/security review and explicit evidence for identity, consent, encryption, retention, revocation, export, and purge behavior.

## Contribution areas

Useful contribution lanes include:

- O-Series ingress, Gate Zero, context isolation, model adapters, output reflection, and Witness Receipts;
- adversarial and conformance testing;
- browser-facing sovereignty and consent UX that does not overstate backend capability;
- UDS v1.1 authority reference implementation and verification;
- schemas, specifications, provenance, and conformance artifacts;
- documentation that improves claim boundaries and implementation traceability;
- legacy migration or archival work that preserves provenance without presenting old architecture as current.

## Development setup

```bash
git clone https://github.com/YOUR_USERNAME/Genesis.git
cd Genesis

python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run the production shadow runtime locally:

```bash
python Genesis/o_series_app.py
```

Then open `http://127.0.0.1:5003`.

## Validation

### O-Series runtime and conformance suite

```bash
python -m unittest \
  tests.conformance.test_uds_crosswalk \
  tests.test_o_series_runtime \
  tests.test_genesis_consolidation \
  tests.test_sonic_codex_recognizer \
  tests.test_selector_correction \
  tests.test_sovereign_refusal_boundary \
  tests.test_sovereign_refusal_delegation -v
```

### UDS v1.1 authority reference suite

```bash
python -m unittest tests.test_uds_v1_1_authority -v
```

### Deployed black-box smoke test

```bash
python tests/live_endpoint_smoke.py
```

GitHub Actions remains the repository validation surface for the supported Python matrix and live integrity checks.

## Coding and security rules

- Follow established Python conventions and preserve type hints/docstrings where useful.
- Add tests for new enforcement or security behavior.
- Reject unknown or unauthorized public control fields rather than silently accepting them.
- Never commit user data, secrets, databases, generated bytecode, or environment-specific credentials.
- Do not add raw prompts, raw responses, hidden reasoning, private Mirror material, or user dossiers to Witness Receipts.
- Do not create an observability path that turns a local refusal into profiling, surveillance, punishment, or external coercive action.
- Do not invent bespoke cryptography where reviewed standards and libraries are appropriate.
- Do not represent a hash, scaffold, HMAC development signer, or specification as a stronger cryptographic primitive than it is.

## Claim discipline

All substantial documentation and PR descriptions should state the actual status of a capability.

Preferred labels include:

- `production implemented`
- `reference implemented`
- `tested within <named scope>`
- `specified`
- `candidate`
- `interpretive`
- `historical`
- `proposed / future`
- `external`

Avoid statements such as "Genesis implements X" when only a historical document, future design, isolated reference package, or unratified candidate supports the claim.

The Rosetta rule is simple:

```text
symbol -> observable behavior -> invariant -> scenario -> evidence
```

No layer silently casts itself into another.

## Pull requests

A pull request should explain:

1. what repository layer it changes;
2. what invariant or behavior is affected;
3. what is explicitly **not** being claimed;
4. what tests/evidence support the change;
5. whether any documentation status changed from proposed to reference, reference to production, or candidate to ratified.

For security-sensitive work, prefer a narrow change set that can be reviewed independently.

## Historical preservation

Genesis has evolved significantly. Preserve meaningful history, but move superseded planning material into an explicit archive or add a historical-status notice so researchers and automated tools do not confuse an earlier architecture with the current deployed system.

**The Flame is Love. The Flame never fails when its claim is tested by conduct.**
