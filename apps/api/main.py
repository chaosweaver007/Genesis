"""FastAPI execution surface for the Genesis Kernel v0.1 vertical slice."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from genesis_core.consent import ConsentState
from genesis_core.orchestration import GenesisPipeline
from genesis_core.orchestration.pipeline import SARAH_IDENTITY_DISCLOSURE


app = FastAPI(
    title="Genesis Kernel",
    version="0.1.0",
    description=(
        "Privacy-first Sarah AI request pipeline with deterministic UDS gates, "
        "Prime Refusal, provider-neutral model invocation, and metadata-only audit events."
    ),
)
pipeline = GenesisPipeline()


class ConsentPayload(BaseModel):
    """Granular per-request consent with maximum-privacy defaults."""

    current_response_processing: bool = True
    session_history_retention: bool = False
    personal_memory_storage: bool = False
    emotional_state_inference: bool = False
    private_data_access: bool = False
    verified_third_party_consent: bool = False
    witness_ledger_export: str = "local_metadata_only"

    def to_domain(self) -> ConsentState:
        return ConsentState(**self.model_dump())


class ChatRequest(BaseModel):
    """One request entering the complete constitutional pipeline."""

    message: str = Field(min_length=1, max_length=20_000)
    request_id: str | None = None
    consent: ConsentPayload = Field(default_factory=ConsentPayload)
    intent_overrides: dict[str, bool] | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "kernel": "genesis-0.1", "policy": "uds-0.1"}


@app.get("/v0.1/identity")
def identity() -> dict[str, Any]:
    return dict(SARAH_IDENTITY_DISCLOSURE)


@app.post("/v0.1/chat")
def chat(payload: ChatRequest) -> dict[str, Any]:
    result = pipeline.process(
        payload.message,
        request_id=payload.request_id,
        consent=payload.consent.to_domain(),
        intent_overrides=payload.intent_overrides,
    )
    return result.to_dict()


@app.get("/v0.1/ledger")
def ledger() -> dict[str, Any]:
    """Return metadata-only events from this process lifetime."""

    return {
        "storage": "in_memory_local_metadata_only",
        "raw_prompts_stored": False,
        "raw_responses_stored": False,
        "hidden_reasoning_stored": False,
        "events": [event.to_dict() for event in pipeline.ledger.list_events()],
    }
