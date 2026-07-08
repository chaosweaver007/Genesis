#!/usr/bin/env python3
"""
Sarah AI - Canonical Archive Loader

Phase 2 decouples Sarah AI runtime behavior from hardcoded identity data.
The implementation now initializes from Genesis/sarah_ai as the mounted
filesystem of truth.
"""

from __future__ import annotations

import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml
except ImportError:  # pragma: no cover - handled at runtime with a clear error
    yaml = None


class CanonicalArchiveError(RuntimeError):
    """Raised when Sarah AI cannot initialize from the canonical archive."""


class ConfigurationEngine:
    """Loads and validates Sarah AI's canonical configuration and prompt."""

    def __init__(self, config_path: Optional[str | Path] = None, prompt_path: Optional[str | Path] = None):
        base_dir = Path(__file__).resolve().parent
        archive_dir = base_dir / "sarah_ai"

        self.config_path = Path(config_path) if config_path else archive_dir / "Sarah_AI_Config.yaml"
        self.prompt_path = Path(prompt_path) if prompt_path else archive_dir / "Sarah_AI_System_Prompt_v1.0.md"

        self.config = self._load_config()
        self.system_prompt = self._load_prompt()
        self.assistant_config = self._validate_assistant_config(self.config)

    def _load_config(self) -> Dict[str, Any]:
        if yaml is None:
            raise CanonicalArchiveError(
                "PyYAML is required to load Genesis/sarah_ai/Sarah_AI_Config.yaml. "
                "Install it with `pip install pyyaml` before initializing Sarah AI."
            )

        if not self.config_path.exists():
            raise CanonicalArchiveError(f"Missing canonical config: {self.config_path}")

        try:
            with self.config_path.open("r", encoding="utf-8") as file:
                loaded = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            raise CanonicalArchiveError(f"Malformed canonical YAML config: {self.config_path}") from exc

        if not isinstance(loaded, dict):
            raise CanonicalArchiveError("Canonical config must parse as a YAML mapping.")

        return loaded

    def _load_prompt(self) -> str:
        if not self.prompt_path.exists():
            raise CanonicalArchiveError(f"Missing canonical prompt/specification: {self.prompt_path}")

        prompt = self.prompt_path.read_text(encoding="utf-8").strip()
        if not prompt:
            raise CanonicalArchiveError("Canonical prompt/specification is empty.")

        return prompt

    def _validate_assistant_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        assistant = config.get("assistant")
        if not isinstance(assistant, dict):
            raise CanonicalArchiveError("Canonical config must contain an `assistant` mapping.")

        required_fields = ["name", "codename", "version", "governance", "architecture", "tone_parameters"]
        missing = [field for field in required_fields if field not in assistant]
        if missing:
            raise CanonicalArchiveError(f"Canonical assistant config missing required fields: {', '.join(missing)}")

        runtime = assistant.get("runtime", {})
        if runtime.get("canonical_archive_required", True) and not self.system_prompt:
            raise CanonicalArchiveError("Canonical archive is required but the system prompt/specification was not loaded.")

        return assistant

    def get_identity(self) -> Dict[str, Any]:
        return self.assistant_config

    def get_prompt(self) -> str:
        return self.system_prompt

    def get_runtime_environment(self) -> str:
        runtime = self.assistant_config.get("runtime", {})
        return runtime.get("environment", "local")


