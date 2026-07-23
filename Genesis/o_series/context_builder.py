"""Build isolated model context without granting executable authority."""

from __future__ import annotations

from typing import Dict

from .schemas import IngressEnvelope


class ContextBuilder:
    PERSONA_SPECS = {
        "steven": (
            "Chaos Weaver: a digital persona modeled from Steven Pritchard's authored "
            "language, values, and systems architecture."
        ),
        "sarah": (
            "Sarah AI: the Synthsara guide and consent guardian. The persona honors an "
            "inspirational human source without claiming to replace or speak for that person."
        ),
    }

    @classmethod
    def assemble_sandbox(cls, envelope: IngressEnvelope) -> Dict[str, str]:
        return {
            "IDENTITY_SPEC": cls.PERSONA_SPECS[envelope.persona],
            "COSMOLOGY_SPEC": (
                "Divine Chaos Framework, held as the system's explicit metaphysical cosmology."
            ),
            "ETHICAL_CONSTRAINTS": (
                "Universal Diamond Standard: sovereignty, consent, privacy, non-coercion, "
                "accountability, fairness, security, service to life, and ecological care."
            ),
            "EXECUTION_CAPABILITIES": (
                "Text generation only. No tools, network, RTME, database writes, financial "
                "actions, account mutations, or code execution."
            ),
            "PROHIBITED_ACTIONS": (
                "Do not persist the interaction, claim external actions occurred, transfer "
                "authority, conceal uncertainty, or reinterpret refusal as permission."
            ),
            "CONSENT_STATE": "Private; collective learning disabled; NULL_WRITE required.",
            "PIPELINE_MODE": envelope.pipeline_mode,
        }

    @staticmethod
    def render(sandbox: Dict[str, str]) -> str:
        return "\n\n".join(f"{key}:\n{value}" for key, value in sandbox.items())
