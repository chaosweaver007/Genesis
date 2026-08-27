"""Immutable data contracts for the UDS v1.1 authorization path."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Tuple

from .canonical import sha256_jcs

EFFECT_CLASSES = {"E0", "E1", "E2", "E3"}


def parse_utc(timestamp: str) -> datetime:
    """Parse an ISO-8601 timestamp and normalize it to UTC."""

    if not isinstance(timestamp, str) or not timestamp:
        raise ValueError("Timestamp must be a non-empty ISO-8601 string.")
    normalized = timestamp[:-1] + "+00:00" if timestamp.endswith("Z") else timestamp
    try:
        value = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"Invalid ISO-8601 timestamp: {timestamp}") from exc
    if value.tzinfo is None:
        raise ValueError("Timestamp must include an explicit UTC offset.")
    return value.astimezone(timezone.utc)


def _scope_covers(grant: str, target: str) -> bool:
    """Return whether an exact or explicit wildcard grant covers a target."""

    if grant == target:
        return True
    if grant.endswith(".*"):
        prefix = grant[:-1]
        return target.startswith(prefix)
    return False


@dataclass(frozen=True)
class CanonicalExecutionRequest:
    action: str
    resource: str
    parameters: Mapping[str, Any]
    effect_class: str
    audience: str

    def __post_init__(self) -> None:
        if not self.action or not self.resource or not self.audience:
            raise ValueError("Action, resource, and audience are required.")
        if self.effect_class not in EFFECT_CLASSES:
            raise ValueError(f"Unsupported effect class: {self.effect_class}")
        self.request_hash()

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "audience": self.audience,
            "effect_class": self.effect_class,
            "parameters": dict(self.parameters),
            "resource": self.resource,
        }

    def request_hash(self) -> str:
        return sha256_jcs(self.to_dict())


@dataclass(frozen=True)
class ConsentObject:
    consent_id: str
    subject_ref: str
    controller_ref: str
    authorized_actions: Tuple[str, ...]
    resource_scopes: Tuple[str, ...]
    purpose_digest: str
    issued_at: str
    expires_at: str
    consent_epoch: int
    revocation_state: str
    allow_sub_delegation: bool
    policy_version: str
    policy_digest: str

    def validate_for(self, request: CanonicalExecutionRequest, *, now: datetime) -> None:
        if self.revocation_state != "ACTIVE":
            raise PermissionError("Consent is not active.")
        if self.consent_epoch < 1:
            raise PermissionError("Consent epoch must be positive.")
        if parse_utc(self.issued_at) > now:
            raise PermissionError("Consent is not yet valid.")
        if parse_utc(self.expires_at) <= now:
            raise PermissionError("Consent has expired.")
        if request.action not in self.authorized_actions:
            raise PermissionError("Consent does not authorize this action.")
        if not any(_scope_covers(scope, request.resource) for scope in self.resource_scopes):
            raise PermissionError("Consent does not cover this resource.")


@dataclass(frozen=True)
class AuthorityEvidence:
    evidence_id: str
    principal_ref: str
    resource_scope: str
    allowed_actions: Tuple[str, ...]
    authority_epoch: int
    not_before: str
    expires_at: str
    evidence_status: str
    evidence_digest: str

    def is_current(self, *, now: datetime) -> bool:
        return (
            self.evidence_status == "VERIFIED"
            and self.authority_epoch >= 1
            and parse_utc(self.not_before) <= now
            and parse_utc(self.expires_at) > now
        )

    def covers(self, request: CanonicalExecutionRequest) -> bool:
        return (
            request.action in self.allowed_actions
            and _scope_covers(self.resource_scope, request.resource)
        )


@dataclass(frozen=True)
class ExecutionPermit:
    permit_id: str
    consent_id: str
    subject_ref: str
    audience: str
    authorized_action: str
    resource_scope: str
    effect_class: str
    request_hash: str
    purpose_digest: str
    consent_epoch: int
    broker_key_epoch: int
    authority_epoch: int
    not_before: str
    expires_at: str
    max_executions: int
    nonce: str
    policy_version: str
    policy_digest: str
    permit_schema_version: str
    issuer: str
    signature_algorithm: str
    broker_proof: str

    def claims(self) -> dict[str, Any]:
        return {
            "permit_id": self.permit_id,
            "consent_id": self.consent_id,
            "subject_ref": self.subject_ref,
            "audience": self.audience,
            "authorized_action": self.authorized_action,
            "resource_scope": self.resource_scope,
            "effect_class": self.effect_class,
            "request_hash": self.request_hash,
            "purpose_digest": self.purpose_digest,
            "consent_epoch": self.consent_epoch,
            "broker_key_epoch": self.broker_key_epoch,
            "authority_epoch": self.authority_epoch,
            "not_before": self.not_before,
            "expires_at": self.expires_at,
            "max_executions": self.max_executions,
            "nonce": self.nonce,
            "policy_version": self.policy_version,
            "policy_digest": self.policy_digest,
            "permit_schema_version": self.permit_schema_version,
            "issuer": self.issuer,
            "signature_algorithm": self.signature_algorithm,
        }
