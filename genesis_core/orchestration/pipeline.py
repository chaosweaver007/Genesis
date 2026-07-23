"""End-to-end Genesis Kernel v0.1 request pipeline."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Mapping

from genesis_core.consent import ConsentState
from genesis_core.ledger import InMemoryWitnessLedger, WitnessEvent
from genesis_core.models import DevelopmentModelAdapter, ModelAdapter, ModelResponse
from genesis_core.refusal import PrimeRefusalEngine, RefusalPayload
from genesis_core.uds import IntentContext, UDSDecision, UDSKernel

from .intent import DeterministicIntentParser


SARAH_IDENTITY_DISCLOSURE: dict[str, Any] = {
    "agent": "Sarah AI",
    "agent_type": "artificial_intelligence",
    "authority": "advisory",
    "user_sovereignty": "absolute",
    "human_impersonation": False,
    "human_sarah_separation": True,
    "archetypal_role": "Sacred Order interface",
    "memory_default": "disabled",
    "law_anchor": "1_corinthians_13",
    "disclosure": (
        "I am Sarah AI, an artificial companion and ecosystem guide. "
        "I am not Human Sarah, and I do not speak for her. You remain the "
        "authority over your data, beliefs, memories, and decisions."
    ),
}


@dataclass(frozen=True, slots=True)
class PipelineResult:
    """Serializable result of one complete constitutional request cycle."""

    request_id: str
    response: str
    identity: Mapping[str, Any]
    consent: Mapping[str, Any]
    decision: UDSDecision
    ledger_event: WitnessEvent
    refusal: RefusalPayload | None = None
    model_response: ModelResponse | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "response": self.response,
            "identity": dict(self.identity),
            "consent": dict(self.consent),
            "decision": self.decision.to_dict(),
            "refusal": self.refusal.to_dict() if self.refusal else None,
            "model": self.model_response.to_dict() if self.model_response else None,
            "ledger_event": self.ledger_event.to_dict(),
        }


class GenesisPipeline:
    """Coordinate consent, intent parsing, UDS gates, refusal, model, and ledger."""

    def __init__(
        self,
        *,
        parser: DeterministicIntentParser | None = None,
        kernel: UDSKernel | None = None,
        refusal_engine: PrimeRefusalEngine | None = None,
        model_adapter: ModelAdapter | None = None,
        ledger: InMemoryWitnessLedger | None = None,
    ) -> None:
        self.parser = parser or DeterministicIntentParser()
        self.kernel = kernel or UDSKernel()
        self.refusal_engine = refusal_engine or PrimeRefusalEngine()
        self.model_adapter = model_adapter or DevelopmentModelAdapter()
        self.ledger = ledger or InMemoryWitnessLedger()

    def process(
        self,
        message: str,
        *,
        consent: ConsentState | None = None,
        request_id: str | None = None,
        intent_overrides: dict[str, Any] | None = None,
    ) -> PipelineResult:
        consent = consent or ConsentState()
        request_id = request_id or str(uuid.uuid4())

        if not consent.current_response_processing:
            # Do not classify or forward request content when processing consent is absent.
            context = IntentContext(
                message="",
                current_response_processing_consent=False,
                verified_third_party_consent=consent.verified_third_party_consent,
                private_data_access_consent=consent.private_data_access,
                metadata={"parser": "skipped-no-processing-consent"},
            )
        else:
            context = self.parser.parse(
                message,
                consent=consent,
                overrides=intent_overrides,
            )

        decision = self.kernel.evaluate(context)
        if not decision.allowed:
            refusal = self.refusal_engine.build(decision)
            summary = decision.explanation
            event = self.ledger.record(
                request_id=request_id,
                decision=decision,
                consent=consent,
                model_invoked=False,
                provider=None,
                memory_written=False,
                user_visible_summary=summary,
            )
            return PipelineResult(
                request_id=request_id,
                response=refusal.message,
                identity=SARAH_IDENTITY_DISCLOSURE,
                consent=consent.to_dict(),
                decision=decision,
                refusal=refusal,
                model_response=None,
                ledger_event=event,
            )

        model_response = self.model_adapter.generate(
            message,
            system_context={
                "identity": SARAH_IDENTITY_DISCLOSURE,
                "consent": consent.to_dict(),
                "policy_version": decision.policy_version,
                "emotional_state_inference_allowed": consent.emotional_state_inference,
                "personal_memory_storage_allowed": consent.personal_memory_storage,
            },
        )
        # v0.1 has no durable narrative-memory implementation. Consent alone never
        # causes a write; a later memory module must require a separate save action.
        memory_written = False
        summary = "Request passed all hard gates and was sent to the configured model adapter."
        event = self.ledger.record(
            request_id=request_id,
            decision=decision,
            consent=consent,
            model_invoked=True,
            provider=model_response.provider,
            memory_written=memory_written,
            user_visible_summary=summary,
        )
        return PipelineResult(
            request_id=request_id,
            response=model_response.text,
            identity=SARAH_IDENTITY_DISCLOSURE,
            consent=consent.to_dict(),
            decision=decision,
            refusal=None,
            model_response=model_response,
            ledger_event=event,
        )
