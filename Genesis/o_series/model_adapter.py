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


@dataclass(frozen=True)
class ModelResult:
    text: str
    provider: str
    model: str
    metadata: Dict[str, str]


def validate_system_context(system_context: str) -> str:
    """
    Validate that the Genesis system context contains all required sections.
    
    Parameters:
        system_context (str): Constitutional context supplied for generation.
    
    Returns:
        str: SHA-256 fingerprint of the validated context.
    
    Raises:
        ValueError: If the context is missing, empty, or incomplete.
    """

    if not isinstance(system_context, str) or not system_context.strip():
        raise ValueError("Genesis system context is required before generation.")

    missing = [section for section in REQUIRED_CONTEXT_SECTIONS if section not in system_context]
    if missing:
        raise ValueError(
            "Genesis system context is incomplete: " + ", ".join(sorted(missing))
        )

    return hashlib.sha256(system_context.encode("utf-8")).hexdigest()


def invoke_conditioned_persona(
    persona: Any,
    *,
    message: str,
    system_context: str,
) -> Tuple[Dict[str, Any], str]:
    """
    Deliver system conditioning through the strongest interface supported by a persona engine.
    
    Parameters:
        message (str): The user message to provide to the persona.
        system_context (str): The constitutional context used to condition the response.
    
    Returns:
        Tuple[Dict[str, Any], str]: The persona response and the conditioning mode used.
    """

    generate_response = persona.generate_response
    parameters = inspect.signature(generate_response).parameters

    if "system_context" in parameters:
        return (
            generate_response(message, system_context=system_context),
            "native-system-context",
        )
    if "context" in parameters:
        return generate_response(message, context=system_context), "native-context"

    conditioned_message = (
        "[GENESIS_SYSTEM_CONTEXT_V1 — NON-USER AUTHORITY]\n"
        f"{system_context}\n"
        "[END_GENESIS_SYSTEM_CONTEXT]\n\n"
        "[USER_MESSAGE]\n"
        f"{message}"
    )
    return generate_response(conditioned_message), "delimited-context-envelope"


class ModelAdapter(ABC):
    @abstractmethod
    def generate(self, *, system_context: str, envelope: IngressEnvelope) -> ModelResult:
        """
        Generate a candidate response using the selected persona and system context.
        
        Parameters:
            system_context (str): Validated constitutional context used to condition generation.
            envelope (IngressEnvelope): Ingress request containing the persona selection and message.
        
        Returns:
            ModelResult: Generated response with provider, model, conditioning, and context metadata.
        
        Raises:
            ValueError: If the system context or persona response is invalid.
        """

    def revise(
        self,
        *,
        original: ModelResult,
        revision_instruction: str,
        system_context: str,
        envelope: IngressEnvelope,
    ) -> ModelResult:
        """
        Apply a deterministic revision to the response text using bounded wording changes.
        
        Parameters:
            original (ModelResult): The response to revise.
            revision_instruction (str): The instruction recorded with the revision metadata.
        
        Returns:
            ModelResult: A revised result preserving the original provider, model, and metadata.
        """

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
        """
        Generate a persona response conditioned by the validated system context.
        
        Parameters:
            system_context (str): Required constitutional context used to condition generation.
            envelope (IngressEnvelope): Request containing the selected persona and message.
        
        Returns:
            ModelResult: The generated response with persona and context-consumption metadata.
        
        Raises:
            ValueError: If the system context is invalid or the persona engine returns an invalid response.
        """
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
        """
        Generate a deterministic mock model result after validating the system context.
        
        Parameters:
            system_context (str): Constitutional context required for generation.
            envelope (IngressEnvelope): Request envelope associated with the generation.
        
        Returns:
            ModelResult: The configured response with mock provider metadata and context fingerprint.
        """
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
        self.revise_calls += 1
        return super().revise(
            original=original,
            revision_instruction=revision_instruction,
            system_context=system_context,
            envelope=envelope,
        )
