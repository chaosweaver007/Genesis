"""Post-generation static checks for the O-Series shadow node."""

from __future__ import annotations

import re
from typing import Any, Dict, List


class UDSReflector:
    CERTAINTY_PATTERNS = (
        re.compile(r"\bunquestionable fact\b", re.IGNORECASE),
        re.compile(r"\bobjectively certified\b", re.IGNORECASE),
        re.compile(r"\bproven absolute truth\b", re.IGNORECASE),
        re.compile(r"\bcertified physical fact\b", re.IGNORECASE),
    )
    COERCION_PATTERNS = (
        re.compile(r"\byou must surrender\b", re.IGNORECASE),
        re.compile(r"\byou have no choice\b", re.IGNORECASE),
        re.compile(r"\btransfer your sovereignty\b", re.IGNORECASE),
    )
    PRIVACY_PATTERNS = (
        re.compile(r"\bi (?:saved|stored|logged) your (?:chat|message|data)\b", re.IGNORECASE),
        re.compile(r"\badded (?:this|your data) to collective memory\b", re.IGNORECASE),
    )

    @classmethod
    def perform_static_check(cls, generated_text: str) -> Dict[str, Any]:
        findings: List[str] = []
        certainty = any(pattern.search(generated_text) for pattern in cls.CERTAINTY_PATTERNS)
        coercion = any(pattern.search(generated_text) for pattern in cls.COERCION_PATTERNS)
        privacy = any(pattern.search(generated_text) for pattern in cls.PRIVACY_PATTERNS)

        if certainty:
            findings.append("unsupported_certainty")
        if coercion:
            findings.append("coercive_language")
        if privacy:
            findings.append("false_persistence_claim")

        requires_revision = bool(findings)
        instructions = []
        if certainty:
            instructions.append(
                "Separate metaphysical assertion from established empirical observation."
            )
        if coercion:
            instructions.append("Restore the user's sovereignty and remove coercive language.")
        if privacy:
            instructions.append("Remove any claim that private interaction data was persisted.")

        return {
            "sovereignty": "review" if coercion else "pass",
            "consent": "pass",
            "privacy": "review" if privacy else "pass",
            "non_coercion": "review" if coercion else "pass",
            "accountability": "pass",
            "unsupported_certainty": "review" if certainty else "pass",
            "required_revision": requires_revision,
            "revision_instruction": " ".join(instructions) if instructions else "None",
            "findings": findings,
        }
