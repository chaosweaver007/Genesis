"""Deterministic Capability Broker for UDS v1.1."""

from __future__ import annotations

import secrets
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from typing import Callable
from uuid import uuid4

from .authority import AuthorityEvidenceResolver
from .canonical import canonical_json_bytes
from .models import AuthorityEvidence, CanonicalExecutionRequest, ConsentObject, ExecutionPermit
from .signing import PermitSigner
from .state import AuthorizationStateRegistry


class CapabilityBroker:
    """Issue narrowly bound permits after consent and authority both validate."""

    def __init__(
        self,
        *,
        signer: PermitSigner,
        issuer: str,
        permit_ttl_seconds: int = 120,
        permit_id_factory: Callable[[], str] | None = None,
        nonce_factory: Callable[[], str] | None = None,
    ) -> None:
        if permit_ttl_seconds <= 0:
            raise ValueError("permit_ttl_seconds must be positive.")
        self.signer = signer
        self.issuer = issuer
        self.permit_ttl_seconds = permit_ttl_seconds
        self._permit_id_factory = permit_id_factory or (lambda: f"urn:uds:permit:{uuid4()}")
        self._nonce_factory = nonce_factory or (lambda: secrets.token_hex(32))

    def issue_permit(
        self,
        *,
        consent: ConsentObject,
        authority_evidence: AuthorityEvidence,
        request: CanonicalExecutionRequest,
        state: AuthorizationStateRegistry,
        now: datetime | None = None,
    ) -> ExecutionPermit:
        now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        consent.validate_for(request, now=now)

        resolution = AuthorityEvidenceResolver.resolve(
            consent,
            authority_evidence,
            request,
            now=now,
        )
        if not resolution.valid or resolution.authority_epoch is None:
            raise PermissionError(resolution.reason)

        if not self.signer.supports_effect_class(request.effect_class):
            raise PermissionError(
                "No approved signer profile is available for this effect class."
            )

        state.assert_current(
            consent_epoch=consent.consent_epoch,
            broker_key_epoch=self.signer.key_epoch,
            authority_epoch=resolution.authority_epoch,
            policy_digest=consent.policy_digest,
        )

        not_before = now.isoformat().replace("+00:00", "Z")
        expires = (now + timedelta(seconds=self.permit_ttl_seconds)).isoformat().replace(
            "+00:00", "Z"
        )
        unsigned = ExecutionPermit(
            permit_id=self._permit_id_factory(),
            consent_id=consent.consent_id,
            subject_ref=consent.subject_ref,
            audience=request.audience,
            authorized_action=request.action,
            resource_scope=request.resource,
            effect_class=request.effect_class,
            request_hash=request.request_hash(),
            purpose_digest=consent.purpose_digest,
            consent_epoch=consent.consent_epoch,
            broker_key_epoch=self.signer.key_epoch,
            authority_epoch=resolution.authority_epoch,
            not_before=not_before,
            expires_at=expires,
            max_executions=1,
            nonce=self._nonce_factory(),
            policy_version=consent.policy_version,
            policy_digest=consent.policy_digest,
            permit_schema_version="UDS-EXEC-PERMIT-1.1",
            issuer=self.issuer,
            signature_algorithm=self.signer.algorithm,
            broker_proof="",
        )
        proof = self.signer.sign(canonical_json_bytes(unsigned.claims()))
        return replace(unsigned, broker_proof=proof)
