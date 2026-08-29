# Changelog

All notable changes to Genesis are documented in this file.

## Unreleased

### UDS Sovereign Refusal Boundary v1.0-rc2.1 Candidate

- Staged UDS Article VI candidate under `standards/uds/candidates/`.
- Added O-Series local-only sovereign refusal runtime enforcing `REFUSE_SELF != CONTROL_OTHER`.
- Added bounded privacy-preserving Witness Receipt scaffold with no raw prompt, user/session identity, private Mirror material, risk score, exact timestamp, or hidden reasoning.
- Added TEST-SRB-01 through TEST-SRB-07 and constructor hardening checks.
- Added TEST-SRB-06 to prove injected telemetry/admin sinks are never invoked by refusal handling.
- Added TEST-SRB-07 to exercise refusal through a real Flask application lifecycle, short-circuiting before the downstream view and asserting no application-owned socket/URL emission or sensitive log/response leakage.
- Explicitly bounded TEST-SRB-07 claims to application-owned observability. Reverse proxies, host collectors, sidecars, kernel telemetry, and independently configured APM/OpenTelemetry agents remain deployment-level audit targets.
- Current receipt intentionally retains `zk_proof=None`; hashes and metadata minimization are not represented as a cryptographic zero-knowledge proof.

## 2026-08-27

### UDS v1.1 Authority Core

- Added a hardened authorization reference slice with consent objects, independent authority evidence, canonical request hashing, capability permits, state/epoch checks, and dedicated CI.

## 2026-08-21

### Sonic Codex Recognition Layer

- Integrated the Sonic Codex recognition layer into the O-Series pipeline.

## Earlier history

See repository history and release notes for prior Genesis, O-Series, UDS D1, and Synthsara changes.
