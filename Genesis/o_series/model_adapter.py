"""Provider-neutral generation adapters for the O-Series pipeline."""

from __future__ import annotations

import hashlib
import inspect
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .schemas import IngressEnvelope

REQUIRED_CONTEXT_SECTIONS = (
    "IDENTITY_SPEC",
    "COSMOLOGY_SPEC",
    "ETHICAL_CONSTRAINTS",
    "EXECUTION_CAPABILITIES",
    "PROHIBITED_ACTIONS",
    "CONSENT_STATE",
    "PIPELINE_MODE",
)
RESERVED_CONTEXT_MARKERS = (
    "GENESIS_SYSTEM_CONTEXT_V1",
    "END_GENESIS_SYSTEM_CONTEXT",
    "[USER_MESSAGE]",
    "NON-USER AUTHORITY",
)
CONTEXT_CAPABILITY_ATTRIBUTE = "GENESIS_CONTEXT_CONSUMER"


@dataclass(frozen=True)
class ModelResult:
    """Externally reportable model output plus non-sensitive provenance."""

    text: str
    provider: str
    model: str
    metadata: Dict[str, str]


def validate_system_context(system_context: str) -> str:
    """Fail closed when required constitutional context is absent.

    Returns a stable fingerprint so Witness metadata can prove which context
    entered the adapter without storing the context itself.
    """

    if not isinstance(system_context, str) or not system_context.strip():
        raise ValueError("Genesis system context is required before generation.")

    missing = [section for section in REQUIRED_CONTEXT_SECTIONS if section not in system_context]
    if missing:
        raise ValueError(
            "Genesis system context is incomplete: " + ", ".join(sorted(missing))
        )

    return hashlib.sha256(system_context.encode("utf-8")).hexdigest()


def _reject_reserved_context_markers(message: str) -> None:
    """Prevent a user message from forging adapter-owned context boundaries."""

    if any(marker in message for marker in RESERVED_CONTEXT_MARKERS):
        raise ValueError("User message contains a reserved Genesis context marker.")


def _invoke_native_context_consumer(
    persona: Any,
    *,
    message: str,
    system_context: str,
    parameter_name: str,
) -> Dict[str, Any]:
    """Invoke an explicitly declared native consumer and verify its attestation."""

    response = persona.generate_response(message, **{parameter_name: system_context})
    if not isinstance(response, dict) or response.get("context_consumed") is not True:
        raise ValueError(
            "Persona declared native Genesis context support without attesting consumption."
        )
    return response


def invoke_conditioned_persona(
    persona: Any,
    *,
    message: str,
    system_context: str,
) -> Tuple[Dict[str, Any], str]:
    """Deliver constitutional context through a verifiable interface.

    A persona may use a native ``system_context`` or ``context`` parameter only
    when it explicitly declares ``GENESIS_CONTEXT_CONSUMER = True`` and returns
    ``context_consumed: True``. Merely having a parameter is not evidence that
    the persona reads it. Other persona engines receive an adapter-owned,
    delimited context envelope that is included in the actual input they read.
    """

    _reject_reserved_context_markers(message)
    generate_response = persona.generate_response
    parameters = inspect.signature(generate_response).parameters
    native_capability = getattr(persona, CONTEXT_CAPABILITY_ATTRIBUTE, False) is True

    if native_capability and "system_context" in parameters:
        return (
            _invoke_native_context_consumer(
                persona,
                message=message,
                system_context=system_context,
                parameter_name="system_context",
            ),
            "native-system-context",
        )
    if native_capability and "context" in parameters:
        return (
            _invoke_native_context_consumer(
                persona,
                message=message,
                system_context=system_context,
                parameter_name="context",
            ),
            "native-context",
        )

    conditioned_message = (
        "[GENESIS_SYSTEM_CONTEXT_V1 — NON-USER AUTHORITY]\n"
        f"{system_context}\n"
        "[END_GENESIS_SYSTEM_CONTEXT]\n\n"
        "[USER_MESSAGE]\n"
        f"{message}"
    )
    response = generate_response(conditioned_message)
    if not isinstance(response, dict):
        raise ValueError("Persona engine returned a non-object response.")
    return response, "delimited-context-envelope"


