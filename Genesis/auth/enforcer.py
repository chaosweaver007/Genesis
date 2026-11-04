"""Receiver-side UDS v1.1 reference authorization boundary.

This module is deliberately NOT registered as a public route. Genesis's live
O-Series node remains stateless and has no effectful executor. Integrations
must invoke ReceiverEnforcer.execute from the receiving executor itself,
rather than trusting browser consent, model output, or an API gateway flag.

The in-process epochs and revocations are reference-only; SQLite nonce state
works across processes sharing ONE database file, not across serverless nodes.
A production executor needs a centrally authoritative, atomic store and an
approved production signing profile. HMACDevelopmentSigner is E0/E1 test-only.
"""

from __future__ import annotations

import re
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Callable, Iterator

from uds_v1_1 import (
    AuthorizationStateRegistry,
    CanonicalExecutionRequest,
    ExecutionPermit,
    ExecutionPermitVerifier,
)
from uds_v1_1.canonical import canonical_json_bytes
from uds_v1_1.models import parse_utc

_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True)
class ActionOutcome:
    """Trusted executor's result and its independently computed result digest."""

    value: Any
    result_digest: str


@dataclass(frozen=True)
class ReceiverResult:
    """HTTP-ready reference result; receipt contains NO input or personal IDs."""

    status_code: int
    value: Any | None
    receipt: dict[str, str]


class AuthorizationDenied(PermissionError):
    def __init__(self, reason_code: str):
        super().__init__(reason_code)
        self.reason_code = reason_code


class SQLiteNonceStore:
    """Durably burn a nonce once using a unique SQLite key.

    This is suitable only when all receiver processes share one persistent
    SQLite filesystem. Do not use ephemeral serverless disks as global state.
    Nonces are intentionally not automatically pruned to preserve replay
    evidence across permit expiry and possible clock or backup restoration.
    """

    def __init__(self, path: str | Path):
        self.path = str(path)
        if not self.path or self.path == ":memory:":
            raise ValueError("Nonce store requires a persistent file path.")
        with sqlite3.connect(self.path, timeout=5.0) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS consumed_nonces "
                "(nonce TEXT PRIMARY KEY, expires_at TEXT NOT NULL)"
            )

    def consume(self, nonce: str, expires_at: str) -> bool:
        if not isinstance(nonce, str) or len(nonce) < 32 or len(nonce) > 256:
            raise AuthorizationDenied("PERMIT_MALFORMED")
        with sqlite3.connect(self.path, timeout=5.0) as conn:
            cursor = conn.execute(
                "INSERT INTO consumed_nonces (nonce, expires_at) VALUES (?, ?) "
                "ON CONFLICT(nonce) DO NOTHING",
                (nonce, expires_at),
            )
            return cursor.rowcount == 1


def _covers(revoked_scope: str, resource: str) -> bool:
    return revoked_scope == resource or (
        revoked_scope.endswith(".*") and resource.startswith(revoked_scope[:-1])
    )


class InProcessRevocations:
    """Single-process reference kill switch, permit and scope revocations.

    The lock spans the final check and local action, so a revocation published
    through this object cannot interleave with an already admitted action.
    This does not provide distributed commit-time consistency.
    """

    def __init__(self):
        self._lock = RLock()
        self._killed = False
        self._permit_ids: set[str] = set()
        self._scopes: set[str] = set()

    def kill(self):
        with self._lock:
            self._killed = True

    def revoke_permit(self, permit_id: str):
        with self._lock:
            self._permit_ids.add(permit_id)

    def revoke_scope(self, scope: str):
        with self._lock:
            self._scopes.add(scope)

    @contextmanager
    def admit(
        self, permit: ExecutionPermit, request: CanonicalExecutionRequest
    ) -> Iterator[None]:
        with self._lock:
            if self._killed or permit.permit_id in self._permit_ids or any(
                _covers(scope, request.resource) for scope in self._scopes
            ):
                raise AuthorizationDenied("SCOPE_REVOKED")
            yield


def _verifier_reason(exc: PermissionError) -> str:
    """Convert verifier errors to bounded public reason codes."""

    detail = str(exc).lower()
    if "signature" in detail or "signer" in detail:
        return "INVALID_SIGNATURE"
    if "expired" in detail:
        return "PERMIT_EXPIRED"
    if "not yet valid" in detail:
        return "PERMIT_NOT_YET_VALID"
    if "replay" in detail:
        return "NONCE_REPLAYED"
    if "epoch" in detail or "policy digest" in detail:
        return "STALE_AUTHORITY"
    if "mismatch" in detail or "single-transition" in detail:
        return "PERMIT_BINDING_MISMATCH"
    return "PERMIT_DENIED"


