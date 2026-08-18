"""Deterministic, interpretive-only recognition against the pinned Sonic Codex."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Sequence

from .codex_registry import CodexRegistry


_TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?", re.IGNORECASE)


@dataclass(frozen=True)
class RecognitionCandidate:
    node_id: str
    title: str
    harmonic_phase: str
    archetype: str
    confidence: float
    matched_themes: List[str]
    reason_codes: List[str]
    epistemic_claims: List[Dict[str, Any]]
    authority: str = "INTERPRETIVE_ONLY"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CodexRecognizer:
    """Rank declared node themes without granting them constitutional authority."""

    def __init__(self, registry: CodexRegistry, *, max_candidates: int = 3) -> None:
        if max_candidates < 1:
            raise ValueError("max_candidates must be positive.")
        self.registry = registry
        self.max_candidates = max_candidates

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {match.group(0).lower() for match in _TOKEN_RE.finditer(text)}

    @classmethod
    def _theme_matches(cls, theme: str, text_lower: str, text_tokens: set[str]) -> bool:
        normalized = " ".join(theme.lower().split())
        if normalized in text_lower:
            return True

        theme_tokens = cls._tokens(normalized)
        if not theme_tokens:
            return False
        if len(theme_tokens) == 1:
            return bool(theme_tokens & text_tokens)

        overlap = len(theme_tokens & text_tokens) / len(theme_tokens)
        return overlap >= 0.8

    def recognize(self, text: str, gate_zero_decision: str) -> List[RecognitionCandidate]:
        """Return bounded candidates only after Gate Zero has explicitly allowed ingress."""

        if gate_zero_decision != "allow":
            return []
        if not isinstance(text, str) or not text.strip():
            return []

        text_lower = " ".join(text.lower().split())
        text_tokens = self._tokens(text_lower)
        candidates: List[RecognitionCandidate] = []

        for node in self.registry.iter_nodes():
            recognition = node["recognition"]
            themes: Sequence[str] = recognition["themes"]
            reason_codes: Sequence[str] = recognition["reason_codes"]

            matched_indexes = [
                index
                for index, theme in enumerate(themes)
                if self._theme_matches(theme, text_lower, text_tokens)
            ]
            if not matched_indexes:
                continue

            matched_themes = [themes[index] for index in matched_indexes]
            matched_reason_codes = [
                reason_codes[index]
                for index in matched_indexes
                if index < len(reason_codes)
            ]
            confidence = min(1.0, (len(matched_themes) / len(themes)) * 1.5)

            candidates.append(
                RecognitionCandidate(
                    node_id=node["node_id"],
                    title=node["title"],
                    harmonic_phase=node["harmonic_phase"],
                    archetype=node["archetype"]["primary"],
                    confidence=round(confidence, 2),
                    matched_themes=matched_themes,
                    reason_codes=matched_reason_codes,
                    epistemic_claims=list(node.get("claims", [])),
                    authority=node["uds_mapping"]["authority"],
                )
            )

        candidates.sort(key=lambda candidate: (-candidate.confidence, candidate.node_id))
        return candidates[: self.max_candidates]
