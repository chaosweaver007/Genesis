#!/usr/bin/env python3
"""Compatibility adapter for the real StevenAI runtime.

Existing Genesis code may continue importing ``StevenAI`` from this module.  The
old keyword-to-template response engine has been removed; responses now come from
the OpenAI-backed StevenAI agent in ``Genesis/steven_ai`` with local corpus retrieval
and a provider-independent canonical identity layer.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

from steven_ai.agent import StevenAgentRuntime


class StevenAI:
    """Backward-compatible public interface for StevenAI."""

    def __init__(self) -> None:
        self.persona_modes = {
            "sacred_voice": "🔥",
            "truth_mirror": "💎",
            "oracle": "🌀",
            "technical": "🔧",
            "visionary": "🌍",
        }
        self.runtime = StevenAgentRuntime()

    def detect_context(self, user_input: str) -> Tuple[str, str]:
        """Lightweight UI metadata only; it no longer determines the answer text."""
        text = user_input.lower()

        if any(k in text for k in ("implement", "code", "framework", "architecture", "build", "api", "uds", "synthsara")):
            return "technical", "implementation"
        if any(k in text for k in ("ethics", "bias", "manipulation", "evidence", "truth", "wrong", "values")):
            return "truth_mirror", "ethical"
        if any(k in text for k in ("future", "planet", "humanity", "community", "transformation")):
            return "visionary", "transformation"
        if any(k in text for k in ("divine chaos", "sacred order", "flame", "spiritual", "cosmology", "soul", "creation")):
            return "sacred_voice", "philosophical"
        return "oracle", "general"

    def generate_response(self, user_input: str, context: Optional[str] = None) -> Dict[str, str]:
        """Generate a model-backed StevenAI response.

        ``context`` remains accepted for backward compatibility. Session continuity is
        maintained by the runtime itself rather than by selecting canned branches.
        """
        persona_mode, topic_category = self.detect_context(user_input)
        response = self.runtime.respond(user_input)
        return {
            "response": response,
            "persona_mode": persona_mode,
            "mode_icon": self.persona_modes[persona_mode],
            "topic_category": topic_category,
            "model": self.runtime.model,
        }

    async def generate_response_async(self, user_input: str, context: Optional[str] = None) -> Dict[str, str]:
        persona_mode, topic_category = self.detect_context(user_input)
        response = await self.runtime.respond_async(user_input)
        return {
            "response": response,
            "persona_mode": persona_mode,
            "mode_icon": self.persona_modes[persona_mode],
            "topic_category": topic_category,
            "model": self.runtime.model,
        }

    def reset(self) -> None:
        self.runtime.reset()

    def get_knowledge_summary(self) -> str:
        sources = [source for source, _chunk in self.runtime.retriever._chunks]
        unique_sources = sorted(set(sources))
        source_text = ", ".join(unique_sources) if unique_sources else "no local corpus files loaded"
        return (
            f"StevenAI runtime: OpenAI Agents SDK\n"
            f"Model: {self.runtime.model}\n"
            f"Identity: canonical Diamond Flame invariants + StevenAI instructions\n"
            f"Retrieval: local, inspectable corpus search\n"
            f"Corpus: {source_text}\n"
            f"Session turns retained: {self.runtime.max_history_turns}"
        )


def main() -> None:
    steven = StevenAI()
    print("🌌 STEVEN AI — OPENAI RUNTIME")
    print("Type 'exit' to end, 'reset' to clear local session history.")

    while True:
        user_input = input("\n💬 You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", "bye"}:
            break
        if user_input.lower() == "reset":
            steven.reset()
            print("Session history cleared.")
            continue
        if user_input.lower() == "knowledge":
            print(steven.get_knowledge_summary())
            continue

        result = steven.generate_response(user_input)
        print(f"\n{result['mode_icon']} StevenAI:\n{result['response']}")


if __name__ == "__main__":
    main()