class ReceiverEnforcer:
    """Run a trusted local action only after exact permit verification.

    No caller may supply a boolean authorization bypass. The signer and issuer
    are pinned by the receiving service, never chosen from request payloads.
    """

    def __init__(
        self,
        *,
        verifier: ExecutionPermitVerifier,
        state: AuthorizationStateRegistry,
        nonce_store: SQLiteNonceStore,
        revocations: InProcessRevocations,
        audience: str,
        trusted_issuer: str,
        clock: Callable[[], datetime] | None = None,
    ):
        if not audience or not trusted_issuer:
            raise ValueError("Receiving audience and issuer must be pinned.")
        self.verifier = verifier
        self.state = state
        self.nonce_store = nonce_store
        self.revocations = revocations
        self.audience = audience
        self.trusted_issuer = trusted_issuer
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    @staticmethod
    def _deny(reason_code: str, *, status_code: int = 403) -> ReceiverResult:
        return ReceiverResult(
            status_code=status_code,
            value=None,
            receipt={
                "rule_id": "UDS-AUTH-001",
                "auth_status": "DENY",
                "reason_code": reason_code,
            },
        )

    def execute(
        self,
        *,
        permit: ExecutionPermit | None,
        request: CanonicalExecutionRequest,
        action: Callable[[], ActionOutcome],
    ) -> ReceiverResult:
        """Fail closed before ANY action; never include raw data in receipts.

        A consumed permit cannot be retried, including when the action fails.
        Any third-party side effects must have their own reconciliation path.
        """

        if permit is None:
            return self._deny("PERMIT_MISSING")
        if not isinstance(permit, ExecutionPermit) or not isinstance(
            request, CanonicalExecutionRequest
        ):
            return self._deny("PERMIT_MALFORMED")
        if permit.permit_schema_version != "UDS-EXEC-PERMIT-1.1":
            return self._deny("PERMIT_MALFORMED")
        if permit.issuer != self.trusted_issuer:
            return self._deny("ISSUER_MISMATCH")
        if not callable(action):
            return self._deny("INVALID_EXECUTOR")
        if not self.verifier.signer.supports_effect_class(request.effect_class):
            return self._deny("UNSUPPORTED_EFFECT_CLASS")

        try:
            # Verify signed claims BEFORE binding comparisons so tampering
            # is reported as signature failure, not as an ordinary scope error.
            if permit.signature_algorithm != self.verifier.signer.algorithm:
                raise AuthorizationDenied("INVALID_SIGNATURE")
            if not self.verifier.signer.verify(
                canonical_json_bytes(permit.claims()), permit.broker_proof
            ):
                raise AuthorizationDenied("INVALID_SIGNATURE")

            # Existing verifier binds the signature, exact canonical request,
            # audience, action, resource, time bounds and authority epochs.
            status, _ = self.verifier.authorize_execution(
                permit=permit,
                request=request,
                expected_audience=self.audience,
                idempotency_key=permit.permit_id,
                state=self.state,
                now=self.clock(),
            )
            # Reference verifier permits a same-key read of committed results.
            # This receiving action path is stricter: no second execution.
            if status != "STARTED":
                raise AuthorizationDenied("NONCE_REPLAYED")
            if not self.nonce_store.consume(permit.nonce, permit.expires_at):
                raise AuthorizationDenied("NONCE_REPLAYED")

            with self.revocations.admit(permit, request):
                # The last local check happens at the execution boundary.
                # A production distributed executor must make this atomic
                # with its durable state transition, not just sequential.
                now = self.clock()
                if parse_utc(permit.not_before) > now:
                    raise AuthorizationDenied("PERMIT_NOT_YET_VALID")
                if parse_utc(permit.expires_at) <= now:
                    raise AuthorizationDenied("PERMIT_EXPIRED")
                self.state.assert_current(
                    consent_epoch=permit.consent_epoch,
                    broker_key_epoch=permit.broker_key_epoch,
                    authority_epoch=permit.authority_epoch,
                    policy_digest=permit.policy_digest,
                )
                try:
                    outcome = action()
                    if not isinstance(outcome, ActionOutcome) or not isinstance(
                        outcome.result_digest, str
                    ) or not _DIGEST.fullmatch(outcome.result_digest):
                        raise ValueError("Executor did not supply a valid result digest.")
                    self.state.commit(
                        permit_id=permit.permit_id,
                        result_digest=outcome.result_digest,
                    )
                except Exception:
                    # Do not return raw exception messages or retry side effects.
                    return self._deny("EXECUTION_FAILED", status_code=500)

            return ReceiverResult(
                status_code=200,
                value=outcome.value,
                receipt={
                    "rule_id": "UDS-AUTH-001",
                    "auth_status": "PASS",
                    "reason_code": "AUTHORIZED",
                },
            )
        except AuthorizationDenied as exc:
            return self._deny(exc.reason_code)
        except PermissionError as exc:
            return self._deny(_verifier_reason(exc))
        except (ValueError, TypeError):
            return self._deny("PERMIT_MALFORMED")
        except sqlite3.Error:
            # Missing/unavailable shared replay registry is never an ALLOW.
            return self._deny("AUTH_STATE_UNAVAILABLE", status_code=503)
