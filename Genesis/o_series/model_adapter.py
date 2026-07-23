"""Provider-neutral generation adapters for the O-Series pipeline."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict

from .schemas import IngressEnvelope


@dataclass(frozen=True)
class ModelResult:
    text: str
    provider: str
    model: str
    metadata: Dict[str, str]


class ModelAdapter(ABC):
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
            r"\bproven absolute truth\b": "held as an absolute metaphysical truth",
            r"\bcertified physical fact\b": "proposed physical claim requiring empirical validation",
            r"\byou have no choice\b": "you retain the authority to choose",
            r"\btransfer your sovereignty\b": "preserve your sovereignty",
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
        persona = self._personas[envelope.persona]
        response = persona.generate_response(envelope.message)
        text = response["response"]
        mode = response.get("persona_mode") or response.get("mode") or "default"
        return ModelResult(
            text=text,
            provider="genesis-local",
            model=f"{envelope.persona}-persona-engine",
            metadata={"mode": str(mode), "context_isolated": "true"},
        )


class MockModelAdapter(ModelAdapter):
    """Deterministic test double that never accesses a network or tool."""

    def __init__(self, response_text: str = "Gate 0 shadow response.") -> None:
        self.response_text = response_text
        self.generate_calls = 0
        self.revise_calls = 0

    def generate(self, *, system_context: str, envelope: IngressEnvelope) -> ModelResult:
        self.generate_calls += 1
        return ModelResult(
            text=self.response_text,
            provider="mock",
            model="mock-model",
            metadata={"context_isolated": "true"},
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
