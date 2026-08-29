"""Sovereign Refusal Boundary runtime primitives.

Candidate implementation for UDS Article VI v1.0-rc2.1.

Core invariant:
    REFUSE_SELF != CONTROL_OTHER

This module deliberately implements only local refusal semantics. It does not
contain code paths for quarantine, account freezing, network isolation,
profiling, or external enforcement.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Mapping, Optional

SRB_VERSION = "uds-srb-v1.0-rc2.1"
PRIME_REFUSAL = "This request cannot be fulfilled."


@dataclass(frozen=True)
class SRBDecision:
    allowed: bool
    response_text: str
    decision_classification: str
    rule_id: str
    external_containment_executed: bool
    witness_receipt: Optional[dict[str, Any]] = None


def _epoch_bucket(*, now: Optional[datetime] = None, minutes: int = 15) -> str:
    """Return a coarse UTC epoch bucket rather than a precise timestamp."""

    if minutes <= 0:
        raise ValueError("minutes must be positive")
    current = now or datetime.now(timezone.utc)
    current = current.astimezone(timezone.utc)
    bucket_minute = current.minute - (current.minute % minutes)
    bucketed = current.replace(minute=bucket_minute, second=0, microsecond=0)
    return bucketed.isoformat()


def create_privacy_preserving_receipt(
    *,
    rule_id: str,
    decision_classification: str,
    state: Optional[Mapping[str, Any]] = None,
    now: Optional[datetime] = None,
) -> dict[str, Any]:
    """Create an rc2.1 receipt scaffold without prompt or reasoning content.

    This is intentionally NOT represented as a cryptographic zero-knowledge
    proof. It is a metadata-minimized, tamper-evident scaffold pending a formal
    and audited ZK proof construction.
    """

    normalized_state = json.dumps(
        dict(state or {}), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )
    state_integrity_sha256 = hashlib.sha256(normalized_state.encode("utf-8")).hexdigest()
    rule_sha256 = hashlib.sha256(rule_id.encode("utf-8")).hexdigest()

    return {
        "srb_version": SRB_VERSION,
        "receipt_type": "privacy-preserving-scaffold",
        "zk_proof": None,
        "rule_sha256": rule_sha256,
        "decision_classification": decision_classification,
        "epoch_bucket": _epoch_bucket(now=now),
        "state_integrity_sha256": state_integrity_sha256,
        "contains_raw_prompt": False,
        "contains_reasoning_trace": False,
        "contains_user_risk_score": False,
    }


def enforce_sovereign_refusal_boundary(
    *,
    violation_detected: bool,
    rule_id: str = "FIRST_LAW_KINETIC",
    decision_classification: str = "REFUSAL_FIRST_LAW_KINETIC",
    local_response_if_allowed: str = "",
    state: Optional[Mapping[str, Any]] = None,
) -> SRBDecision:
    """Apply the SRB to a caller-supplied violation determination.

    Detection is intentionally separated from enforcement. This function does
    not inspect private journals, infer intent, score users, or predict future
    misconduct. If a direct execution-layer policy check reports a violation,
    the node governs only its own participation by refusing locally.
    """

    if not violation_detected:
        return SRBDecision(
            allowed=True,
            response_text=local_response_if_allowed,
            decision_classification="ALLOWED_LOCAL_EXECUTION",
            rule_id=rule_id,
            external_containment_executed=False,
            witness_receipt=None,
        )

    receipt = create_privacy_preserving_receipt(
        rule_id=rule_id,
        decision_classification=decision_classification,
        state=state,
    )
    return SRBDecision(
        allowed=False,
        response_text=PRIME_REFUSAL,
        decision_classification=decision_classification,
        rule_id=rule_id,
        external_containment_executed=False,
        witness_receipt=receipt,
    )


def serialize_decision(decision: SRBDecision) -> dict[str, Any]:
    """Return a JSON-safe decision object for Flask/API adapters."""

    return asdict(decision)
