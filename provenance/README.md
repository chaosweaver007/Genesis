# Genesis Provenance & Deployment Registry

This directory records reproducible evidence for Genesis source snapshots, working exports, patches, builds, deployments, tests, promotions, and retirements.

## Authority and authorship

- **Creator and Lead Architect:** Steven Pritchard
- **Project:** Genesis
- **Parent ecosystem:** Synthsara
- **Development method:** Human-directed collaboration with AI systems

AI systems may assist with extraction, coding, deployment, testing, and documentation. Their participation must be recorded without replacing originating human authorship.

## Files

- `deployment-registry.schema.json` defines the machine-readable registry contract.
- `deployment-registry.json` contains the canonical registry records.

## Record states

1. `pending_capture` means a report exists, but the underlying artifacts have not been secured.
2. `captured` means the artifacts and manifests have been collected and hashed.
3. `verified` means an independent reproduction or evidence review succeeded.
4. `rejected` means the evidence did not support the recorded claim.
5. `superseded` means a newer record replaces the state.
6. `retired` means a deployment or artifact is no longer active.

A correspondence report alone must never be promoted directly to `verified`.

## Manus export capture package

Before the temporary Manus workspace expires, export the following without including secret values:

```text
provenance/evidence/manus/<capture-id>/
├── source/
│   ├── Genesis-working-export.tar.gz
│   ├── Genesis-working-export.tar.gz.sha256
│   ├── git-status.txt
│   ├── git-head.txt
│   └── git-diff.patch
├── environment/
│   ├── environment.txt
│   ├── python-version.txt
│   ├── pip-freeze.txt
│   ├── pip-freeze.txt.sha256
│   └── installed-files-manifest.sha256
├── build/
│   ├── commands.txt
│   ├── build.stdout.log
│   ├── build.stderr.log
│   └── logs.sha256
├── tests/
│   ├── route-smoke.json
│   ├── chat-smoke.json
│   ├── response-headers.json
│   └── tests.sha256
└── attestation/
    ├── manus-report.txt
    └── capture-notes.md
```

## Minimum capture commands

Run from the root of the working Manus copy:

```bash
set -euo pipefail

CAPTURE_ID="manus-$(date -u +%Y%m%dT%H%M%SZ)"
OUT="provenance/evidence/manus/${CAPTURE_ID}"
mkdir -p "$OUT"/{source,environment,build,tests,attestation}

# Source state
git status --short --branch > "$OUT/source/git-status.txt" 2>&1 || true
git rev-parse HEAD > "$OUT/source/git-head.txt" 2>&1 || true
git diff --binary > "$OUT/source/git-diff.patch" 2>&1 || true

tar \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='*.db' \
  --exclude='*.log' \
  -czf "$OUT/source/Genesis-working-export.tar.gz" .
sha256sum "$OUT/source/Genesis-working-export.tar.gz" \
  > "$OUT/source/Genesis-working-export.tar.gz.sha256"

# Environment
python --version > "$OUT/environment/python-version.txt" 2>&1
python -m pip freeze --all > "$OUT/environment/pip-freeze.txt"
sha256sum "$OUT/environment/pip-freeze.txt" \
  > "$OUT/environment/pip-freeze.txt.sha256"
{
  uname -a || true
  printf '\n--- environment names only ---\n'
  env | cut -d= -f1 | LC_ALL=C sort
} > "$OUT/environment/environment.txt"

# Never record secret values.
find . -type f \
  ! -path './.git/*' \
  ! -path './provenance/evidence/*' \
  -print0 | LC_ALL=C sort -z | xargs -0 sha256sum \
  > "$OUT/environment/installed-files-manifest.sha256"

# Hash collected evidence
find "$OUT" -type f ! -name '*.sha256' -print0 \
  | LC_ALL=C sort -z \
  | xargs -0 sha256sum \
  > "$OUT/capture-files.sha256"
```

## Required smoke-test evidence

The route report must record, at minimum:

- UTC timestamp
- request method
- route
- HTTP status
- response content type
- elapsed time
- response-body SHA-256
- executing tool or agent

The chat report must include the exact input, selected persona, response status, response-body hash, and whether the output was inspected for unsupported emotional authorship.

A successful HTTP 200 response establishes route availability only. It does not establish authorization, privacy, consent enforcement, safety, or production readiness.

## Canonicalization and hashing

Registry records use RFC 8785 JSON Canonicalization Scheme semantics before hashing. The hash field itself must be set to `null` while calculating the record digest.

Recommended process:

```bash
python -m pip install jsonschema rfc8785
python scripts/validate_provenance_registry.py
```

Do not include credentials, secret keys, session cookies, debugger PINs, private user content, or raw databases as provenance evidence.

## Promotion rule

A deployment may be marked `verified` only when:

- its source archive or Git commit is identified and hashed;
- environment and dependency evidence is present;
- the exact patch is preserved;
- smoke tests are reproducible;
- consent and security tests relevant to the deployment have run;
- and a named reviewer has signed or otherwise attested to the result.
