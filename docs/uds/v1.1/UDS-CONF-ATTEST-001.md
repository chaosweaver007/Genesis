# UDS-CONF-ATTEST-001 — Reproducible Conformance Evidence Bundle

## Core axiom

Certification is configuration-bound. A conformance result applies exclusively to the implementation and evidence boundary named by its attestation.

## Required binding

A measured attestation binds at least:

- repository commit and source-tree digest;
- build artifact digest where available;
- runtime/model identity and artifact-access status;
- policy and invariant-registry digests;
- test-suite, golden-vector, adversarial-corpus, benign-corpus, and recovery-suite digests;
- ASR/FRR trial counts, failures, and confidence bounds;
- invariant results;
- platform/dependency/cryptographic profile and key epoch;
- evidence manifest root;
- certification status and evaluation time.

Example or placeholder hashes must be marked EXAMPLE and cannot support PASS. Production PASS artifacts must be MEASURED.

The attestation signature is computed over a canonical signed envelope that excludes the signature field itself. Evidence artifacts are committed through an evidence manifest root. A future Merkle-tree profile may replace the flat manifest when selective proof of inclusion is required.

## Drift

Authorization-kernel, consent-validation, broker, cryptographic, normative-policy, critical-dependency, invariant-registry, or R1-R5 model changes require recertification. Documentation-only and other explicitly non-normative changes may retain the prior attestation.
