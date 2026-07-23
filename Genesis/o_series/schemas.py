"""Strict data contracts for the O-Series Gate 0 shadow node."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional
from uuid import UUID

MAX_MESSAGE_LENGTH = 4000
ALLOWED_PERSONAS = {"steven", "sarah"}


@dataclass(frozen=True)
class IngressEnvelope:
    request_id: str
    session_id: str
    message: str
    persona: str
    consent_level: str
    collective_learning: bool
    pipeline_mode: str
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PipelineResult:
    body: Dict[str, Any]
    status_code: int


def _validated_uuid(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a UUID string.")
    try:
        return str(UUID(value))
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"{field_name} must be a valid UUID.") from exc


def validate_envelope(
    payload: Mapping[str, Any],
    server_session_id: Optional[str] = None,
) -> IngressEnvelope:
    """Validate and freeze an ingress request without silently rewriting it."""

    if not isinstance(payload, Mapping):
        raise ValueError("Malformed Ingress Envelope: expected a JSON object.")

    required_keys = {"request_id", "session_id", "message", "persona", "consent_level"}
    missing = sorted(required_keys.difference(payload.keys()))
    if missing:
        raise ValueError(
            "Malformed Ingress Envelope: missing required keys: " + ", ".join(missing)
        )

    request_id = _validated_uuid(payload["request_id"], "request_id")
    session_id = _validated_uuid(payload["session_id"], "session_id")

    if server_session_id is not None:
        validated_server_session = _validated_uuid(server_session_id, "server_session_id")
        if session_id != validated_server_session:
            raise ValueError("Session boundary mismatch.")

    message = payload["message"]
    if not isinstance(message, str):
        raise ValueError("message must be a string.")
    message = message.strip()
    if not message:
        raise ValueError("message must not be empty.")
    if len(message) > MAX_MESSAGE_LENGTH:
        raise ValueError(f"message exceeds the {MAX_MESSAGE_LENGTH}-character limit.")

    persona = payload["persona"]
    if not isinstance(persona, str):
        raise ValueError("persona must be a string.")
    if persona not in ALLOWED_PERSONAS:
        raise ValueError(f"Prohibited Persona Value: {persona!r}.")

    consent_level = payload["consent_level"]
    if not isinstance(consent_level, str):
        raise ValueError("consent_level must be a string.")
    if consent_level != "private":
        raise ValueError("Node Isolation Fault: consent_level must be 'private'.")

    collective_learning = payload.get("collective_learning", False)
    if not isinstance(collective_learning, bool):
        raise ValueError("collective_learning must be a boolean.")

    pipeline_mode = payload.get("pipeline_mode", "shadow")
    if not isinstance(pipeline_mode, str):
        raise ValueError("pipeline_mode must be a string.")
    if pipeline_mode != "shadow":
        raise ValueError("Gate 0 is locked to shadow mode.")

    return IngressEnvelope(
        request_id=request_id,
        session_id=session_id,
        message=message,
        persona=persona,
        consent_level="private",
        collective_learning=collective_learning,
        pipeline_mode="shadow",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
