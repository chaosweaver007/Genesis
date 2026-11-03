# ADR — Architecture Evidence Lint Gate

**ID:** ADR-2026-11-03  
**Status:** Accepted for repository integration; CI and merge protection require separate verification  
**Date:** 2026-11-03  
**Scope:** Genesis repository architecture documentation only

## Decision

Introduce a dependency-free structural linter for newly created `ADR-*.md` and `SPEC-*.md` files beneath `docs/architecture/`. Require authors to record evidence, limits, safeguards, and how claims will be verified. Run the linter's own regression tests in a separate, unfiltered GitHub Actions job named `architecture-lint` on pull requests and pushes to `main`.

## Evidence Basis

The repository's existing `docs/architecture/Genesis-Kernel-v0.1-Source-Map.md` already distinguishes `ETHICAL LAW`, `ENGINEERING REQUIREMENT`, `MYTHOS / INTERPRETIVE LANGUAGE`, `HYPOTHESIS`, and `EMPIRICAL EVIDENCE`, while tying constitutional requirements to source files. The root README describes a stateless, private, text-only Gate Zero production boundary, metadata-only Witness Receipts, and limits on claims of implemented capabilities. The new gate turns these documentation disciplines into a repeatable structural check. The companion Python regression suite passed 11 tests in the local preparation environment on 2026-11-03; GitHub CI has not yet been run for these files.

## Claim Ceiling

Passing this linter proves only that recognized architecture records contain headings and non-placeholder explanations. It does not validate source authenticity, independent authorship, cryptographic integrity, the adequacy of an implementation safeguard, test success in production, security properties, compliance with UDS, or agreement between design documents and deployed behavior. Existing source-map documents are exempt from retroactive formatting changes. Records outside the `ADR-*.md` and `SPEC-*.md` filename patterns are out of scope.

## Implementation Safeguard

The GitHub Actions job runs with read-only repository permissions and Python's standard library. It does not alter runtime policies, mutate source records, publish private evidence, or provide additional authority to any actor. Code fences are excluded from documentation analysis; missing or placeholder-only sections cause the check to fail. The job uses unfiltered pull-request triggers so required checks do not hang when unrelated paths change. A true merge block requires an administrator to configure a branch ruleset after the check exists in GitHub.

## Verification Method

After adding the files to Genesis, run `python3 -m unittest discover -s tests -p 'test_lint_architecture.py' -v` and `python3 scripts/lint_architecture.py`. Open a pull request and verify the `architecture-lint` job reports success on GitHub. Temporarily remove the Claim Ceiling from a test ADR and confirm that CI reports failure, then restore it. Finally configure the `architecture-lint` job as a required status check in GitHub's `main` branch ruleset. No remote results are claimed until that workflow actually runs.
