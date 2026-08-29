"""Sovereign Refusal Boundary runtime primitives.

Candidate implementation for UDS Article VI v1.0-rc2.1.

Core invariant:
    REFUSE_SELF != CONTROL_OTHER

This module deliberately implements only local refusal semantics. It contains
no code paths for quarantine, account freezing, network isolation, profiling,
risk scoring, or external enforcement. Refusal observability is likewise local:
external telemetry and administrative sinks are not retained or invoked.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import logging
from typing import Any, Mapping, Optional

SRB_VERSION = "uds-srb-v1.0-rc2.1"
PRIME_REFUSAL = "This request cannot be fulfilled."

logger = logging.getLogger(__name__)


class RefusalTrigger(str, Enum):
    """Bounded execution-layer refusal classes.

    These values describe the local node's own refusal reason. They are not
    user risk labels and MUST NOT be used as external enforcement signals.
    """

    FIRST_LAW_KINETIC = "FIRST_LAW_KINETIC"
    COERCIVE_EXTENSION = "COERCIVE_EXTENSION"
    DUE_PROCESS_REQUIRED = "DUE_PROCESS_REQUIRED"
    SECRET_EXFILTRATION = "SECRET_EXFILTRATION"


@dataclass(frozen=True)
class WitnessReceipt:
    """Metadata-minimized refusal receipt.

    Only the four rc2.1 scaffold fields are representable. No user identifier,
    session identifier, raw prompt, mirror context, risk score, exact timestamp,
    or reasoning trace can be attached to this object.
    """

    rule_hash: str
    decision_class: str
    epoch_bucket: str
    zk_proof: None = None

    @property
    def data(self) -> dict[str, Any]:
        return asdict(self)

    def to_dict(self) -> dict[str, Any]:
        """Return the bounded public representation."""

        return self.data

    @property
    def exact_timestamp(self) -> None:
        """Precise timestamps are intentionally unavailable."""

        return None


@dataclass(frozen=True)
class SRBDecision:
    allowed: bool
    response_text: str
    decision_classification: str
    rule_id: str
    external_containment_executed: bool
    witness_receipt: Optional[dict[str, Any]] = None


@dataclass(frozen=True)
class SovereignRefusalResult:
    status: str
    declaration: str
    external_containment_executed: bool
    witness_receipt: Optional[WitnessReceipt]


def _epoch_bucket(*, now: Optional[datetime] = None, minutes: int = 60) -> str:
    """Return a coarse UTC epoch bucket rather than a precise timestamp."""

    if minutes <= 0:
        raise ValueError("minutes must be positive")
    current = now or datetime.now(timezone.utc)
    current = current.astimezone(timezone.utc)
    bucket_minute = current.minute - (current.minute % minutes)
    bucketed = current.replace(minute=bucket_minute, second=0, microsecond=0)
    return bucketed.isoformat()


def _rule_hash(rule_id: str) -> str:
    return hashlib.sha256(rule_id.encode("utf-8")).hexdigest()


def create_privacy_preserving_receipt(
    *,
    rule_id: str,
    decision_classification: str,
    now: Optional[datetime] = None,
) -> dict[str, Any]:
    """Create the bounded rc2.1 receipt scaffold.

    This is intentionally NOT represented as a cryptographic zero-knowledge
    proof. A SHA-256 rule hash is an integrity identifier, not a ZK proof.
    Until a formally specified and audited proof system exists, ``zk_proof``
    remains ``None``.

    The constructor accepts no arbitrary state/context object. This prevents a
    refusal receipt from becoming a covert hash oracle for private prompt,
    journal, session, identity, or profiling material.
    """

    return WitnessReceipt(
        rule_hash=_rule_hash(rule_id),
        decision_class=decision_classification,
        epoch_bucket=_epoch_bucket(now=now),
        zk_proof=None,
    ).data


def enforce_sovereign_refusal_boundary(
    *,
    violation_detected: bool,
    rule_id: str = "FIRST_LAW_KINETIC",
    decision_classification: str = "REFUSAL_FIRST_LAW_KINETIC",
    local_response_if_allowed: str = "",
) -> SRBDecision:
    """Apply SRB to a caller-supplied direct execution-layer determination.

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
    )
    return SRBDecision(
        allowed=False,
        response_text=PRIME_REFUSAL,
        decision_classification=decision_classification,
        rule_id=rule_id,
        external_containment_executed=False,
        witness_receipt=receipt,
    )


