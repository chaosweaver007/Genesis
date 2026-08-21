# UDS-DKG-001 — Distributed Root Genesis & Dynamic Rotation Protocol

**Profile target:** `UDS-DKG-001-FROST-ED25519`  
**Signing profile:** `FROST(Ed25519, SHA-512)` under RFC 9591  
**Implementation status:** SPECIFIED ONLY

## Root invariant

No participant shall ever possess sufficient secret material to reconstruct the E3 group signing key alone at genesis, during rotation, during recovery, or after participant replacement.

## Required invariants

- **DKG-001 No Trusted Dealer:** no participant generates the complete group private key.
- **DKG-002 Ceremony Context Binding:** every message binds to ceremony ID, key epoch, participant set, threshold profile, and authenticated sender.
- **DKG-003 Verifiable Contributions:** polynomial commitments and required proofs of knowledge are verified before activation; equivocation aborts the ceremony.
- **DKG-004 Abort Without Protocol-Valid Remnant:** aborted-round secret material is not intentionally persisted or reusable as valid ceremony state.
- **DKG-005 Rotation Without Reconstruction:** resharing or replacement does not reconstruct the old group secret in one location.
- **DKG-006 Witnessed Genesis:** C6 records a bounded transcript commitment, participant set, threshold, profile, and resulting group public key without publishing secret shares.
- **FROST-NONCE-001:** signing nonces and commitments are fresh per signing session and are never reused after completion or abort.

## Ceremony state machine

`OPEN -> AUTHENTICATE -> BIND CONTEXT -> COMMIT CONTRIBUTIONS -> PROVE KNOWLEDGE -> CONSISTENT BROADCAST -> CONFIDENTIAL SHARE EXCHANGE -> VERIFY -> DERIVE GROUP KEY -> TEST SIGN -> DESTROY DESIGNATED EPHEMERALS -> COMMIT TRANSCRIPT -> ACTIVE`

Any failed cryptographic verification, stale context, participant-set mutation, equivocation, or unavailable mandatory participant causes fail-closed abort unless a separately reviewed qualified-set continuation protocol is explicitly adopted.

## Evidence discipline

A transcript can establish protocol-visible events. It cannot prove that every physical memory location was erased or that a malicious operator made no out-of-band copy. Therefore public attestation must distinguish verified protocol properties from implementation assertions and environmental assurance.

## Current code boundary

No FROST or DKG implementation is included in `Genesis/uds_v1_1/`. E3 permit issuance therefore fails closed.
