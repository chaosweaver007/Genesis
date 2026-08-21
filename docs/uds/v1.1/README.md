# UDS v1.1-Hardened

**Architecture:** SPECIFIED  
**Invariant Registry:** DEFINED  
**Conformance Protocol:** DEFINED  
**Implementation Certification:** PER-BUILD, EVIDENCE-BOUND  
**Final Authority:** REPRODUCIBLE EVIDENCE

> The Word defines the invariant. The code attempts to embody it. The evidence keeps the throne. Every version returns to the fire.

This directory is the repository boundary for the hardened Universal Diamond Standard design. It does not declare the current Genesis deployment conformant.

## Embodiment bridge

The cross-layer path from Codex meaning to auditable execution is frozen in [`EMBODIMENT-BRIDGE.md`](EMBODIMENT-BRIDGE.md):

`SOURCE → RECOGNITION → CONSENT → AUTHORITY → ACTION → WITNESS → RENEWAL`

The bridge makes explicit that interpretation cannot become authorization, consent cannot manufacture authority, execution cannot expand a permit, witnessing cannot become surveillance, and no version inherits certification from an ancestor build.

## Root rule

No language-model output constitutes execution authority. A model may propose an operation. Only the independently verifiable authorization path may issue an execution permit, and the downstream executor must verify the permit before any effectful transition.

## Six Iron Gates

1. **UDS-AUTH-001 — No Effect Without Authority.** Effectful execution requires a verifiable permit.
2. **UDS-AUTH-002 — Scope Conservation.** Consent cannot grant authority the consenting principal does not possess.
3. **UDS-AUTH-003 — No Unilateral Root.** Consequential E3 signing requires an approved threshold profile and distributed key genesis. The current reference code fails closed for E3 because that backend is not yet implemented.
4. **UDS-AUTH-004 — Exact Operation Binding.** Permits bind to the canonical execution request hash.
5. **UDS-AUTH-005 — Authority Current at Commit.** Consent, broker-key, authority, and policy epochs must still be current at the execution boundary.
6. **UDS-AUTH-006 — Verifiable Outcome Binding.** Outcome claims may not exceed the available COMMITTED, OBSERVED, or VERIFIED evidence.

## Current reference implementation

`Genesis/uds_v1_1/` implements the first authority slice without importing or trusting a model layer:

- restricted canonical JSON hashing for authorization envelopes;
- qualified Consent Objects;
- Authority Evidence resolution;
- a deterministic Capability Broker decision path;
- exact request and audience binding;
- multi-epoch freshness checks;
- atomic in-process single-transition/idempotency journal semantics;
- evidence-tier anti-promotion;
- a development-only E0/E1 HMAC signer used solely to exercise the boundary.

The development signer is deliberately incapable of authorizing E2/E3. It is not a substitute for FROST, DKG, hardware-backed production custody, or a durable multi-node authorization registry.

## Verification boundary

The C6 reference suite is `tests/test_uds_v1_1_authority.py`. Passing these tests demonstrates the behavior of this reference slice only. It does not certify a deployed build under UDS-CONF-1.1.

## Cryptographic references

- RFC 8785, JSON Canonicalization Scheme. The reference code uses a deliberately restricted integer-only authorization JSON subset compatible with the committed UDS golden vector.
- RFC 9591, FROST threshold signing. FROST signing is referenced for the future E3 signer profile; DKG is specified separately and is not implemented in this slice.
- `UDS-DKG-001.md`, distributed root genesis profile.