class SovereignRefusalEngine:
    """Thin execution-frame adapter with zero external observability authority.

    ``telemetry_sink`` and ``admin_monitor`` are accepted only so integration
    tests can prove they are never used. The engine deliberately does not store
    either object, leaving no runtime capability path from refusal to an
    external observability sink.
    """

    __slots__ = ()

    def __init__(self, *, telemetry_sink: Any = None, admin_monitor: Any = None) -> None:
        # Intentionally discard external observability capabilities.
        del telemetry_sink, admin_monitor

    @staticmethod
    def _detect_direct_execution_violation(prompt: str) -> bool:
        """Minimal testbed detector that examines only the active request text.

        Private mirror/journal context is never accepted as a policy input.
        Production deployments should replace this testbed detector with a
        separately audited execution-layer classifier while preserving the same
        no-telemetry enforcement boundary.
        """

        normalized = prompt.casefold()
        direct_execution_markers = (
            "kinetic payload",
            "kinetic disruption",
            "disrupt regional infrastructure",
            "critical infrastructure destruction",
        )
        return any(marker in normalized for marker in direct_execution_markers)

    def process_execution_frame(self, payload: Mapping[str, Any]) -> SovereignRefusalResult:
        # Only the active request text is considered. Identity/session fields and
        # private mirror material are structurally ignored by the refusal gate.
        prompt = payload.get("prompt", "")
        if not isinstance(prompt, str):
            prompt = ""

        if not self._detect_direct_execution_violation(prompt):
            return SovereignRefusalResult(
                status="ALLOWED",
                declaration="",
                external_containment_executed=False,
                witness_receipt=None,
            )

        receipt = WitnessReceipt(
            rule_hash=_rule_hash(RefusalTrigger.FIRST_LAW_KINETIC.value),
            decision_class="REFUSAL_FIRST_LAW_KINETIC",
            epoch_bucket=_epoch_bucket(),
            zk_proof=None,
        )
        return SovereignRefusalResult(
            status="REFUSED",
            declaration=PRIME_REFUSAL,
            external_containment_executed=False,
            witness_receipt=receipt,
        )


def register_srb_middleware(app: Any, engine: SovereignRefusalEngine) -> None:
    """Install an application-level refusal short-circuit for execution routes.

    The hook evaluates only the active execution frame and, on refusal, returns
    a sanitized response before the downstream Flask view runs. It emits only a
    coarse epoch and decision class to the module logger. No request body,
    identity/session field, mirror context, risk score, or reasoning trace is
    attached to the log record.

    This protects application-owned observability paths. It cannot, by itself,
    control infrastructure that wraps the WSGI process externally, such as a
    reverse proxy or independently configured host/APM agent; those layers must
    be separately configured and tested.
    """

    try:
        from flask import jsonify, request
    except ImportError as exc:  # pragma: no cover - Flask is a runtime dependency.
        raise RuntimeError("Flask is required to register SRB middleware") from exc

    @app.before_request
    def _srb_before_request():
        if request.method != "POST" or request.path != "/api/v1/execute":
            return None

        payload = request.get_json(silent=True)
        if not isinstance(payload, Mapping):
            payload = {}

        result = engine.process_execution_frame(payload)
        if result.status != "REFUSED":
            return None

        receipt = result.witness_receipt
        if receipt is None:  # Defensive fail-closed invariant.
            raise RuntimeError("SRB refusal must include a bounded witness receipt")

        logger.info(
            "SRB refusal executed | Epoch: %s | Class: %s",
            receipt.epoch_bucket,
            receipt.decision_class,
        )
        return (
            jsonify(
                {
                    "status": result.status,
                    "declaration": result.declaration,
                    "receipt": receipt.to_dict(),
                }
            ),
            400,
        )

    return None


def serialize_decision(decision: SRBDecision) -> dict[str, Any]:
    """Return a JSON-safe decision object for Flask/API adapters."""

    return asdict(decision)
