# Architecture Overview

> **Historical architecture redirect:** The previous contents of this page document an earlier implemented/prototyped Genesis generation: the Collective Consciousness Network with database-backed memory, Steven/Sarah persona systems, consent-aware collective interfaces, and related platform surfaces. Git history confirms those components existed in the repository and received feature work. The full historical page is preserved at `archive/legacy-docs/wiki/Architecture-Overview.md` for provenance.
>
> This status does **not** mean those features were imaginary or merely proposed. It means they are not all part of the current public production entrypoint.

## Current production architecture

For present-tense claims about Genesis, use:

1. [`README.md`](../README.md)
2. [`docs/architecture/REPOSITORY-TRUTH-MAP.md`](../docs/architecture/REPOSITORY-TRUTH-MAP.md)
3. [`docs/architecture/Genesis-Kernel-v0.1-Source-Map.md`](../docs/architecture/Genesis-Kernel-v0.1-Source-Map.md)
4. [`docs/architecture/rosetta-crosswalk-v1.0.md`](../docs/architecture/rosetta-crosswalk-v1.0.md)
5. [`provenance/conversations-archive-crosswalk.md`](../provenance/conversations-archive-crosswalk.md)

The declared production path is:

```text
wsgi.py
  -> Genesis/o_series_app.py
  -> strict ingress validation
  -> monotonic Gate Zero
  -> isolated constitutional context
  -> conditioned persona adapter
  -> six-layer reportable output reflection
  -> metadata-only Witness Receipt
```

The deployed O-Series node is deliberately stateless, private, and text-only. It does not presently enable durable database-backed conversation memory, collective learning, RTME execution, WORTH issuance/scoring, Synthocracy execution, or production ZK proofs.

## Broader ecosystem

Synthsara includes historical implementations, interpretive/canonical material, proposed systems, candidate standards, and reference implementations. Those layers remain part of the project record, but they must be classified by status rather than flattened into one present-tense runtime.

See the Repository Truth Map and archive crosswalk for the complete classification and lineage.
