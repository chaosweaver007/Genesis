# UDS-AUTH-001–006: Receiver-Side Permit Preview

**Status:** standalone offline functional proof only; **NOT** deployed or executable.
**Owner:** Genesis engineering, awaiting Architect review.
**Claim class:** engineering requirement.
**Reviewed:** October 31, 2026.
**Source:** Genesis/auth/broker.py, tests/test_auth_broker.py, Genesis/rtme_parser.py.
**Reference:** [RFC 8785 JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785).

## Exactly what this does

The broker binds the *entire* SYN-RD-002 draft-plan dictionary to SHA-256 of canonical JSON, including the original intention, success criterion, all steps and all existing fields. Unlike the compiler's non-private metadata_digest(), this digest deliberately binds raw plan data; never confuse those hashes.

It verifies a server-side, domain-separated HMAC-SHA256 permit against a trusted keyring, including issuer, key ID, the exact plan hash, phase-six step ID, authenticated subject, resource scope, effect class, requested authority, nonce and timestamps.

Consent and possessed authority are read from distinct trusted SQLite registries at the authorization commit boundary. The request is allowed only when requested_authority is a subset of granted_authority, which in turn is a subset of possessed_authority. The single recognized preview authority is draft:review. Both registries must hold unexpired, unrevoked entries.

An atomic SQLite BEGIN IMMEDIATE transaction checks grants, timestamps and revocation, inserts a single-use (issuer, nonce) entry under a unique constraint, then commits before returning ALLOW_PREVIEW. An already-used nonce returns DENY_REPLAY, including under concurrent requests to the same durable SQLite database.

## Critical safety and capability boundary

The current intent compiler produces **zero executable steps**. An E0 preview is not an action authorization. This broker refuses EVERY external effect class E1 or higher, even when signatures and consent are otherwise valid.

There is no public endpoint, no integration into wsgi.py or the production O-Series application, no network action, no payment, no external executor, and no authorization to act in the physical world. The permit issuer and grant-management method are trusted server/test APIs only and MUST NOT be exposed to browsers or untrusted services. No self-minted browser signatures are accepted.

The signer uses HMAC with a minimum 32-byte random server secret. Symmetric HMAC is appropriate only within co-trusted components, not public, independently verifiable capability exchange. Production key custody, rotation and Ed25519 remain future work.

## Canonicalization compatibility

The local canonicalizer is RFC 8785-compatible over its explicitly restricted I-JSON subset: strings, booleans, nulls, arrays, objects and safe integral JSON numbers. It recursively orders object keys using UTF-16 code units, preserves raw Unicode without normalization, and emits UTF-8. Floats, numbers above the exactly representable IEEE-754 integer range, unpaired surrogates, over-large or over-deep documents and unsupported Python types fail closed. **This is not a claim to support every RFC 8785 number representation.** Full JCS vector coverage is required before broader use.

## Bounded local decision receipt

Allowed or refused decisions expose only these fields:

- plan_digest: 64-character hex or null
- decision_class: ALLOW_PREVIEW or a specific DENY_* result
- policy_version: UDS-AUTH-PREVIEW-0.1
- timestamp_bucket: whole-hour epoch bucket
- zk_proof: null
- receipt_kind: UNSIGNED_LOCAL_DECISION_METADATA
- executed: false

No intent text, success criterion, subject ID, scope, nonce, key or signature is returned. A plan hash is still potentially linkable and can permit dictionary guesses for low-entropy text; treat receipts as potentially sensitive metadata. No signed Witness Ledger write, immutability, zero-knowledge proof or real-world effect is claimed.

## Limitations and next gates

- Identity and trusted consent issuance are external prerequisites, not solved here. The server must authenticate subjects and protect all administrative grant writes.
- This SQLite design covers only processes sharing one durable database, not a distributed fleet. Production needs shared linearizable storage, replay-state retention and fail-closed outage behavior.
- This prototype checks consent at **preview** commit time. A real executor needs independent, receiver-side checks at its own effectful commit boundary to close TOCTOU gaps.
- Do not log plan dictionaries or untrusted secrets, infer ethical compliance from signatures, or treat a permit as proof of another person's consent.
- The module does not interpret the intent's moral meaning, assess legal compliance, implement a secure vault, enforce user rate limits or conduct formal threat-model review.

## Validation

Run: python -m unittest tests.test_auth_broker tests.test_rtme_parser -v

The test matrix covers Python 3.11–3.13, JCS ordering and normalization, signature tampering, subject/scope/step substitution, revocation and expiry, 14 concurrent replay contenders, true full-plan hash binding, and mandatory E1 denial.

**Stacked PR requirement:** Review and merge compiler PR #39 before retargeting this PR to main. Do not add actual E1 permits or deploy this module without an independently reviewed action schema, authenticated consent, key custody, distributed replay state, executor-side effect/TOCTOU enforcement, and security testing.
