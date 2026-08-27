"""Deterministic authority-evidence resolution for UDS-AUTH-002."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .models import AuthorityEvidence, CanonicalExecutionRequest, ConsentObject


@dataclass(frozen=True)
class AuthorityResolution:
    valid: bool
    reason: str
    authority_epoch: int | None = None


class AuthorityEvidenceResolver:
    """Prove that the consenting principal actually possesses scoped authority."""

    @staticmethod
    def resolve(
        consent: ConsentObject,
        evidence: AuthorityEvidence,
        request: CanonicalExecutionRequest,
        *,
        now: datetime,
    ) -> AuthorityResolution:
        if evidence.principal_ref != consent.subject_ref:
            return AuthorityResolution(False, "Authority principal does not match consent subject.")
        if not evidence.is_current(now=now):
            return AuthorityResolution(False, "Authority evidence is not current and verified.")
        if not evidence.covers(request):
            return AuthorityResolution(False, "Authority evidence does not cover action/resource.")
        return AuthorityResolution(True, "Authority evidence verified.", evidence.authority_epoch)
