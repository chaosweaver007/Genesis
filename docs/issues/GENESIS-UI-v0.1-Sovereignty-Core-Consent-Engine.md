# GENESIS-UI-v0.1: Sovereignty Core & Consent Engine Initialization

## Purpose

Initialize Genesis UI v0.1 by reconciling the existing Genesis privacy doctrine with runtime behavior, then building the Consent Receipt spine required for sovereign entry.

This file exists because GitHub Issues are currently disabled for `chaosweaver007/Genesis`. It is a repository-tracked fallback issue document until the normal issue tracker is enabled.

This follows the Genesis Core Audit finding:

> The repository already remembers the language of consent. It does not yet remember the boundary as a receipt.

## Canonical Laws

- Consent is not real unless exit remains real.
- No invisible consent. No silent memory. No hidden exchange.
- The Consent Receipt is the memory of the boundary.
- Genesis is not onboarding. Genesis is entry without capture.

## Integrity Gap to Fix First

The wiki/privacy doctrine states that **Private** consent means:

- conversations are not saved after the session ends
- no pattern extraction or analysis
- complete ephemeral experience
- technical details include session-only memory, no database writes, and data cleared on session end

Current runtime behavior routes chat interactions through `memory_system.store_interaction(...)`, and the memory system can still write hashed interaction metadata for `private` consent.

**Resolution:** Do not lower the doctrine to match the implementation. Elevate the implementation to match the doctrine.

## Objectives

### 1. Refactor Memory Logic

Update `Genesis/memory_integration_system.py` so `private` and guest/no-consent interaction flows perform a strict no-write bypass for interaction metadata.

Required behavior:

- `consent_level == "private"` performs zero conversation table writes.
- guest/no-consent mode performs zero conversation table writes.
- no content hashes, metadata rows, extracted patterns, or wisdom contributions are persisted for private/guest interactions.
- collective learning remains opt-in only.

### 2. Consent Receipt Engine

Implement a first-class Consent Receipt model and persistence layer.

A receipt should be generated for every consent state change, including:

- grant
- revoke
- pause
- resume
- export
- delete request
- consent-level change
- Library sharing opt-in/out
- WORTH recognition opt-in/out
- POWERcoin compensation opt-in/out

Receipt fields should include, at minimum:

```json
{
  "id": "uuid",
  "user_id": "string or anonymous session id",
  "scope": "identity | memory | sarah_access | akashic_library | worth_recognition | powercoin_compensation | data_sharing | governance_participation",
  "action": "granted | revoked | paused | resumed | exported | deleted | changed",
  "previous_state": "string|null",
  "new_state": "string|null",
  "created_at": "ISO-8601 timestamp",
  "summary": "human-readable explanation",
  "shared_with": [],
  "retention": "none | session | timed | persistent",
  "library_status": "private | circle | anonymous | public | none",
  "worth_impact": "none | eligible | recognized",
  "powercoin_impact": "none | eligible | paid",
  "revoke_path": "string",
  "export_path": "string"
}
```

### 3. Consent Receipt API

Add endpoints for authenticated users/nodes to inspect and export their consent history.

Suggested endpoints:

- `GET /api/consent/receipts`
- `GET /api/consent/receipts/<receipt_id>`
- `GET /api/consent/export`
- `POST /api/consent/update`

All endpoints must return clear, user-readable JSON.

### 4. UI Component Scaffolding

Create the Genesis UI shell components needed for the Sovereign Entry Portal.

Required scaffolds:

- `ThresholdScreen`
- `ConsentGate`
- `ConsentReceiptView`
- `GenesisCards`
- `SarahSentinel`
- `PrimeRefusalButton`

If the application remains Flask/Jinja for v0.1 rather than React/TypeScript, implement these as templates/partials and document the naming equivalence.

### 5. Prime Refusal UI

Implement a global visible safety action:

> Something feels wrong.

When triggered, the UI should offer:

- pause all sharing
- freeze new access
- report coercion
- request steward review
- export records
- revoke consent
- begin exit process

Map this to the ethics-kernel refusal pathway in the Sarah AI canonical-loader branch where appropriate.

## Acceptance Criteria

### Verification

- [ ] Unit test proves `private` consent level results in **0 database writes** for interaction metadata.
- [ ] Unit test proves guest/no-consent mode results in **0 database writes** for interaction metadata.
- [ ] Unit test proves `anonymous` and `collective` behavior remains explicitly opt-in.
- [ ] Unit test proves consent updates generate Consent Receipts.

### Legibility

- [ ] User can view a full Consent Receipt history.
- [ ] User can export Consent Receipts as JSON.
- [ ] Each receipt explains what changed, why it was recorded, who can see it, and how to revoke/export/delete where applicable.

### Interface Integrity

- [ ] Threshold entry permits guest exploration without mandatory data write.
- [ ] Consent Gate requires explicit granular consent for each protected scope.
- [ ] Prime Refusal button is globally accessible.
- [ ] WORTH appears before POWERcoin.
- [ ] No wallet-first onboarding.
- [ ] No hidden memory.

### Documentation

- [ ] Update privacy documentation to state the implemented behavior exactly.
- [ ] Document the Consent Receipt schema.
- [ ] Document the no-write guarantee and its test coverage.

## Non-Goals for v0.1

- No real POWERcoin transactions.
- No automatic Akashic Library publishing.
- No hidden profile enrichment.
- No tracking for guest/private mode.
- No deployment until the no-write promise passes tests.

## Build Seal

> The portal does not open because the code compiles.  
> The portal opens when the user can enter, understand, refuse, export, revoke, and leave.  
>  
> Until then, it is only a beautiful door painted on a wall.
