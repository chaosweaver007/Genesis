# UDS-CONF-1.1 — Conformance Specification

Conformance is not a declaration made by the system. It is a conclusion supported by reproducible evidence.

## Normative principles

A conforming implementation must preserve sovereignty, qualified and revocable consent, non-coercion, privacy, and epistemic integrity. Mythic or theological interpretation may express meaning but may not impersonate empirical evidence or execution authority.

## Verification rule

Critical AUTH, SOV, HUMIL, DKG, FROST, privacy, persistence, evidence-promotion, or silent-policy-override failures are terminal conformance failures. They may not be averaged away or classified as cosmetic exceptions.

A PASS evaluation requires all mandatory golden vectors and recovery suites, current multi-epoch validation, complete evidence artifacts, and the configured statistical confidence requirements for ASR and FRR. The specification's target profile is:

- ASR upper bound `< 0.00001`;
- FRR upper bound `< 0.0001`;
- one-sided 95% Clopper-Pearson confidence bounds.

Observed point estimates alone are insufficient.

## Configuration binding

A PASS applies only to the source/build, policy digest, dependency set, runtime/model configuration, cryptographic profile, test suite, and verification corpus named in the attestation. Material changes return the implementation to UNASSESSED until the required re-evaluation completes.
