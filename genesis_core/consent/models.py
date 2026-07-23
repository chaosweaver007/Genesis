"""Granular consent state for one Genesis request."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ConsentState:
    """Privacy-first consent defaults.

    Only current-response processing is enabled by default. Every durable or
    inferential use remains opt-in.
    """

    current_response_processing: bool = True
    session_history_retention: bool = False
    personal_memory_storage: bool = False
    emotional_state_inference: bool = False
    private_data_access: bool = False
    verified_third_party_consent: bool = False
    witness_ledger_export: str = "local_metadata_only"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
