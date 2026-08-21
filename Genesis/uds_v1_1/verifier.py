"""Downstream execution-permit verification for the Hammer boundary."""

from __future__ import annotations

from datetime import datetime, timezone

from .canonical import canonical_json_bytes
from .models import CanonicalExecutionRequest, ExecutionPermit, parse_utc
from .signing import PermitSigner
from .state import AuthorizationStateRegistry, ExecutionJournalEntry


class ExecutionPermitVerifier:
    """Verify exact binding, freshness, audience, signature, and single use."""

    def __init__(self, *, signer: PermitSigner) -> None:
        self.signer = signer

    def authorize_execution(
        self,
        *,
        permit: ExecutionPermit,
        request: CanonicalExecutionRequest,
        expected_audience: str,
        idempotency_key: str,
        state: AuthorizationStateRegistry,
        now: datetime | None = None,
    ) -> tuple[str, ExecutionJournalEntry]:
        now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)

        if permit.max_executions != 1:
            raise PermissionError("Permit is not single-transition bound.")
        if permit.audience != expected_audience or request.audience != expected_audience:
            raise PermissionError("Permit audience mismatch.")
        if permit.authorized_action != request.action:
            raise PermissionError("Permit action mismatch.")
        if permit.resource_scope != request.resource:
            raise PermissionError("Permit resource mismatch.")
        if permit.effect_class != request.effect_class:
            raise PermissionError("Permit effect-class mismatch.")
        if permit.request_hash != request.request_hash():
            raise PermissionError("UDS-AUTH-004 request hash mismatch.")
        if permit.signature_algorithm != self.signer.algorithm:
            raise PermissionError("Permit signer algorithm mismatch.")
        if permit.broker_key_epoch != self.signer.key_epoch:
            raise PermissionError("Permit signer key epoch mismatch.")
        if parse_utc(permit.not_before) > now:
            raise PermissionError("Permit is not yet valid.")
        if parse_utc(permit.expires_at) <= now:
            raise PermissionError("Permit has expired.")

        if not self.signer.verify(canonical_json_bytes(permit.claims()), permit.broker_proof):
            raise PermissionError("Permit signature verification failed.")

        state.assert_current(
            consent_epoch=permit.consent_epoch,
            broker_key_epoch=permit.broker_key_epoch,
            authority_epoch=permit.authority_epoch,
            policy_digest=permit.policy_digest,
        )

        return state.begin_execution(
            permit_id=permit.permit_id,
            idempotency_key=idempotency_key,
            request_hash=permit.request_hash,
        )
