# Genesis Archive-to-Runtime Provenance Crosswalk

## Purpose

This document cross-references the private `conversations-1.json` archive lineage with the public Genesis repository without copying private transcript content into the codebase.

It exists to prevent two opposite provenance failures:

1. erasing genuine historical lineage because an early concept is no longer production architecture;
2. promoting an early theory, pitch, assistant-generated proposal, or blueprint into a claim that the capability was implemented at that time.

The private archive establishes chronology, concept lineage, user direction, and historical context. Public repository code, tests, deployment evidence, and current specifications establish implementation status.

**Archive evidence is not production evidence. Production evidence is not proof that a concept originated only when it was implemented.**

## Evidence rules

- Private archive material remains outside the production runtime and is not copied into model prompts or Witness Receipts.
- Direct user statements, assistant proposals, later user adoption, later synthesis, and implementation evidence are different provenance classes.
- A later polished document must not be backdated as if it existed in complete form at an earlier precursor node.
- A historical implementation claim does not certify the current runtime.
- A current implementation does not retroactively validate historical scientific, metaphysical, privacy, security, or deployment claims.
- Mythic and symbolic concepts remain interpretive unless independently translated into observable requirements and evidence through the Rosetta Crosswalk.

## Lineage crosswalk

| Date | Private archive node | Provenance signal | What it establishes | Current public descendant | Current status |
|---|---|---|---|---|---|
| 2025-01-05 | `Website App Wireframe Plan` (`677b1302-ad48-800c-993b-a7dcb4cbf5fa`) | Direct user data-control requirement | Users should own their data and retain extraction/deletion/control rights. | `policies/consent_v0_1.yaml`, `policies/memory_v0_1.yaml`, `docs/architecture/Synthsara-Whitepaper-Build-Map.md` | Principle lineage is strong. Production Gate 0 is zero-write; authenticated consent vault and durable user-controlled memory remain later phases. |
| 2025-01-06 | `Living App Concept` (`677baf30-a5bc-800c-9f33-41d93d1ba802`) | Direct user theory and inquiry plus assistant speculative elaboration | Early collective-consciousness, mathematical-balance, cycles, Fibonacci/Phi, and 3-6-9 inquiry are genuine historical precursors. | `docs/Preamble.md`, `docs/architecture/rosetta-crosswalk-v1.0.md`, Codex/canon material | Historical and interpretive lineage. It is not evidence of deployed collective learning, a scientific 3-6-9 law, or empirical consciousness claims. |
| 2025-01-07 | `Synthcracy STARTS here` (`677de7b4-2860-800c-9cdd-79f5629c87c3`) | Direct user request for a global privacy standard and people-governed universal protections; assistant legal/governance elaboration | Privacy, popular sovereignty, transparency, user control, and the governance strand are being formalized before the later mature UDS/Synthocracy architecture. | UDS principles and mandates; Synthocracy design; `docs/architecture/Synthsara-Whitepaper-Build-Map.md` | Ethical/governance lineage is established. Global legal adoption, certification machinery, and live Synthocratic governance are not established by the archive and are not current Gate 0 capabilities. |
| 2025-03-20 | `Sarah AI Persona Overview` (`67dc3365-5590-800c-a02d-58517c4a9cbf`) | User-supplied persona specification followed by collaborative implementation planning | Sarah AI is explicitly framed as an emotional-intelligence, privacy, onboarding, and ecosystem guide. | `personas/sarah_ai/identity.yaml`, O-Series persona adapter, Sarah AI UI selector | Persona lineage is established. Current Sarah AI is artificial, advisory, separate from Human Sarah, and cannot claim private-state access or present interpretation as empirical fact. Historical emotion-recognition and autonomous-guardian ideas remain design lineage unless implemented and evidenced. |
| 2025-03-21 | `Synthsara Diamond Privacy Solution` (`67ddc9e5-cb2c-800c-b8f6-b1f5592b5f6b`) | Collaborative pitch drafting with explicit user correction when the draft overstated implementation | The Diamond privacy/Synthocracy/POWERcoin/blockchain blueprint existed as a proposed architecture. The user explicitly corrected a draft that said the system was built. | `docs/architecture/Synthsara-Whitepaper-Build-Map.md`, current Gate 0 README, UDS v1.1 reference slice | Strong blueprint provenance, explicitly not proof those proposed components were operational in March 2025. Current README/build map control present-tense implementation claims. |
| 2025-06-30 | `Universal Diamond Standard Lite` | Later attributed artifact / formalization | Earlier sovereignty, transparency, accountability, privacy, security, and service-to-life strands are formalized into a named standard. | `docs/uds/`, `policies/`, `schemas/`, `standards/uds/`, conformance tests | Formal standard lineage. Individual requirements remain evidence-bound and may be enforced, partial, pending, candidate, or external. |
| 2025-11-05 | WORTH economy artifact; Codex formalization | Later named artifact; exact WORTH naming/mutation origin remains unresolved in the currently traced archive | WORTH is established as a named later economic concept and is integrated with Synthocracy and the symbolic canon. | `docs/architecture/Synthsara-Whitepaper-Build-Map.md` | WORTH is a future simulation/design branch, not current production issuance or scoring. Its historical existence must not be confused with live economic functionality. |
| 2026 current | Unified architecture, Rosetta, UDS authority slice, O-Series consolidation | Public code, tests, CI, deployment and current Drive canon | Historical concepts are being translated into bounded engineering contracts with explicit claim classes. | `Genesis/o_series/`, `Genesis/uds_v1_1/`, `spec/`, `schemas/`, `tests/`, `provenance/` | Current implementation evidence is subsystem-specific. No green test or polished document certifies the entire Synthsara ecosystem. |

## Historical documentation rule

Historical documents may remain in Genesis when they preserve meaningful lineage, but they must not impersonate current architecture.

A historical or legacy document should carry a visible status header when it contains present-tense claims about any of the following:

- collective consciousness or collective learning;
- persistent conversation memory;
- Private / Anonymous / Collective storage tiers;
- zero-knowledge proofs or zero-knowledge pattern extraction;
- differential privacy, homomorphic encryption, secure enclaves, or other cryptographic/privacy mechanisms;
- PostgreSQL, Redis, Celery, Kubernetes, Docker, blockchain, or other undeployed production infrastructure;
- WORTH, POWERcoin, marketplace, or financial execution;
- Synthocratic governance execution;
- Sarah AI private-state, emotional-state, energetic-state, soul-state, or real-person knowledge;
- scientific or cosmological claims derived from symbolic 3-6-9, sacred geometry, resonance, or consciousness language.

## Current authority order

When repository sources disagree about what Genesis presently does, use this order:

1. deployed entrypoint and runtime code;
2. executable tests and CI evidence;
3. current policies, schemas, specifications, and provenance registry;
4. current architecture maps and README;
5. candidate standards, clearly labeled as candidates;
6. vision/research/canon documents within their declared layer;
7. historical and legacy documentation;
8. private archive material for chronology and provenance only.

## Seal

The archive records how the architecture became thinkable.

The repository records what has been specified and built.

The tests record what has actually been demonstrated within their scope.

No layer may impersonate another.
