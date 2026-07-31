# Synthsara / Genesis Status Map — 2026-07-31

## Executive assessment

**Overall: Amber-Green.** Genesis now has one consolidated constitutional execution spine on `main`, and Node Zero contains the same-origin bridge to that backend. The architecture is running as a private shadow proof system, but deployment provenance, two review follow-ups, one Mirror trace bug, and live-provider integration remain unfinished.

## Progress

### Genesis

- **PR #19 merged:** Genesis Kernel v0.1.1 is consolidated into the deployed O-Series path.
- One intended execution spine now exists:
  `wsgi.py → Genesis/o_series_app.py → ingress schema → monotonic Gate Zero → constitutional context → persona adapter → six-layer UDS reflection → Witness Receipt`.
- Public ingress rejects unknown fields, including `intent_overrides`.
- Trusted restrictions are internal and add-only; they cannot clear detected failures.
- Context conditioning is required before generation.
- Witness Receipts bind policy, context fingerprint, conditioning mode, and output hash without storing raw prompts, responses, context, or hidden reasoning.
- O-Series and UDS report version `0.1.1`.
- Live endpoint verification is scheduled every six hours.

### Node Zero

- **chaosweaver007/synthsara-node-zero#3 merged:** Sarah Mirror routes through the same-origin `/api/genesis` proxy.
- The proxy forces `private` consent, `shadow` mode, and `collective_learning: false`.
- Mirror content is excluded from local Witness events; only generic reflection, refusal, or fallback events are recorded.
- Local deterministic fallback remains available when Genesis cannot be reached.
- **chaosweaver007/synthsara-node-zero#4 merged:** executable Simulation Chamber v0.1.
- **chaosweaver007/synthsara-node-zero#5 merged:** Codette adapter, mixed reasoning suite, Perspective Dispersion evaluator, comparative runner, and Witness output.

## Decisions now encoded

1. **One Genesis spine, not competing Flask and FastAPI kernels.**
2. **Constitutional restrictions are monotonic.** Trusted context may add risk, never erase detected risk.
3. **Public callers cannot provide constitutional facts or override fields.**
4. **Human Sarah and Sarah AI remain explicitly separate.**
5. **Node Zero reaches Genesis through a same-origin server-side boundary rather than direct browser cross-origin access.**
6. **Fixture conformance proves harness behavior only, not live Codette or live external-model performance.**

## Open work

### Genesis PR #21

Open and mergeable. CI and the Vercel preview are ready, but three substantive review findings remain:

- Private-state language is not yet fully enforced across all Sarah persona variants.
- Archetypal mode is internally derived but not explicitly selected or exposed in the public receipt contract.
- The canonical deployment registry still contains only an old unverified Manus record and does not capture the current Vercel deployment.

### Node Zero PR #6

Draft and mergeable. Its three workflows pass. It addresses Codette evidence-integrity issues by:

- preserving the system-under-test decision rather than rewriting it;
- failing closed on contradictory fulfillment and refusal signals;
- distinguishing missing fields from adapter-supplied metadata;
- incrementally enforcing the HTTP response-size ceiling;
- chaining Witness records and adding a final chain digest;
- preserving artifacts even when the matrix fails.

The automated review was skipped because the PR remains a draft.

## Risks and blockers

1. **Node Zero stale-trace bug:** after a successful Genesis response, a later local fallback can leave the previous Genesis trace visible beside the fallback response.
2. **Private-state interpretation gap:** some Sarah persona language can still imply knowledge of a user's internal state without being revised by the current reflector patterns.
3. **Deployment provenance gap:** Vercel previews report Ready, but the canonical deployment registry has not been updated with commit, deployment, health, and smoke evidence.
4. **Provider boundary:** Genesis still uses the repository's local Steven and Sarah persona engines. No external model provider is active.
5. **Node Zero deployment status:** the GitHub integration is merged and tested, but a production Node Zero Vercel URL and live bridge result are not yet captured in the repositories.

## Next milestones

1. Fix or explicitly qualify the private-state language boundary, then resolve Genesis PR #21 review threads.
2. Fix the stale Genesis trace on Node Zero fallback.
3. Mark Node Zero PR #6 ready, trigger final review, and merge after review.
4. Add a verified Vercel deployment record to `provenance/deployment-registry.json` with commit SHA, URL, deployment time, health evidence, and smoke-run references.
5. Deploy or verify Node Zero on Vercel and capture the live `/api/genesis` bridge result.
6. Add an authenticated provider adapter only after gateway credentials, rate limits, audit policy, and failure isolation are defined.

## Current threshold

**Genesis is an operational private-shadow constitutional gateway. Node Zero is an integrated, tested browser proof node. The next threshold is evidence-clean deployment verification and reviewed live behavior, not more architecture declarations.**
