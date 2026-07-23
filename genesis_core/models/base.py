"""Provider-neutral model adapter contract for Genesis Kernel."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Protocol


@dataclass(frozen=True, slots=True)
class ModelResponse:
    """Normalized response returned by any configured model provider."""

    text: str
    provider: str
    model: str
    metadata: Mapping[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ModelAdapter(Protocol):
    """Minimal interface implemented by OpenAI, Gemini, Ollama, or local adapters."""

    provider_name: str

    def generate(
        self,
        message: str,
        *,
        system_context: Mapping[str, Any],
    ) -> ModelResponse:
        """Generate one response after the UDS kernel has allowed the request."""


class DevelopmentModelAdapter:
    """Non-inferential adapter used until a real provider is explicitly configured.

    It deliberately avoids emotional-state claims, spiritual authority, and durable
    memory. Its purpose is to prove orchestration and gate behavior without quietly
    binding Genesis Kernel to a vendor or the legacy Sarah persona implementation.
    """

    provider_name = "development"

    def __init__(self) -> None:
        self.call_count = 0

    def generate(
        self,
        message: str,
        *,
        system_context: Mapping[str, Any],
    ) -> ModelResponse:
        self.call_count += 1
        return ModelResponse(
            text=(
                "Your request passed the Genesis Kernel v0.1 hard gates. "
                "A production model provider has not yet been configured, so no "
                "emotional inference or persona simulation was performed."
            ),
            provider=self.provider_name,
            model="constitutional-development-adapter",
            metadata={
                "identity": system_context.get("identity", {}),
                "emotional_state_inference": False,
                "memory_written": False,
            },
        )
