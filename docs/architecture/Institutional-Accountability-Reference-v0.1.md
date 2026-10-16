# Synthsara Institutional Accountability — Reference v0.1

Status: **REFERENCE_IMPLEMENTED / PUBLIC SERVICE NOT ENABLED**
Repository: Genesis | Owner: chaosweaver007
Canon relationship: Synthocracy, Universal Diamond Standard, Gate Zero, WORTH,
Sovereignty, Witness Ledger, restorative justice.
Oath: **Nobody Left Behind.**

## Contract

| Question | Constitutional invariant | Reference evidence | Boundary |
|---|---|---|---|
| Who is excluded? | Basic access to remedy cannot depend on money, WORTH, political status, or contribution history. | \`open_case\` accepts a server-authenticated participant and no financial/reputation input; tests enforce this. | No identity/accessibility or offline-intake deployment exists yet. |
| Who decides? | Claims cannot be judged by the accused institution or complainant; appeals require a different independent reviewer. | Independent review and appeal role/state checks. | Real reviewer appointment, legitimacy, human qualifications, and conflict declarations need external verification. |
| Who controls resources? | A complaint decision cannot itself move money, change identity, grant root, or bypass consent. | The kernel has no transfer/permission/tool capability. | Treasury authorization and independently operated budget controls remain separate, NOT DEMONSTRATED. |
| What remedies exist? | Decisions are contestable; restoration must be independently verified before closure; dismissals remain appealable. | Hash-chained receipts for open → review → decision → appeal → appeal decision → verification → closure. | Human due process, real restitution, deadlines, and durable case management are not live. |

## Run it

From the repository root, with Python 3.11+ and no third-party packages:

\`\`\`bash
python -m unittest tests.test_institutional_accountability -v
python examples/accountability_walkthrough.py
\`\`\`

The demo uses **synthetic actors and evidence fingerprints only**. It never
submits user narratives, accesses a real account, pays funds, or changes rights.

## Why this is separate from the deployed O-Series service

The Vercel O-Series application is private, text-only, stateless, and
\`NULL_WRITE\` for sensitive input. Deploying unauthenticated complaint storage
into that service would violate rather than implement Synthsara's constitution.
This first slice is an offline reference engine and CI conformance target.
No public route has been added.

## Threat model and claims discipline

* **Authentication:** \`Principal\` MUST come from a trusted identity/role provider.
  A public client may never assert its own roles or authenticated status. The
  reference kernel does not solve authentication.
* **Identity and privacy:** Private claimant/institution identifiers exist only
  in memory. Public receipts contain category, state, action, HMAC evidence
  commitments, timestamps, hashes, and opaque case IDs. Raw narratives and raw
  evidence are rejected; their unsalted SHA-256 values are not published.
* **No unilateral power:** Initial reviewers cannot be claimants or subjects;
  appeal reviewers cannot be initial reviewers; remedy attestations require a
  distinct auditor. The kernel never auto-executes sanctions or reparations.
* **Hash chain:** Events bind their sequence and predecessor; \`verify_chain\`
  optionally verifies an externally pinned head. A hash chain alone provides
  neither trusted timestamping nor signer authenticity; a compromised host can
  forge or truncate an internally held history.
* **Ephemeral state:** No durability is claimed. Restarting the process loses
  cases, actors, events, and the HMAC key. Do not use for real complaints.
* **Procedural justice:** An outcome marked \`REMEDY_VERIFIED\` denotes a trusted
  auditor's attestation of an evidence fingerprint, NOT independent proof that
  a real person has been restored.
* **No perfection claim:** "Indestructible" is not testable. Targets are
  survivability, revocation, auditability, repair, independent challenge, and
  graceful failure. Findings should be reported rather than hidden.

## Deployment gates (all mandatory before real people rely on this)

1. **Stable federation and human fallbacks:** secure self-sovereign identity,
   recovery, non-digital access, language/disability accessibility, anti-Sybil
   controls that do not turn lack of ID into loss of basic rights.
2. **Authenticated authority:** role grants with expiry, segregation of duties,
   conflict disclosures, rotation, independently reviewable delegation, UDS-0
   founder neutrality, explicit consent scopes.
3. **Confidential evidence handling:** encrypted evidence vault, least
   privilege, per-case access logs, selective disclosures, retention/deletion,
   key management, lawful handling of urgent safety reports.
4. **Durable, externally witnessed journal:** transactionally append-only
   records, external signed checkpoints, independent replicas/backups, disaster
   recovery drills, privacy-preserving export and revocation support.
5. **Real remedy executor:** separately authorized and testable actions for
   access restoration, correction, or compensation; no automatic transfers
   from AI output or tribunal labels; independent confirmation of completed
   remedy and human support.
6. **Justice and abuse operations:** published appeal deadlines, case triage,
   recusals, minority protections, hardship exceptions, emergency response,
   capacity for false reports and appeal flooding, independent ombuds function.
7. **Resource governance:** transparent budget ownership, quorum and voting
   rules, segregation of treasury privileges, no token purchase of constitutional
   rights, auditable distributions, independent external financial review.
8. **Evidence-based release:** adversarial security review, tests on deployed
   endpoints, load and availability targets, proven rollback, accessibility
   tests, data-deletion verification, incident playbooks, external audits, and
   public build-specific UDS claims only when evidenced.

Until these gates pass, this repository must label the work **reference**,
never "certified", "decentralized production governance", or "real-world
restoration".

## Traceability

Historical inputs:
- Feb 27, 2025: Synthocracy — participatory governance, rehabilitation, restorative justice.
- Mar 3, 2025: decentralized participation, identity, access, and local/global review concepts.
- Later UDS and WORTH specifications: consent, domain-limited authority,
  separated compensation, no root by founding status, Witness accountability.

This artifact is an executable first slice, not a restatement or replacement of
those constitutions.
