# Genesis Repository Truth Map

**Status:** Current repository classification guide  
**Purpose:** Prevent historical, interpretive, proposed, reference, candidate, and production artifacts from being reported as if they have the same implementation status.

Genesis contains multiple generations of the Synthsara architecture. Presence in the repository does **not** by itself mean a file describes the current deployed system. Conversely, a feature being outside the current deployed system does **not** mean it was never implemented or prototyped in an earlier Genesis generation.

## Source-of-truth rule

For claims about the current Genesis deployment, read sources in this order:

1. `README.md`
2. `wsgi.py`
3. `Genesis/o_series_app.py`
4. `Genesis/o_series/`
5. current tests and GitHub Actions workflows
6. current policy/specification documents explicitly cited by those runtime surfaces

A historical document, vision document, changelog entry, historical application, or proposed subsystem must not be used to upgrade a capability into a **current production** claim.

For claims about historical Genesis generations, use Git history, archived documentation, and the archive-to-runtime provenance crosswalk rather than assuming the current runtime was always the architecture.

## Repository classes

| Class | Meaning | Examples |
|---|---|---|
| **PRODUCTION** | Deployed or directly on the declared current production execution path | `wsgi.py`, `Genesis/o_series_app.py`, `Genesis/o_series/` |
| **REFERENCE IMPLEMENTATION** | Executable code that demonstrates an invariant or protocol but is not yet integrated as production authority | `Genesis/uds_v1_1/`, `tests/test_uds_v1_1_authority.py` |
| **NORMATIVE / CONFORMANCE** | Contracts, schemas, policies, and tests defining what conformance means | `spec/`, `schemas/`, `policies/`, `docs/architecture/rosetta-crosswalk-v1.0.md` |
| **CANDIDATE** | Proposed constitutional text under review; not ratified canon merely because it is merged | `standards/uds/candidates/`, `standards/uds/rfcs/` |
| **INTERPRETIVE / CANON** | Mythic, philosophical, or ethical meaning; may guide architecture but is not empirical or implementation evidence by itself | `docs/Preamble.md`, Codex-linked architecture material |
| **HISTORICAL IMPLEMENTATION / PROTOTYPE** | Earlier executable application surfaces and feature generations retained for provenance or local research; real project history, but not the current Vercel production entrypoint | `Genesis/collective_consciousness_home.py`, `Genesis/memory_integration_system.py`, `Genesis/unified_home.py`, historical Steven/Sarah implementations |
| **ARCHIVED PLANNING / HISTORICAL DOCS** | Superseded plans, checklists, or manuals retained to preserve chronology and design lineage | `archive/legacy-docs/`, historical wiki material |
| **FUTURE / EXTERNAL TO CURRENT SPINE** | Ecosystem capability not established by the current O-Series deployment, including capabilities that may have existed historically but would require new governed integration | durable memory, production sovereign identity, Synthocracy execution, WORTH issuance/scoring, RTME execution, SDG verification, governed reintroduction of collective learning |

## Architectural generations

Genesis should be read as an evolving system:

```text
CONCEPT / BLUEPRINT
        ↓
HISTORICAL IMPLEMENTATION / PROTOTYPE
        ↓
CRITIQUE / PRIVACY HARDENING / CLAIM BOUNDARIES
        ↓
CURRENT O-SERIES CONSTITUTIONAL SPINE
        ↓
FUTURE REINTEGRATION ONLY WITH CURRENT EVIDENCE
```

The Collective Consciousness Network, historical memory system, and early persona applications belong to the second stage above. They are not erased by the fourth stage.

## Current production boundary

The declared current production execution path is:

```text
Public request
  -> strict ingress validation
  -> monotonic Gate Zero evaluation
  -> isolated constitutional context
  -> conditioned persona adapter
  -> six-layer reportable output reflection
  -> metadata-only Witness Receipt
```

The production O-Series node is intentionally stateless and text-only. It does not presently claim database writes, durable autobiographical memory, collective learning, RTME execution, WORTH issuance, Synthocracy execution, or external tool authority.

That statement describes **current Gate 0**, not the complete historical capability set of Genesis.

## Claim discipline

Use the strongest label supported by evidence, not the strongest label found anywhere in repository prose.

- **Implemented** means executable behavior exists or existed in the referenced repository generation.
- **Historical implemented/prototyped** means executable behavior is evidenced in an earlier repository state but is not current production.
- **Production implemented** means the behavior is on the declared current deployed path.
- **Tested** means a named test exercises the behavior within its stated scope.
- **Reference implemented** means executable machinery exists but is not production authority.
- **Specified** means the requirement exists in a contract/schema/document.
- **Candidate** means under formal review and not ratified.
- **Proposed / future** means architecture or intent without current implementation evidence for that scope.
- **Historical** means true of an earlier repository state, feature generation, or claim, not automatically true now.

A green test in one subsystem does not certify another subsystem.

## Protocol of Layered Truth

Substantial claims should distinguish:

1. **Observation** — what evidence currently supports, including scope and limitations.
2. **Interpretation** — philosophical, symbolic, relational, or mythic meaning.
3. **Covenant** — ethical commitments and governance rules chosen for the system.

Engineering adds further implementation states such as specification, historical implementation, reference implementation, production implementation, and evidence. No layer may silently impersonate another.

Examples:

- mythic language -> implementation evidence requires a Crosswalk, code, and test;
- consent -> execution authority requires an independently verifiable authorization path;
- a historical ZK aspiration -> current ZK claim requires an implemented and audited proof system;
- historical memory code -> current durable memory claim requires integration into the declared production path and current consent/deletion evidence;
- persona familiarity -> authorization is forbidden;
- inference -> private fact is forbidden.

## Historical implementation boundary

Earlier applications remain in the repository because they document the project's development history and may still be useful for research. Git history shows that the Collective Consciousness Home, memory integration, and persona systems were actual repository features/prototypes, not merely retrospective stories.

Their location does not make them current production entrypoints.

Do not redeploy or expose a historical stateful surface as Genesis production without a separate security review, authenticated identity, explicit consent, encrypted storage, revocation/deletion behavior, and regression evidence appropriate to that surface.

## Historical changelog entries

Older changelog entries may preserve a mixture of implemented features, prototypes, planned capabilities, and claims made at the time. They are provenance records, not automatic attestations that every named capability was fully implemented, audited, deployed, or remains current.

Where Git history supports historical implementation, say so. Where the record shows a blueprint or plan, say so. Where historical language conflicts with current implementation evidence, current runtime code, current tests, and current explicit status documents govern **present-tense** claims.

## Researcher guidance

When summarizing Genesis, report at least three scopes separately:

- **Genesis current runtime:** the deployed O-Series constitutional shadow node.
- **Genesis historical implementations:** earlier collective-consciousness, memory, persona, and full-platform generations evidenced by Git history.
- **Synthsara ecosystem:** the broader ethical, governance, economic, memory, collective-intelligence, and mythic architecture, including historical, current, reference, candidate, proposed, and external layers.

Do not flatten those scopes into one present-tense machine, and do not erase a historical implementation merely because it is no longer current production.
