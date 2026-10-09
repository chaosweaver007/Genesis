"""Opt-in OpenAI Responses API adapter; no SDK dependency.

Only server-side credentials are read. No tools, stored response state,
or raw user messages in Witness metadata.
"""
from __future__ import annotations

import json
import os
from urllib import request, error

from .model_adapter import ModelAdapter, ModelResult, validate_system_context
from .schemas import IngressEnvelope


class OpenAIResponsesAdapter(ModelAdapter):
    """Generate conditioned text via the OpenAI Responses API."""

    def __init__(self, *, model: str | None = None) -> None:
        self.model = model or os.getenv("GENESIS_OPENAI_MODEL", "gpt-4.1-mini")

    def generate(self, *, system_context: str, envelope: IngressEnvelope) -> ModelResult:
        fingerprint = validate_system_context(system_context)
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY is not configured on the server.")
        payload = {
            "model": self.model,
            "instructions": system_context,
            "input": [{"role": "user", "content": envelope.message}],
            "store": False,
            "tools": [],
            "max_output_tokens": 600,
        }
        req = request.Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=25) as resp:
                result = json.load(resp)
        except (error.HTTPError, error.URLError, TimeoutError) as exc:
            # Do not expose upstream bodies, tokens, or private content.
            raise ValueError("OpenAI response generation unavailable.") from exc
        parts = [
            item.get("text", "")
            for output in result.get("output", [])
            if output.get("type") == "message"
            for item in output.get("content", [])
            if item.get("type") == "output_text"
        ]
        response_text = "\n".join(parts).strip()
        if not response_text:
            raise ValueError("OpenAI returned no reportable response text.")
        return ModelResult(
            text=response_text,
            provider="openai",
            model=self.model,
            metadata={
                "context_isolated": "true",
                "context_consumed": "true",
                "conditioning_mode": "responses-instructions",
                "context_sha256": fingerprint,
            },
        )
