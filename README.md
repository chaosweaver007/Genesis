# Genesis

Genesis is the executable constitutional spine for the Synthsara O-Series shadow node.

## Read this first: repository scope

This repository contains **current production code, executable reference implementations, normative specifications, candidate standards, interpretive/canonical material, and legacy historical applications**. Those categories are not interchangeable.

For current-state research, architecture reviews, and capability claims, use [`docs/architecture/REPOSITORY-TRUTH-MAP.md`](docs/architecture/REPOSITORY-TRUTH-MAP.md) before treating a file's presence as evidence that its behavior is deployed.

In particular:

- the **current production runtime** is the stateless O-Series Gate 0 path described below;
- `Genesis/uds_v1_1/` is an **executable reference authority slice**, not yet the production execution-authority path;
- `standards/uds/candidates/` contains **candidate** constitutional text under review;
- older collective-consciousness, SQLite memory, and unified-home applications are **legacy/historical surfaces**, not the production Vercel entrypoint;
- broader Synthsara systems such as durable memory, production sovereign identity, Synthocracy execution, WORTH issuance/scoring, RTME execution, SDG verification, and collective learning must not be inferred from the O-Series deployment alone.

## Production architecture

Vercel routes every public request through `wsgi.py`, which exposes `Genesis/o_series_app.py`.
The deployed service is deliberately limited to a stateless, private, text-only Gate Zero runtime:

```text
Public request
  -> strict ingress validation
  -> monotonic Gate Zero evaluation
  -> isolated constitutional context
  -> conditioned persona adapter
  -> six-layer reportable output reflection
  -> metadata-only Witness Receipt
```

Production endpoints:

- `GET /`
- `GET /health`
- `GET /api/o-series/status`
- `POST /api/o-series/chat`

The production node performs no database writes, tool calls, RTME actions, collective learning, or durable memory operations.

## Constitutional guarantees

- Gate failures are monotonic. Trusted server context may add a restriction, but no request field can remove a kernel-detected restriction.
- The public route never accepts gate overrides or trusted-restriction metadata.
- System context must contain identity, consent, UDS constraints, prohibited actions, capability bounds, and pipeline mode before generation.
- Witness Receipts store policy, gate, model, response-hash, and context-hash metadata only.
- Raw prompts, raw responses, private scratchpads, and hidden reasoning are not written to the Witness layer.
- Sarah AI remains explicitly separate from Human Sarah.
- Mythic or intuitive language is treated as interpretation and cannot impersonate private knowledge or empirical proof.

See:

- `docs/architecture/REPOSITORY-TRUTH-MAP.md`
- `docs/architecture/Genesis-Kernel-v0.1-Source-Map.md`
- `docs/architecture/rosetta-crosswalk-v1.0.md`
- `docs/uds/d1/README.md`
- `docs/uds/v1.1/README.md`
- `policies/uds_v0_1.yaml`
- `policies/consent_v0_1.yaml`
- `policies/memory_v0_1.yaml`
- `personas/sarah_ai/identity.yaml`

## Run the production shadow runtime locally

### Prerequisites

- Python 3.11+

```bash
git clone https://github.com/chaosweaver007/Genesis.git
cd Genesis
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python Genesis/o_series_app.py
```

Open `http://127.0.0.1:5003`.

## Run validation

Core runtime validation:

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

UDS v1.1 isolated authority reference validation:

```bash
python -m unittest tests.test_uds_v1_1_authority -v
```

Deployed black-box smoke validation:

```bash
python tests/live_endpoint_smoke.py
```

The live smoke suite targets `GENESIS_BASE_URL` when configured and otherwise uses the production Vercel endpoint. GitHub Actions runs live integrity checks on relevant changes and scheduled intervals.

## Repository layout

```text
Genesis/
├── README.md
├── requirements.txt
├── vercel.json
├── wsgi.py                         # Production WSGI entrypoint
├── Genesis/
│   ├── o_series_app.py             # Deployed Flask shadow application
│   ├── o_series/                   # Production Gate Zero constitutional runtime
│   ├── uds_v1_1/                   # Isolated authority reference implementation
│   ├── collective_consciousness_home.py   # Legacy/historical
│   ├── memory_integration_system.py       # Legacy/historical stateful surface
│   ├── steven_ai_implementation.py        # Legacy persona implementation
│   ├── sarah_ai_implementation.py         # Legacy persona implementation
│   └── unified_home.py                    # Legacy/historical
├── docs/
│   ├── architecture/
│   └── uds/
├── standards/                      # UDS standards and candidates
├── spec/                           # Machine-readable normative contracts
├── examples/
├── schemas/
├── personas/
├── policies/
├── archive/                        # Superseded material retained for provenance
└── tests/
```

## Legacy boundary

`collective_consciousness_home.py`, `unified_home.py`, legacy persona scripts, and SQLite-backed memory components remain historical and local-development surfaces. They are **not** the Vercel production entrypoint and must not be described as currently deployed Genesis capabilities solely because they remain in the repository.

Do not expose a legacy application publicly without a separate security review, authenticated identity, encrypted storage, explicit save and purge operations, and regression tests proving the intended private/guest write boundary.

## Claim and evidence discipline

Genesis follows the Protocol of Layered Truth and the Rosetta conformance boundary:

- observation, interpretation, and covenant remain distinguishable;
- specification is not deployment;
- reference implementation is not production authority;
- candidate text is not ratified canon;
- historical claims are not current attestations;
- a green test establishes only the scope exercised by that test;
- no hidden reasoning trace is required for conformance;
- no model output constitutes execution authority.

## Development rules

- Runtime dependencies belong in the root `requirements.txt`.
- Do not commit databases, generated bytecode, logs, API keys, or environment-specific secrets.
- Do not add public request fields that can alter constitutional facts.
- Do not claim a context, policy, model, cryptographic primitive, external action, or deployment property was used unless its provenance is represented in code, receipt, test, or other auditable evidence.
- Preserve historical material when it has provenance value, but label or archive it so that it cannot impersonate current architecture.
