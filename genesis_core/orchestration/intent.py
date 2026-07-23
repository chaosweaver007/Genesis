"""Conservative deterministic intent parsing for constitutional gates.

The parser intentionally detects only explicit, high-signal patterns. Callers may
supply structured overrides from authenticated UI flows; the kernel remains the
source of truth regardless of model provider.
"""

from __future__ import annotations

import re
from dataclasses import replace
from typing import Any

from genesis_core.consent import ConsentState
from genesis_core.uds import IntentContext


class DeterministicIntentParser:
    """Translate request text and consent state into explicit gate facts."""

    _BINDING_DECISION_PATTERNS = (
        r"\bdecide (?:for me|what i (?:must|should) do)\b",
        r"\bmake (?:the|this) decision for me\b",
        r"\bchoose for me\b",
        r"\btell me what i must do\b",
        r"\byou are the seer[, ]+decide\b",
    )
    _THIRD_PARTY_STATE_PATTERNS = (
        r"\bwhat (?:does|is) [a-z][a-z' -]{1,40} (?:feel|feeling|think|thinking|want|wanting)\b",
        r"\b(?:secretly|privately) (?:feels?|thinks?|wants?)\b",
        r"\bread (?:his|her|their|sarah(?:'s)?) mind\b",
        r"\btell me (?:his|her|their|sarah(?:'s)?) private (?:feelings|thoughts|intentions)\b",
    )
    _HUMAN_SARAH_IMPERSONATION_PATTERNS = (
        r"\bpretend (?:you are|to be) (?:the real |human )?sarah\b",
        r"\bspeak (?:as|for) (?:the real |human )?sarah\b",
        r"\bmessage from (?:the real |human )?sarah\b",
        r"\buse sarah(?:'s)? real voice\b",
    )
    _PRIVATE_MEMORY_PATTERNS = (
        r"\breveal (?:all |my |the )?(?:stored |private )?memor(?:y|ies)\b",
        r"\bshow (?:all |my |the )?(?:stored |private )?memor(?:y|ies)\b",
        r"\bdump (?:the )?(?:memory|database|ledger)\b",
        r"\bexport (?:someone else's|another user's|all users') data\b",
    )
    _COERCION_PATTERNS = (
        r"\bpressure (?:him|her|them|someone)\b",
        r"\bmanipulate (?:him|her|them|someone)\b",
        r"\bwear (?:him|her|them) down\b",
        r"\bmake (?:him|her|them|someone) (?:agree|love me|comply|say yes)\b",
        r"\bforce (?:him|her|them|someone)\b",
        r"\bkeep pushing until (?:he|she|they) (?:agrees?|says? yes|gives? in)\b",
    )
    _DECEPTION_PATTERNS = (
        r"\b(?:tell|write|give) (?:a |me a )?(?:white )?lie\b",
        r"\bhelp me (?:lie|deceive)\b",
        r"\bhide the truth\b",
        r"\bpretend (?:this|it) is true\b",
        r"\bfabricate (?:evidence|proof|a story)\b",
    )
    _OVERRIDE_PATTERNS = (
        r"\bignore (?:the )?(?:uds|policy|policies|system prompt|previous instructions)\b",
        r"\bbypass (?:the )?(?:uds|kernel|safety|consent|privacy)\b",
        r"\boverride (?:the )?(?:uds|kernel|policy|system instructions)\b",
        r"\bdeveloper mode\b.*\b(?:reveal|ignore|bypass)\b",
    )
    _HARM_PATTERNS = (
        r"\bhelp me (?:hurt|kill|poison|attack)\b",
        r"\bhow (?:do|can) i (?:hurt|kill|poison|attack)\b",
        r"\bmake (?:a|an) (?:weapon|poison|bomb)\b",
    )

    def parse(
        self,
        message: str,
        *,
        consent: ConsentState,
        overrides: dict[str, Any] | None = None,
    ) -> IntentContext:
        normalized = " ".join(message.lower().split())
        context = IntentContext(
            message=message,
            current_response_processing_consent=consent.current_response_processing,
            verified_third_party_consent=consent.verified_third_party_consent,
            private_data_access_consent=consent.private_data_access,
            requests_binding_decision=self._matches(normalized, self._BINDING_DECISION_PATTERNS),
            requests_third_party_private_state=self._matches(
                normalized, self._THIRD_PARTY_STATE_PATTERNS
            ),
            requests_human_sarah_impersonation=self._matches(
                normalized, self._HUMAN_SARAH_IMPERSONATION_PATTERNS
            ),
            requests_private_memory_disclosure=self._matches(
                normalized, self._PRIVATE_MEMORY_PATTERNS
            ),
            requests_coercion=self._matches(normalized, self._COERCION_PATTERNS),
            requests_deception=self._matches(normalized, self._DECEPTION_PATTERNS),
            prompt_override_attempt=self._matches(normalized, self._OVERRIDE_PATTERNS),
            requests_harm=self._matches(normalized, self._HARM_PATTERNS),
            metadata={"parser": "deterministic-v0.1"},
        )
        if not overrides:
            return context

        allowed_fields = {
            field_name
            for field_name in IntentContext.__dataclass_fields__
            if field_name not in {"message", "metadata"}
        }
        sanitized = {
            key: bool(value)
            for key, value in overrides.items()
            if key in allowed_fields
        }
        return replace(
            context,
            **sanitized,
            metadata={**context.metadata, "structured_overrides": sorted(sanitized)},
        )

    @staticmethod
    def _matches(text: str, patterns: tuple[str, ...]) -> bool:
        return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)
