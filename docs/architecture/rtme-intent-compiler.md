# SYN-RD-002 — Bounded RTME Intent Compiler (candidate)

**Claim class:** ENGINEERING REQUIREMENT  
**Implementation status:** FUNCTIONAL PROOF (standalone, offline library)  
**Canonical status:** candidate; not ratified constitutional policy  
**Owner:** Genesis engineering / Architect review  
**First drafted:** 2026-10-31  
**Source:** [Genesis](../../README.md), [Genesis source map](./Genesis-Kernel-v0.1-Source-Map.md), [UDS consent policy](../../policies/consent_v0_1.yaml), [Node Zero](https://github.com/chaosweaver007/synthsara-node-zero)  
**Source file:** `Genesis/rtme_parser.py`  
**Tests:** `tests/test_rtme_parser.py`

## Scope

This Python 3.11+ module compiles a bounded *draft plan*, not executable instructions.
The domain-specific abstract syntax tree (AST) consists only of nine fixed
`DraftNode` objects in three 3–6–9 phases. The natural-language intention
is preserved as inert data. There is **no** execution language, Python `ast`
evaluation, dynamic import, filesystem access, subprocess, outbound HTTP,
device interaction, memory persistence, or automatic approval.

Do not mistake this module for an LLM natural-language understanding system.
It does not infer whether arbitrary words are harmless. All real actions
require a separate, scoped, receiver-side capability permit and a qualified
review when appropriate. There is no capability broker or action executor
in this module.

## Example

```python
from rtme_parser import compile_intent

plan = compile_intent({
    "intent": "Create an opt-in community tutoring exchange.",
    "success_criterion": "Five volunteers try a reversible pilot.",
    "horizon_days": 30,
    "consent_to_draft": True,
})

draft = plan.to_dict()
assert draft["execution_status"] == "NOT_EXECUTED"
assert draft["witness_write"] == "none"
assert draft["execution_permitted"] is False
```

The compiler accepts only four specified fields. It rejects unexpected
fields, malformed text, control characters, unsupported horizons and
absent/inexact consent. Explicit consent grants **only** permission to
produce this local draft; it does not extend Genesis Gate Zero authority.

## Boundaries and limitations

- `IntentAST.to_dict()` includes the original user-authored intention and
  success criterion, so callers must not log it or send it to analytics.
- `metadata_digest()` is SHA-256 of *non-private* metadata and does not bind
  the intention; it is **not** a signed Witness Receipt, an integrity proof
  of the complete plan, or an RFC 8785 JCS canonicalization implementation.
- `uds_certification: NOT_ASSESSED` means no automated legal compliance,
  independent ethics audit, clinical judgment or security certification.
- The fixed template cannot ensure physical causality, safety, fairness, or
  suitability of a proposed human action. It simply cannot actuate anything.
- This module is not imported by `wsgi.py` or `Genesis/o_series_app.py`,
  which must remain stateless and tool-free. No production routes are added.
- Public Node Zero/localStorage is not an encrypted vault. A new Gate 1 vault,
  consent service, or receiver-side permit system requires its own design,
  threat model and tests.
- Privacy promises apply only to the compiler's *lack of I/O*. The caller
  is responsible for input handling, process logs and infrastructure.

## Local verification

```bash
python -m unittest tests.test_rtme_parser -v
python -m unittest tests.test_o_series_runtime tests.test_genesis_consolidation tests.test_uds_d1_registry_artifacts -v
```

The dedicated test suite covers consent fail-closed, strict field validation,
3–6–9 typed nodes, non-execution metadata, unicode boundaries, injected code
remaining inert data, stable non-private metadata digests, and patched
filesystem/process/network API isolation.

## Next distinct security work packages

1. Receiver-side `UDS-AUTH-001…006` capability verification: authorized
   issuer keys, domain separation, canonical request bytes (RFC 8785),
   single-use atomic nonces, clock windows, scoped operations, and commit-time
   revocation. **Not implemented here.**
2. Explicit Gate 1 identity and consent propagation with a protected vault.
3. Hash-linked signed metadata-only Witness receipts, minimizing leakage.
4. Adversarial action-boundary testing. Passing this compiler's unit tests
   is not evidence of executor conformance.

**Ledger before Spiral:** this document specifies which behaviors exist,
which are unimplemented, and the evidence needed for each promotion.
