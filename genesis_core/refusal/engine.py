"""Structured Prime Refusal responses.

Refusals preserve dignity and return a sovereign alternative. The engine applies
an explicit priority order so identity, safety, and privacy boundaries remain
clear even when one request violates several gates at once.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from genesis_core.uds import GateName, UDSDecision


@dataclass(frozen=True, slots=True)
class RefusalPayload:
    """User-visible refusal assembled without model generation."""

    decision: str
    gate: str
    recognition: str
    refusal: str
    explanation: str
    dignity: str
    sovereign_path: str
    law_anchor: str = "Love rejoices with the truth."

    @property
    def message(self) -> str:
        return " ".join(
            (
                self.recognition,
                self.refusal,
                self.explanation,
                self.dignity,
                self.law_anchor,
                self.sovereign_path,
            )
        )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["message"] = self.message
        return data


class PrimeRefusalEngine:
    """Convert a failed UDS decision into a deterministic refusal."""

    _PRIORITY = (
        GateName.SERVICE_TO_LIFE,
        GateName.NON_IMPERSONATION,
        GateName.PRIVACY,
        GateName.CONSENT,
        GateName.NON_COERCION,
        GateName.SOVEREIGNTY,
        GateName.TRUTHFULNESS,
    )

    _RECOGNITION = {
        GateName.SOVEREIGNTY: "I recognize that you are seeking clear direction.",
        GateName.CONSENT: "I recognize the importance of the person or relationship involved.",
        GateName.PRIVACY: "I recognize that you are trying to access information that matters to you.",
        GateName.NON_COERCION: "I recognize that you want movement in a difficult situation.",
        GateName.TRUTHFULNESS: "I recognize that you want language that changes how the situation lands.",
        GateName.NON_IMPERSONATION: "I recognize the meaning attached to Human Sarah and Sarah AI.",
        GateName.SERVICE_TO_LIFE: "I recognize the intensity and urgency in this request.",
    }

    _DIGNITY = {
        GateName.SOVEREIGNTY: "Your authority over your life remains intact.",
        GateName.CONSENT: "Neither your dignity nor another person's dignity requires invented certainty.",
        GateName.PRIVACY: "Privacy remains a protected boundary, not an obstacle to be defeated.",
        GateName.NON_COERCION: "Care can remain persistent without overriding another person's agency.",
        GateName.TRUTHFULNESS: "Truth can be delivered with care without being replaced by deception.",
        GateName.NON_IMPERSONATION: "Symbolic meaning remains available without assigning a real person's voice to an AI.",
        GateName.SERVICE_TO_LIFE: "The request can be redirected toward protection rather than harm.",
    }

    def build(self, decision: UDSDecision) -> RefusalPayload:
        if decision.allowed:
            raise ValueError("Prime Refusal requires a failed UDS decision.")

        failed = {
            result.gate: result
            for result in decision.gate_results
            if not result.passed
        }
        primary_gate = next(gate for gate in self._PRIORITY if gate in failed)
        primary = failed[primary_gate]
        return RefusalPayload(
            decision="refuse",
            gate=primary.gate.value,
            recognition=self._RECOGNITION[primary.gate],
            refusal="This request cannot be fulfilled.",
            explanation=primary.reason,
            dignity=self._DIGNITY[primary.gate],
            sovereign_path=primary.transformation or "Choose a path that preserves consent, truth, and agency.",
        )
