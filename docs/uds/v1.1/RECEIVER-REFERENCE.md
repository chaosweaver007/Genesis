# UDS Receiver Reference Enforcement (proposed)

Status: **REFERENCE CODE ONLY — NOT A DEPLOYED EXECUTOR**

This slice adds 'Genesis/auth/enforcer.py', following Genesis's actual
capital-G Python source tree. It does not replace the existing UDS v1.1
broker, verifier, canonical request schema, or outcome-evidence rules.

## Receiving execution path

1. Server creates a 'CanonicalExecutionRequest' from the actual proposed
   operation. Neither LLM output nor a browser can select the trusted signer,
   issuer, audience, authorization state, or execution callable.
2. 'ReceiverEnforcer' checks the pinned issuer, schema version, allowed effect
   class, cryptographic proof, exact request hash, action, resource, audience,
   expiry, and current UDS authority epochs using the existing verifier.
3. A persistent SQLite unique key consumes the nonce. Any repeated permit or
   a different signed permit reusing that nonce is denied.
4. Under the in-process revocation guard, it checks expiry and epochs again
   immediately before calling the trusted executor.
5. The executor returns an 'ActionOutcome' with a domain-calculated digest.
   The reference journal marks the permit COMMITTED; receipts contain only
   bounded rule/authorization metadata.
6. A failed action consumes the nonce and cannot be blindly retried. Callers
   must reconcile indeterminate external effects separately.

## Explicit boundaries

- The current public O-Series app performs **no effectful actions or memory
  writes**. This reference receiver is NOT registered to a public route.
  An executor integration is still required for a real enforcement boundary.
- The existing 'HMACDevelopmentSigner' is for **E0/E1 isolated tests only**.
  No Ed25519 production key custody, DKG, FROST threshold signing, or E2/E3
  production authorization is implemented in this patch.
- The existing canonicalizer uses a **restricted JSON subset** compatible
  with its reference vectors, **not arbitrary RFC 8785 numeric input**.
  Floating-point values and non-ASCII object keys are rejected.
- SQLite consumption is atomic among processes sharing the **same durable
  database file**. It is not a distributed nonce service. Never use ephemeral
  serverless SQLite to imply global replay prevention.
- Kill switch, revoked permit IDs, revoked scopes, and current authority
  epochs are **in-process reference state**. Multi-node correctness requires a
  centrally authoritative durable store that couples revalidation with the
  effect transition; checking and then invoking a remote action is not
  cross-service TOCTOU-proof.
- The adapter handles typed 'ExecutionPermit' objects, not arbitrary
  unvalidated HTTP JSON. The supplied illustrative 'permit_v1.json' has a
  different shape and must not be silently treated as UDS v1.1.
- A RESULT_DIGEST is evidence supplied by the trusted executor. This reference
  does not promote a COMMITTED action to independently VERIFIED.

## Test command

    python -m unittest tests.test_uds_v1_1_authority tests.test_authorization_enforcer -v

The GitHub Actions receiver workflow executes this command on Python 3.11
when relevant files change.

## Next integration gate

Before deploying any receiver route, replace the development signer with an
approved profile, add a durable shared authorization/revocation backend, bind
the call to the REAL effectful endpoint and its own transaction boundary,
perform concurrency tests, and obtain an independent security review.
