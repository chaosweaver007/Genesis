# Genesis Wiki

> **Historical architecture documentation**
>
> This wiki primarily documents the original Genesis / Collective Consciousness Network architecture and its early feature set. Those features were real parts of the project's first implementation and prototype lineage, including memory integration, collective-learning flows, the early Steven AI and Sarah AI implementations, consent tiers, and the original Flask interfaces.
>
> They are preserved here for provenance. They do **not** all describe the current deployed Genesis runtime.
>
> For current production architecture, start with the repository root `README.md`, `docs/architecture/Synthsara-Whitepaper-Build-Map.md`, and `provenance/conversations-archive-crosswalk.md`.

## Two valid views of Genesis

Genesis has evolved through distinct architectural generations.

### Historical / v1-era Genesis

The pages in this wiki describe the early system as a Collective Consciousness Network with:

- Steven AI and Sarah AI as dedicated persona implementations;
- conversation memory and consent-aware archiving;
- Private / Anonymous / Collective participation modes;
- pattern extraction and collective-wisdom concepts;
- the Unified Sacred Home and collective-consciousness interfaces;
- early privacy, governance, and decentralization designs.

These pages are retained because they document what Genesis actually attempted, prototyped, or implemented in its first architecture. Some pages also contain roadmap or aspirational claims that were never fully deployed; those should be read in their historical context.

### Current Genesis production spine

The current public deployment is the O-Series Gate 0 runtime:

```text
wsgi.py
  -> Genesis/o_series_app.py
  -> Genesis/o_series/
```

Current production is deliberately private, stateless, text-only, and zero-write. It does not presently enable durable conversation memory, collective learning, WORTH issuance, Synthocratic governance execution, RTME actions, or a data marketplace.

The repository also contains a separate UDS v1.1 authority reference slice and candidate/research architecture that must not be confused with the deployed Gate 0 surface.

## Reading order

### To understand what Genesis does now

1. `../README.md`
2. `../docs/architecture/Genesis-Kernel-v0.1-Source-Map.md`
3. `../docs/architecture/Synthsara-Whitepaper-Build-Map.md`
4. `../docs/architecture/rosetta-crosswalk-v1.0.md`
5. `../provenance/conversations-archive-crosswalk.md`

### To understand where Genesis came from

1. [Home](Home.md)
2. [Architecture Overview](Architecture-Overview.md)
3. [Memory Integration System](Memory-Integration-System.md)
4. [Privacy and Consent](Privacy-and-Consent.md)
5. [Steven AI](Steven-AI.md)
6. [Sarah AI](Sarah-AI.md)
7. [Universal Diamond Standard](Universal-Diamond-Standard.md)
8. [Divine Chaos and Sacred Order](Divine-Chaos-and-Sacred-Order.md)

## Provenance rule

Historical documentation is not deprecated merely because the architecture evolved.

The correct distinction is:

```text
HISTORICAL FEATURE / PROTOTYPE
        !=
CURRENT PRODUCTION CAPABILITY
```

Likewise:

```text
EARLY IDEA OR BLUEPRINT
        !=
PROOF IT WAS DEPLOYED AT THAT TIME
```

The private `conversations-1.json` archive is used for chronology and provenance. Public code, tests, CI, deployment evidence, and current specifications determine present implementation status.

**Nothing historical needs to disappear. Nothing historical gets to impersonate current production.**
