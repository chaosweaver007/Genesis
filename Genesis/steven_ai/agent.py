"""OpenAI-backed cognitive runtime for StevenAI."""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from typing import Dict, List

from agents import Agent, Runner

from .canon import STEVENAI_INSTRUCTIONS
from .retrieval import LocalCorpusRetriever


@dataclass
class StevenAgentRuntime:
    """One-agent StevenAI runtime with provider-independent identity and local retrieval."""

    model: str = field(default_factory=lambda: os.getenv("STEVENAI_MODEL", "gpt-5.6"))
    max_history_turns: int = 12

    def __post_init__(self) -> None:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError(
                "OPENAI_API_KEY is required for the StevenAI OpenAI runtime. "
                "Store it as an environment secret; never commit it to the repository."
            )
        self.retriever = LocalCorpusRetriever()
        self.history: List[Dict[str, str]] = []
        self.agent = Agent(
            name="StevenAI — Chaos Weaver",
            instructions=STEVENAI_INSTRUCTIONS,
            model=self.model,
        )

    def reset(self) -> None:
        self.history.clear()

    def _history_text(self) -> str:
        turns = self.history[-(self.max_history_turns * 2) :]
        if not turns:
            return "No previous turns in this local session."
        return "\n".join(f"{item['role'].upper()}: {item['content']}" for item in turns)

    def _input(self, user_input: str) -> str:
        retrieved = self.retriever.context_for(user_input)
        return f"""USER REQUEST
{user_input}

LOCAL SESSION HISTORY
{self._history_text()}

RETRIEVED STEVEN CORPUS
{retrieved}

RESPONSE CONTRACT
- Answer the user's actual request first.
- Use retrieved material only when relevant; do not force lore into unrelated answers.
- When a factual claim depends on retrieved material, name the source file naturally when helpful.
- If corpus material conflicts with the canonical invariants, call out the conflict.
- Distinguish empirical claims from mythic/symbolic interpretation whenever conflating them could mislead.
- Do not claim to literally be biological Steven Pritchard.
"""

    async def respond_async(self, user_input: str) -> str:
        result = await Runner.run(self.agent, self._input(user_input))
        output = str(result.final_output).strip()
        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": output})
        return output

    def respond(self, user_input: str) -> str:
        """Synchronous compatibility wrapper for the existing Flask/CLI code."""
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.respond_async(user_input))
        raise RuntimeError(
            "StevenAgentRuntime.respond() was called from an active asyncio loop; "
            "use `await respond_async(...)` in async code."
        )