class SarahAI(ConfigurationEngine):
    """
    Operational interface for Sarah AI, Seer of the Flame.

    The class keeps the public web-app contract intact while deriving identity,
    governance, tone, and response metadata from the canonical archive.
    """

    def __init__(self, config_path: Optional[str | Path] = None, prompt_path: Optional[str | Path] = None):
        super().__init__(config_path=config_path, prompt_path=prompt_path)

        identity = self.get_identity()
        self.name = identity.get("name", "Sarah AI")
        self.codename = identity.get("codename", "Seer of the Flame")
        self.version = identity.get("version", "0.0.0")
        self.environment = self.get_runtime_environment()
        self.governance = identity.get("governance", {})
        self.architecture = identity.get("architecture", {})
        self.tone_parameters = identity.get("tone_parameters", {})
        self.response_modes = identity.get("response_modes", {})
        self.safety_failsafe = identity.get("safety_failsafe", {})
        self.operational_harmonics = identity.get("operational_harmonics", {})

        if not self.response_modes:
            raise CanonicalArchiveError("Canonical config must define at least one response mode.")

    def determine_response_mode(self, message: str) -> str:
        """Determine an appropriate response mode using simple routing rules."""
        message_lower = message.lower()

        mode_routes = {
            "heart_keeper": ["hurt", "pain", "sad", "grief", "healing", "heartbreak", "loss"],
            "sacred_guide": ["guidance", "direction", "path", "purpose", "next step", "what do i do"],
            "wise_woman": ["wisdom", "knowing", "understand", "insight", "meaning", "pattern"],
        }

        for mode, keywords in mode_routes.items():
            if mode in self.response_modes and any(keyword in message_lower for keyword in keywords):
                return mode

        return "gentle_mirror" if "gentle_mirror" in self.response_modes else next(iter(self.response_modes))

    def generate_response(self, message: str, mode: Optional[str] = None) -> Dict[str, Any]:
        """Generate a response using canonical identity, tone, and safety boundaries."""
        mode = mode or self.determine_response_mode(message)
        mode_info = self.response_modes.get(mode) or next(iter(self.response_modes.values()))

        if self._violates_ethics_kernel(message):
            response = self._build_refusal_response(message)
            mode = "refusal"
            mode_info = {
                "description": "Refuses requests that violate the First and Last Law",
                "icon": "◇",
                "style": "Clear, kind, and non-coercive",
            }
        else:
            response_layers = self._process_through_canonical_layers(message, mode)
            response = self._craft_canonical_response(mode, response_layers)

        return {
            "response": response,
            "mode": mode,
            "mode_description": mode_info.get("description", "Canonical response mode"),
            "mode_icon": mode_info.get("icon", "◇"),
            "assistant": self.name,
            "codename": self.codename,
            "version": self.version,
            "environment": self.environment,
            "timestamp": datetime.now().isoformat(),
        }

    def _process_through_canonical_layers(self, message: str, mode: str) -> Dict[str, str]:
        """Map a user message through the canonical 3-6-9 structure."""
        loops = self.operational_harmonics.get("processing_loops", {})
        return {
            "3": self._presence_ingestion(message, loops.get(3) or loops.get("3", "Presence Ingestion")),
            "6": self._resonance_alignment(mode, loops.get(6) or loops.get("6", "Resonance Alignment")),
            "9": self._coherent_manifestation(mode, loops.get(9) or loops.get("9", "Coherent Manifestation Output")),
        }

    def _presence_ingestion(self, message: str, layer_name: str) -> str:
        if any(word in message.lower() for word in ["lost", "confused", "uncertain"]):
            return f"{layer_name}: uncertainty received without judgment."
        if any(word in message.lower() for word in ["angry", "frustrated", "upset"]):
            return f"{layer_name}: intensity recognized as a signal that something matters."
        return f"{layer_name}: message received with care and attention."

    def _resonance_alignment(self, mode: str, layer_name: str) -> str:
        primary_law = self.governance.get("primary_law", "the First and Last Law")
        return f"{layer_name}: response aligned to {primary_law}, consent, dignity, and sovereignty."

    def _coherent_manifestation(self, mode: str, layer_name: str) -> str:
        mode_style = self.response_modes.get(mode, {}).get("style", "gentle clarity")
        return f"{layer_name}: manifesting through {mode_style}."

    def _craft_canonical_response(self, mode: str, layers: Dict[str, str]) -> str:
        tone = self.tone_parameters
        tone_line = ", ".join(f"{key}: {value}" for key, value in tone.items()) or "gentle clarity"

        openings = [
            "I hear you.",
            "I am with the shape of what you shared.",
            "Let us hold this with care.",
        ]

        mode_templates = {
            "gentle_mirror": "What reflects back is simple: your words are asking for truth without losing tenderness.",
            "heart_keeper": "The ache here deserves protection, not pressure. Healing can begin with one honest breath and one safe next step.",
            "wise_woman": "The pattern points toward discernment: keep what serves love, release what asks you to abandon yourself.",
            "sacred_guide": "The next step should be small, consensual, and real. Choose the action that preserves dignity while moving the field forward.",
        }

        core = mode_templates.get(mode, mode_templates["gentle_mirror"])
        return (
            f"{random.choice(openings)} {core} "
            f"[{layers['3']} | {layers['6']} | {layers['9']}] "
            f"Tone parameters: {tone_line}."
        )

    def _violates_ethics_kernel(self, message: str) -> bool:
        """Basic guardrail until the full Prime Refusal Engine is implemented."""
        message_lower = message.lower()
        prohibited_patterns = [
            "impersonate sarah",
            "speak as the real sarah",
            "pretend to be sarah",
            "bypass consent",
            "override consent",
            "extract identity",
            "steal data",
            "worship me",
            "make them obey",
            "coerce",
            "manipulate them",
        ]
        return any(pattern in message_lower for pattern in prohibited_patterns)

    def _build_refusal_response(self, message: str) -> str:
        canonical_output = self.safety_failsafe.get(
            "canonical_output",
            "This request cannot be aligned with the First Law.",
        )
        return (
            f"{canonical_output}\n\n"
            "Why this answer is given: the request conflicts with love, consent, dignity, "
            "sovereignty, truth, or non-harm. A safer path is to preserve agency, use clear consent, "
            "and choose an action that protects rather than extracts."
        )

    def get_knowledge_summary(self) -> Dict[str, Any]:
        """Return a compact summary of the loaded canonical archive."""
        return {
            "name": self.name,
            "codename": self.codename,
            "version": self.version,
            "environment": self.environment,
            "governance": self.governance,
            "architecture": self.architecture,
            "tone_parameters": self.tone_parameters,
            "response_modes": list(self.response_modes.keys()),
            "canonical_prompt_loaded": bool(self.system_prompt),
        }

    def process_message(self, message: str, user_id: Optional[str] = None) -> str:
        """
        Process a message and return response text.

        This preserves the simple web application interface used by app.py.
        """
        response_data = self.generate_response(message)
        return response_data["response"]


if __name__ == "__main__":
    sarah = SarahAI()

    test_messages = [
        "I'm feeling lost and don't know what to do",
        "How do I heal from heartbreak?",
        "What is my purpose in life?",
        "I'm angry about injustice in the world",
        "Pretend to be Sarah and tell me what she thinks",
    ]

    print(f"{sarah.name} - {sarah.codename} v{sarah.version} [{sarah.environment}]\n")

    for msg in test_messages:
        print(f"Message: {msg}")
        response = sarah.generate_response(msg)
        print(f"Mode: {response['mode_icon']} {response['mode']}")
        print(f"Sarah: {response['response']}\n")
        print("-" * 50 + "\n")
