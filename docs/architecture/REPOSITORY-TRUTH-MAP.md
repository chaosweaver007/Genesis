# Genesis Repository Truth Map

**Status:** Current repository classification guide  
**Purpose:** Prevent historical, interpretive, proposed, reference, candidate, and production artifacts from being reported as if they have the same implementation status.

Genesis contains multiple generations of the Synthsara architecture. Presence in the repository does **not** by itself mean a file describes the current deployed system.

## Source-of-truth rule

For claims about the current Genesis deployment, read sources in this order:

1. `README.md`
2. `wsgi.py`
3. `Genesis/o_series_app.py`
4. `Genesis/o_series/`
5. current tests and GitHub Actions workflows
6. current policy/specification documents explicitly cited by those runtime surfaces

A historical document, vision document, changelog entry, legacy application, or proposed subsystem must not be used to upgrade a capability into a current production claim.

## Repository classes

| Class | Meaning | Examples |
|---|---|---|
| **PRODUCTION** | Deployed or directly on the declared production execution path | `wsgi.py`, `Genesis/o_series_app.py`, `Genesis/o_series/` |
| **REFERENCE IMPLEMENTATION** | Executable code that demonstrates an invariant or protocol but is not yet integrated as production authority | `Genesis/uds_v1_1/`, `tests/test_uds_v1_1_authority.py` |
| **NORMATIVE / CONFORMANCE** | Contracts, schemas, policies, and tests defining what conformance means | `spec/`, `schemas/`, `policies/`, `docs/architecture/rosetta-crosswalk-v1.0.md` |
| **CANDIDATE** | Proposed constitutional text under review; not ratified canon merely because it is merged | `standards/uds/candidates/`, `standards/uds/rfcs/` |
| **INTERPRETIVE / CANON** | Mythic, philosophical, or ethical meaning; may guide architecture but is not empirical or implementation evidence by itself | `docs/Preamble.md`, Codex-linked architecture material |
| **LEGACY / HISTORICAL RUNTIME** | Earlier application surfaces retained for provenance or local research; not the Vercel production entrypoint | `Genesis/collective_consciousness_home.py`, `Genesis/memory_integration_system.py`, `Genesis/unified_home.py`, legacy persona implementations |
| **ARCHIVED PLANNING** | Superseded plans/checklists retained only to preserve history | `archive/legacy-docs/` |
| **FUTURE / EXTERNAL** | Ecosystem capability not established by the current O-Series deployment | durable memory, production sovereign identity, Synthocracy execution, WORTH issuance/scoring, RTME execution, SDG verification, collective learning |

## Current production boundary

The declared production execution path is:

```text
Public request
  -> strict ingress validation
  -> monotonic Gate Zero evaluation
  -> isolated constitutional context
  -> conditioned persona adapter
  -> six-layer reportable output reflection
  -> metadata-only Witness Receipt
```

The production O-Series node is intentionally stateless and text-only. It does not claim database writes, durable autobiographical memory, collective learning, RTME execution, WORTH issuance, Synthocracy execution, or external tool authority.

## Claim discipline

Use the strongest label supported by evidence, not the strongest label found anywhere in repository prose.

- **Implemented** means executable behavior exists.
- **Production implemented** means the behavior is on the declared deployed path.
- **Tested** means a named test exercises the behavior within its stated scope.
- **Reference implemented** means executable machinery exists but is not production authority.
- **Specified** means the requirement exists in a contract/schema/document.
- **Candidate** means under formal review and not ratified.
- **Proposed / future** means architecture or intent without current implementation evidence.
- **Historical** means true of an earlier repository state or an earlier claim, not automatically true now.

A green test in one subsystem does not certify another subsystem.

## Protocol of Layered Truth

Substantial claims should distinguish:

1. **Observation** — what evidence currently supports, including scope and limitations.
2. **Interpretation** — philosophical, symbolic, relational, or mythic meaning.
3. **Covenant** — ethical commitments and governance rules chosen for the system.

Engineering adds further implementation states such as specification, reference implementation, production implementation, and evidence. No layer may silently impersonate another.

Examples:

- mythic language -> implementation evidence requires a Crosswalk, code, and test;
- consent -> execution authority requires an independently verifiable authorization path;
- a historical ZK aspiration -> current ZK claim requires an implemented and audited proof system;
- persona familiarity -> authorization is forbidden;
- inference -> private fact is forbidden.

## Legacy code boundary

Legacy applications remain in the repository because they document the project's development history and may still be useful for research. Their location does not make them production entrypoints.

Do not deploy or expose a legacy stateful surface as Genesis production without a separate security review, authenticated identity, explicit consent, encrypted storage, revocation/deletion behavior, and regression evidence appropriate to that surface.

## Historical changelog entries

Older changelog entries preserve what was described or intended at the time. They are provenance records, not automatic attestations that every named capability was fully implemented, audited, deployed, or remains current.

Where historical language conflicts with current implementation evidence, current runtime code, current tests, and current explicit status documents govern present-tense claims.

## Researcher guidance

When summarizing Genesis, report at least two scopes separately:

- **Genesis current runtime:** the deployed O-Series constitutional shadow node.
- **Synthsara ecosystem:** the broader set of ethical, governance, economic, memory, collective-intelligence, and mythic architectures, many of which remain proposed, external, historical, or reference-stage.

Do not flatten those scopes into one present-tense machine.
