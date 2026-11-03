# Genesis Architecture Records

Genesis treats **Ledger Before Spiral** as a documentation discipline for new architectural decisions and specifications.

The historical [Genesis Kernel v0.1 Source Map](Genesis-Kernel-v0.1-Source-Map.md) remains unchanged. That document identifies the trusted source boundary and distinguishes `ETHICAL LAW`, `ENGINEERING REQUIREMENT`, `MYTHOS / INTERPRETIVE LANGUAGE`, `HYPOTHESIS`, and `EMPIRICAL EVIDENCE`. This directory's new architecture records extend those distinctions to proposed changes without rewriting the existing source map.

## Record naming

Add new, substantive records anywhere beneath `docs/architecture/` using either:

- `ADR-0001-short-decision.md` — a decision, including tradeoffs and acceptance criteria.
- `SPEC-0001-short-system.md` — a specification, including observable contracts and relevant tests.

The CI checker examines all Markdown records matching `ADR-*.md` or `SPEC-*.md` recursively; it excludes `_templates/` and `templates/`. Arbitrarily named historical documents are not retroactively rewritten or rejected.

## Mandatory evidence sections

Every ADR and specification must contain headings with substantive explanations for:

1. **Evidence Basis** — original observations, authorship attribution, source-map link, repository paths, and/or cited test evidence. Label hypotheses and interpretation appropriately.
2. **Claim Ceiling** — what the evidence **does not** establish, including missing implementation or untested deployment boundaries.
3. **Implementation Safeguard** — the actual intended consent, authorization, privacy, safety, and rollback boundaries, as relevant.
4. **Verification Method** — explicit commands, test cases, independent review, or planned evidence needed to verify the implementation. A planned test is not a passed test.

Use the following headings literally:

```markdown
## Evidence Basis
Explain dated or versioned evidence and distinguish sourced requirements from inference.

## Claim Ceiling
State what has not been demonstrated or is outside the scope of the record.

## Implementation Safeguard
Describe operational boundaries that prevent the proposed change from bypassing policy.

## Verification Method
Name concrete tests or checks, and report PASS only when actually executed.
```

## What CI means

The dependency-free linter in `scripts/lint_architecture.py` verifies required sections are present with non-placeholder prose. It ignores fenced-code examples, supports nested subsections, and rejects missing safeguards. Its own regression suite runs on every workflow invocation.

**A passing architecture lint result does not prove the security, correctness, consent posture, authorship, or production deployment of a system.** It is a structural documentation check, separate from application tests, the runtime entrypoint inventory, and actual UDS compliance review.

Do **not** use a path-filtered `pull_request` trigger if this check is required by a branch ruleset: otherwise unaffected pull requests can wait indefinitely for a skipped status check. In GitHub Settings → Rules → Rulesets, require the `architecture-lint` job **after its first successful run** if you want a blocking merge gate.
