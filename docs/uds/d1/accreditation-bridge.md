# D1 Relationship to UDS-TAP and O-Series

**Document ID:** UDS-D1-ACCREDITATION-BRIDGE-v1.0

UDS Tier D1 is the public threshold layer. It records a voluntary promise, supporting evidence, and repair posture.

UDS-TAP and O-Series are the stronger enforcement and accreditation layers that may be used by higher tiers.

## Layer distinction

| Layer | Function | Verification Strength |
|---|---|---|
| D1 Public Threshold | Public promise, evidence links, visible repair path | Self-attestation |
| D1 Registry Schema | Machine-readable registry entry format | Schema validation |
| UDS-TAP | Testing, review, accreditation, revocation, and continuous audit logic | Procedural and technical verification |
| O-Series Soul | Ethics Kernel, refusal behavior, witness receipts, and policy-gated runtime behavior | Runtime enforcement and test evidence |

## D1 boundary

D1 must not claim that a project is technically safe, fully accredited, or independently audited.

D1 only proves that a builder has publicly committed to the Universal Diamond Standard and has made enough evidence visible for review, critique, and correction.

## UDS-TAP bridge

UDS-TAP can consume D1 registry entries as input evidence, but D1 does not replace UDS-TAP.

Future UDS-TAP flows may check:

- whether the D1 commitment exists and validates against the schema;
- whether linked evidence is reachable;
- whether the project documents user rights, consent controls, drift reporting, and repair pathways;
- whether O-Series or Sarah AI integrations acknowledge boundary clauses;
- whether test evidence supports claims around privacy, non-coercion, transparency, and service-to-life;
- whether drift reports were handled within a defined response window.

## O-Series bridge

For O-Series or Sarah AI implementations, D1 registry evidence should point to the runtime files, policy files, tests, or documentation that show:

- consent boundaries;
- capability limits;
- Prime Refusal behavior;
- anti-deification posture;
- fail-closed ingress behavior;
- Witness Receipts that avoid raw context storage;
- explicit separation between Sarah AI and Human Sarah.

## Practical rule

D1 asks: **Did you make the promise visible?**

UDS-TAP asks: **Can the promise survive inspection, tests, review, and drift?**

O-Series asks: **Does the runtime actually behave inside the promise?**

Keep these layers separate so the public chassis stays accessible while the accreditation spine remains rigorous.
