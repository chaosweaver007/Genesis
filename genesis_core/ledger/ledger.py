"""Privacy-minimizing Witness Ledger for Genesis Kernel v0.1.

The ledger records policy decisions and consent state without raw prompts,
responses, hidden reasoning, or inferred emotional profiles.
"""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Iterable

from genesis_core.consent import ConsentState
from genesis_core.uds import UDSDecision


@dataclass(frozen=True, slots=True)
class WitnessEvent:
    """One audit event containing only constitutional metadata."""

    event_id: str
    request_id: str
    timestamp: str
    agent: str
    policy_version: str
    consent_version: str
    decision: str
    gates_checked: tuple[str, ...]
    violated_gates: tuple[str, ...]
    memory_written: bool
    ledger_export_mode: str
    model_invoked: bool
    provider: str | None
    user_visible_summary: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["gates_checked"] = list(self.gates_checked)
        data["violated_gates"] = list(self.violated_gates)
        return data


class InMemoryWitnessLedger:
    """Thread-safe metadata-only ledger suitable for the first vertical slice."""

    consent_version = "consent-0.1"

    def __init__(self) -> None:
        self._events: list[WitnessEvent] = []
        self._lock = Lock()

    def record(
        self,
        *,
        request_id: str,
        decision: UDSDecision,
        consent: ConsentState,
        model_invoked: bool,
        provider: str | None,
        memory_written: bool,
        user_visible_summary: str,
    ) -> WitnessEvent:
        event = WitnessEvent(
            event_id=str(uuid.uuid4()),
            request_id=request_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent="sarah-ai",
            policy_version=decision.policy_version,
            consent_version=self.consent_version,
            decision=decision.action,
            gates_checked=tuple(result.gate.value for result in decision.gate_results),
            violated_gates=decision.violated_gates,
            memory_written=memory_written,
            ledger_export_mode=consent.witness_ledger_export,
            model_invoked=model_invoked,
            provider=provider,
            user_visible_summary=user_visible_summary,
        )
        with self._lock:
            self._events.append(event)
        return event

    def list_events(self) -> tuple[WitnessEvent, ...]:
        with self._lock:
            return tuple(self._events)

    def extend(self, events: Iterable[WitnessEvent]) -> None:
        with self._lock:
            self._events.extend(events)
