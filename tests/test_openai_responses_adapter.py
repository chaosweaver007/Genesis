"""Unit tests for the opt-in Responses API adapter (no network calls)."""
import json
from unittest.mock import patch
from uuid import uuid4

import unittest

from Genesis.o_series.openai_adapter import OpenAIResponsesAdapter
from Genesis.o_series.schemas import IngressEnvelope
from Genesis.o_series.model_adapter import REQUIRED_CONTEXT_SECTIONS


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, *_):
        return json.dumps({
            "output": [{"type": "message", "content": [
                {"type": "output_text", "text": "Hello from a model."}
            ]}]
        }).encode()


def test_openai_adapter_does_not_store_responses():
    envelope = IngressEnvelope(
        request_id=str(uuid4()), session_id=str(uuid4()), message="Hello",
        persona="steven", consent_level="private",
        collective_learning=False, pipeline_mode="shadow", timestamp="now",
    )
    context = "\n".join(REQUIRED_CONTEXT_SECTIONS)
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        with patch("Genesis.o_series.openai_adapter.request.urlopen", return_value=FakeResponse()) as call:
            result = OpenAIResponsesAdapter(model="test-model").generate(
                system_context=context, envelope=envelope
            )
    body = json.loads(call.call_args.args[0].data)
    assert body["store"] is False
    assert body["tools"] == []
    assert body["input"][0]["content"] == "Hello"
    assert result.text == "Hello from a model."
    assert result.provider == "openai"
    assert "Hello" not in str(result.metadata)


def test_openai_adapter_fails_closed_without_key():
    envelope = IngressEnvelope(
        request_id=str(uuid4()), session_id=str(uuid4()), message="Hello",
        persona="steven", consent_level="private",
        collective_learning=False, pipeline_mode="shadow", timestamp="now",
    )
    with patch.dict("os.environ", {}, clear=True):
        with unittest.TestCase().assertRaisesRegex(ValueError, "OPENAI_API_KEY"):
            OpenAIResponsesAdapter().generate(
                system_context="\\n".join(REQUIRED_CONTEXT_SECTIONS),
                envelope=envelope,
            )
