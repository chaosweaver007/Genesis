# CCTS-11.12 — Legacy Entrypoint Quarantine (Phase 1: Inventory)

Status: **AUDIT ONLY / NOT CONFORMANT**. This change does not quarantine
legacy services, implement an authorization service, or prove live behavior.

## Source inventory

- `wsgi.py` imports `Genesis/o_series_app.py` via `o_series_app`.
  `vercel.json` targets root `wsgi.py`.
- `Genesis/wsgi.py` imports `Genesis/app.py` via `app`.
- `Genesis/main.py` defines a separate Flask application with `/api/chat`.
- `Genesis/app.py` includes legacy Sarah/Steven/Collective chat, persistent
  interaction writes, WORTH balance mutation, and governance endpoints.

The legacy applications are **not proven publicly deployed** by repository
presence alone. Their deployment, data custody, and user dependencies must be
established before shutdown or migration.

## Two enforcement contracts

**Generation:** All externally reachable generation paths must have mandatory
ingress evaluation, trusted context conditioning, and output reflection.
Direct adapter access must not permit externally reachable bypass.

**Mutation:** Every protected memory, account, WORTH, or governance mutation
requires independently enforced identity, consent, authorization, transaction
integrity, and audit evidence. Text filters are not financial authorization.

## Phase 1 tests

`tests/test_ccts11_entrypoint_inventory.py` detects unexpected Flask app
instances, inventories sensitive legacy routes, and pins the configured Vercel
WSGI import and O-Series route delegation. These are **static regression
checks**. They cannot establish that a route executes its guard, that
production configuration matches this repository, or that direct internal
calls are authorized.

## Required follow-on work before conformance

1. Inventory actual deployed entrypoints and their traffic, data stores,
   owners, and export/migration obligations.
2. Add explicit default-deny legacy deployment policy without silently
   destroying existing data or user access.
3. Define route-by-route generation and mutation authorization contracts.
4. Instrument runtime tests: reject unauthorized actions and assert no
   generation, writes, transfers, or other protected side effects.
5. Test direct adapter calls, exception classes, policy corruption,
   rollback, replay, alternate WSGI imports, and policy-update races.
6. Independently verify deployment configuration and authorization isolation.

A passing static inventory test is **not** CCTS-11 compliance.
