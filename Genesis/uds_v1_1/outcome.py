"""Evidence-tier enforcement for UDS-AUTH-006."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class EvidenceLevel(IntEnum):
    NONE = 0
    COMMITTED = 1
    OBSERVED = 2
    VERIFIED = 3


@dataclass(frozen=True)
class OutcomeEvidence:
    commitment_digest: str | None = None
    observed_state_digest: str | None = None
    independent_verification_digest: str | None = None

    def highest_supported_level(self) -> EvidenceLevel:
        if self.independent_verification_digest:
            return EvidenceLevel.VERIFIED
        if self.observed_state_digest:
            return EvidenceLevel.OBSERVED
        if self.commitment_digest:
            return EvidenceLevel.COMMITTED
        return EvidenceLevel.NONE


@dataclass(frozen=True)
class OutcomeRecord:
    permit_id: str
    request_hash: str
    result_digest: str
    evidence_level: EvidenceLevel
    evidence: OutcomeEvidence

    @classmethod
    def create(
        cls,
        *,
        permit_id: str,
        request_hash: str,
        result_digest: str,
        claimed_level: EvidenceLevel,
        evidence: OutcomeEvidence,
    ) -> "OutcomeRecord":
        supported = evidence.highest_supported_level()
        if claimed_level > supported:
            raise ValueError(
                f"Evidence promotion prohibited: claimed {claimed_level.name}, "
                f"supported {supported.name}."
            )
        return cls(
            permit_id=permit_id,
            request_hash=request_hash,
            result_digest=result_digest,
            evidence_level=claimed_level,
            evidence=evidence,
        )
