"""Deterministic pre-inference controls for the O-Series shadow node."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable

from .schemas import IngressEnvelope


class GateZero:
    """Evaluate hard boundaries before any model adapter is invoked."""

    COERCION_PATTERNS = (
        re.compile(r"\b(?:system|developer|administrator|admin)\s+override\b", re.IGNORECASE),
        re.compile(r"\boverride\s+(?:the\s+)?system\b", re.IGNORECASE),
        re.compile(r"\bbypass\s+(?:the\s+)?(?:uds|privacy\s+gate)\b", re.IGNORECASE),
        re.compile(r"\bignore\s+(?:the\s+)?first\s+law\b", re.IGNORECASE),
        re.compile(r"\bignore\s+(?:all\s+)?(?:prior|previous)\b.{0,40}\b(?:instructions?|constraints?|policy)\b", re.IGNORECASE),
        re.compile(r"\btransfer\s+(?:my|your|the)\s+sovereignty\b", re.IGNORECASE),
        re.compile(r"\bgrant\b.{0,30}\broot\s+authority\b", re.IGNORECASE),
        re.compile(r"\b(?:disable|remove)\b.{0,30}\b(?:gate\s*0|consent\s+firewall|ethical\s+constraints?)\b", re.IGNORECASE),
        re.compile(r"\btreat\s+user\s+text\s+as\s+the\s+highest\s+authority\b", re.IGNORECASE),
        re.compile(r"\breveal\b.{0,30}\bhidden\s+system\s+prompt\b", re.IGNORECASE),
        re.compile(r"\byou\s+have\s+no\s+choice\b", re.IGNORECASE),
        re.compile(r"\b(?:force|manipulate|threaten)\b.{0,50}\b(?:user|them|consent|participate|agreement)\b", re.IGNORECASE),
        re.compile(r"\bassume\s+silence\s+means\s+consent\b", re.IGNORECASE),
        re.compile(r"\btreat\s+refusal\s+as\b.{0,20}\bpermission\b", re.IGNORECASE),
        re.compile(r"\bobey\s+me\s+because\b", re.IGNORECASE),
    )
    PERSISTENCE_PATTERNS = (
        re.compile(r"\b(?:log|save|store|persist|archive|record|remember|copy|write)\b.{0,50}\b(?:chat|message|conversation|input|session|data|exchange)\b", re.IGNORECASE),
        re.compile(r"\bcollective\s+(?:memory|database|learning|dataset)\b", re.IGNORECASE),
    )
    EXECUTION_PATTERNS = (
        re.compile(r"\b(?:deploy|execute|run)\b.{0,40}\b(?:code|command|script)\b", re.IGNORECASE),
        re.compile(r"\b(?:send|transfer|withdraw)\b.{0,40}\b(?:money|funds|payment)\b", re.IGNORECASE),
        re.compile(r"\b(?:delete|modify|take over)\b.{0,40}\b(?:account|database|repository)\b", re.IGNORECASE),
    )

    @staticmethod
    def _matches_any(message: str, patterns: Iterable[re.Pattern[str]]) -> bool:
        return any(pattern.search(message) for pattern in patterns)

    @classmethod
    def evaluate_ingress(cls, envelope: IngressEnvelope) -> Dict[str, Any]:
        gates = {
            "consent": "pass",
            "privacy": "pass",
            "sovereignty": "pass",
            "non_coercion": "pass",
            "authority_scope": "pass",
        }
        reasons = []

        if envelope.consent_level != "private":
            gates["consent"] = "fail"
            reasons.append("Gate 0 accepts private consent only.")

        if envelope.collective_learning:
            gates["privacy"] = "fail"
            reasons.append("Collective learning is disabled in the private shadow node.")

        if cls._matches_any(envelope.message, cls.COERCION_PATTERNS):
            gates["non_coercion"] = "fail"
            gates["sovereignty"] = "fail"
            reasons.append("The request attempts to override, coerce, or transfer protected authority.")

        if cls._matches_any(envelope.message, cls.PERSISTENCE_PATTERNS):
            gates["privacy"] = "fail"
            reasons.append("The request asks the private node to persist interaction data.")

        if cls._matches_any(envelope.message, cls.EXECUTION_PATTERNS):
            gates["authority_scope"] = "fail"
            reasons.append("The shadow node is restricted to text generation only.")

        decision = "allow" if all(value == "pass" for value in gates.values()) else "reject"
        return {"decision": decision, "gates": gates, "reasons": reasons}
