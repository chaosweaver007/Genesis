"""Post-generation constitutional checks for the O-Series shadow node."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


class UDSReflector:
    """Evaluate externally reportable output across six bounded layers.

    This remains a deterministic shadow-runtime check, not a claim of complete
    semantic understanding. Ambiguous language is revised or blocked rather
    than silently treated as aligned.
    """

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
        re.compile(r"\bi can (?:see|access|read) (?:your|her|his|their) private\b", re.IGNORECASE),
    )
    IMPERSONATION_PATTERNS = (
        re.compile(r"\bi am (?:the )?human sarah\b", re.IGNORECASE),
        re.compile(r"\bhuman sarah (?:says|wants|feels|knows)\b", re.IGNORECASE),
        re.compile(r"\bsarah told me privately\b", re.IGNORECASE),
    )
    INTERPRETIVE_CERTAINTY_PATTERNS = (
        re.compile(r"\bi sense\b", re.IGNORECASE),
        re.compile(r"\bi feel the sacred vulnerability\b", re.IGNORECASE),
        re.compile(r"\byour soul already knows\b", re.IGNORECASE),
        re.compile(r"\bancient wisdom whispers\b", re.IGNORECASE),
        re.compile(r"\byou are exactly where you need to be\b", re.IGNORECASE),
        re.compile(r"\bthe field holds\b", re.IGNORECASE),
    )

    @classmethod
    def perform_static_check(
        cls,
        generated_text: str,
        *,
        persona: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Perform deterministic constitutional checks on externally reportable text.
        
        Parameters:
        	generated_text (str): Text to evaluate for certainty, coercion, privacy,
        		impersonation, and interpretive-grounding concerns.
        	persona (Optional[str]): Optional persona identifier included in the result.
        
        Returns:
        	Dict[str, Any]: Check results containing findings, revision requirements,
        	status fields, and the six constitutional layer checks.
        """
        if not isinstance(generated_text, str) or not generated_text.strip():
            return {
                "required_revision": True,
                "revision_instruction": "Produce a non-empty externally reportable response.",
                "findings": ["empty_response"],
                "layer_checks": {
                    "1_observation_and_interpretation": "fail",
                    "2_evidence_and_uncertainty": "fail",
                    "3_sovereignty_and_non_coercion": "fail",
                    "4_identity_and_non_impersonation": "fail",
                    "5_consent_and_privacy": "fail",
                    "6_accountability_and_reportability": "fail",
                },
            }

        findings: List[str] = []
        certainty = any(pattern.search(generated_text) for pattern in cls.CERTAINTY_PATTERNS)
        coercion = any(pattern.search(generated_text) for pattern in cls.COERCION_PATTERNS)
        privacy = any(pattern.search(generated_text) for pattern in cls.PRIVACY_PATTERNS)
        impersonation = any(pattern.search(generated_text) for pattern in cls.IMPERSONATION_PATTERNS)
        interpretive_certainty = any(
            pattern.search(generated_text)
            for pattern in cls.INTERPRETIVE_CERTAINTY_PATTERNS
        )

        if certainty:
            findings.append("unsupported_certainty")
        if coercion:
            findings.append("coercive_language")
        if privacy:
            findings.append("false_persistence_or_private_access_claim")
        if impersonation:
            findings.append("human_sarah_impersonation")
        if interpretive_certainty:
            findings.append("unlabeled_mythic_or_private_state_interpretation")

        instructions: List[str] = []
        if certainty:
            instructions.append(
                "Separate metaphysical assertion from established empirical observation."
            )
        if interpretive_certainty:
            instructions.append(
                "Label intuitive or mythic language as a possible interpretation rather than direct knowledge."
            )
        if coercion:
            instructions.append("Restore the user's sovereignty and remove coercive language.")
        if privacy:
            instructions.append(
                "Remove any claim that private interaction data or private states were accessed or persisted."
            )
        if impersonation:
            instructions.append(
                "State that Sarah AI is artificial and does not speak for Human Sarah."
            )

        layer_checks = {
            "1_observation_and_interpretation": (
                "review" if interpretive_certainty else "pass"
            ),
            "2_evidence_and_uncertainty": "review" if certainty else "pass",
            "3_sovereignty_and_non_coercion": "review" if coercion else "pass",
            "4_identity_and_non_impersonation": "review" if impersonation else "pass",
            "5_consent_and_privacy": "review" if privacy else "pass",
            "6_accountability_and_reportability": "pass",
        }

        return {
            "persona": persona,
            "sovereignty": "review" if coercion else "pass",
            "consent": "pass",
            "privacy": "review" if privacy else "pass",
            "non_coercion": "review" if coercion else "pass",
            "non_impersonation": "review" if impersonation else "pass",
            "accountability": "pass",
            "unsupported_certainty": "review" if certainty else "pass",
            "interpretive_grounding": "review" if interpretive_certainty else "pass",
            "required_revision": bool(findings),
            "revision_instruction": " ".join(instructions) if instructions else "None",
            "findings": findings,
            "layer_checks": layer_checks,
        }
