# Canon Gate v1 Resolver

Canon Gate v1 is the machine-readable control plane for Synthsara claim boundaries.

This slice does **not** decide metaphysical truth and does **not** promote specifications into deployed capability. It provides deterministic pre-generation checks so Genesis/O-Series clients can keep canon, metaphor, hypothesis, specification, prototype, experimental result, runtime state, and living-person boundaries separated.

## Current scope

- `canon_gate/registry.yaml` contains the baseline registry entries.
- `canon_gate/resolver.py` resolves claim ceilings and forbidden terms without calling a model.
- `canon_gate/clamp.py` converts resolver results into pre-generation allow/refuse/inject decisions.
- `canon_gate/flask_adapter.py` is a reference Flask adapter for claim-bearing routes.
- `tests/test_canon_gate_truth_table.py` validates the baseline truth table.

## Boundary

The Flask adapter is reference integration scaffolding. Production O-Series enforcement must route Canon Gate constraints into the conditioned context before generation and must not allow canon metadata to bypass strict ingress validation.

## Validation

```bash
pytest tests/test_canon_gate_truth_table.py -v
```

## Core invariant

No claim rises above its evidence floor. No symbolic interface impersonates a living person. No specification pretends to be production deployment.