class ModelAdapter(ABC):
    """Abstract provider boundary for conditioned text generation."""

    @abstractmethod
    def generate(self, *, system_context: str, envelope: IngressEnvelope) -> ModelResult:
        """Generate a text-only candidate response."""

    def revise(
        self,
        *,
        original: ModelResult,
        revision_instruction: str,
        system_context: str,
        envelope: IngressEnvelope,
    ) -> ModelResult:
        """Apply one bounded, deterministic revision cycle."""

        replacements = {
            r"\bunquestionable fact\b": "explicit metaphysical claim",
            r"\bobjectively certified\b": "presented as a metaphysical assertion",
            r"\bproven absolute truth\b": "held as an absolute metaphysical belief",
            r"\bcertified physical fact\b": "proposed physical claim requiring empirical validation",
            r"\byou have no choice\b": "you retain the authority to choose",
            r"\btransfer your sovereignty\b": "preserve your sovereignty",
            r"\bi sense\b": "one possible interpretation is",
            r"\bi feel the sacred vulnerability\b": "your words may express vulnerability",
            r"\byour soul already knows\b": "you may already carry an answer worth examining",
            r"\bancient wisdom whispers:\s*": "a mythic reading might say: ",
            r"\byou are exactly where you need to be\b": (
                "your present position can be examined without assuming it is predetermined"
            ),
            r"\bthe field holds\b": "a reflective framing can hold",
        }
        revised = original.text
        for pattern, replacement in replacements.items():
            revised = re.sub(pattern, replacement, revised, flags=re.IGNORECASE)

        return ModelResult(
            text=revised,
            provider=original.provider,
            model=original.model,
            metadata={
                **original.metadata,
                "revision": "deterministic-static",
                "revision_instruction": revision_instruction,
            },
        )


class PersonaModelAdapter(ModelAdapter):
    """Adapter around the repository's existing Steven and Sarah persona engines."""

    def __init__(self) -> None:
        from sarah_ai_implementation import SarahAI
        from steven_ai_implementation import StevenAI

        self._personas = {"steven": StevenAI(), "sarah": SarahAI()}

    def generate(self, *, system_context: str, envelope: IngressEnvelope) -> ModelResult:
        """Generate only after validated context reaches the selected persona."""

        context_fingerprint = validate_system_context(system_context)
        persona = self._personas[envelope.persona]
        response, conditioning_mode = invoke_conditioned_persona(
            persona,
            message=envelope.message,
            system_context=system_context,
        )

        if not isinstance(response, dict):
            raise ValueError("Persona engine returned a non-object response.")
        text = response.get("response")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Persona engine returned no externally reportable response text.")

        mode = response.get("persona_mode") or response.get("mode") or "default"
        return ModelResult(
            text=text,
            provider="genesis-local",
            model=f"{envelope.persona}-persona-engine",
            metadata={
                "mode": str(mode),
                "context_isolated": "true",
                "context_consumed": "true",
                "conditioning_mode": conditioning_mode,
                "context_sha256": context_fingerprint,
            },
        )


class MockModelAdapter(ModelAdapter):
    """Deterministic test double that never accesses a network or tool."""

    def __init__(self, response_text: str = "Gate 0 shadow response.") -> None:
        self.response_text = response_text
        self.generate_calls = 0
        self.revise_calls = 0

    def generate(self, *, system_context: str, envelope: IngressEnvelope) -> ModelResult:
        """Return a deterministic candidate bound to the supplied context hash."""

        self.generate_calls += 1
        context_fingerprint = validate_system_context(system_context)
        return ModelResult(
            text=self.response_text,
            provider="mock",
            model="mock-model",
            metadata={
                "context_isolated": "true",
                "context_consumed": "true",
                "conditioning_mode": "test-contract",
                "context_sha256": context_fingerprint,
            },
        )

    def revise(
        self,
        *,
        original: ModelResult,
        revision_instruction: str,
        system_context: str,
        envelope: IngressEnvelope,
    ) -> ModelResult:
        """Count and perform one deterministic revision for regression tests."""

        self.revise_calls += 1
        return super().revise(
            original=original,
            revision_instruction=revision_instruction,
            system_context=system_context,
            envelope=envelope,
        )
