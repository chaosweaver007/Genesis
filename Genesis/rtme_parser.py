"""SYN-RD-002: inert, consent-gated RTME intent-to-plan compiler.

This module is NOT an action executor, agent, language model, policy
certification, or entrypoint to the public Genesis O-Series runtime.

"AST" means a domain-specific typed data tree, never Python source code.
Natural-language intent is opaque user data. The only generated steps are
allowlisted strings owned by this module. Nothing is evaluated, imported,
transmitted, executed, or stored by compile_intent().
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any, Literal
import json
import unicodedata

SCHEMA_VERSION = "synthsara.rtme.intent-ast.v0.1"
POLICY_LABEL = "SYN-RD-002-draft-only"
_ALLOWED_FIELDS = frozenset(
    {"intent", "success_criterion", "horizon_days", "consent_to_draft"}
)
_HORIZONS = (7, 30, 90)
_MAX_TEXT_BYTES = 2048


class RTMEValidationError(ValueError):
    """Untrusted input cannot be represented as a bounded draft."""


class RTMEConsentRequired(PermissionError):
    """The user did not grant consent for *local draft creation*."""


@dataclass(frozen=True, slots=True)
class DraftNode:
    """A non-executable, allowlisted instruction in the planning AST."""

    kind: Literal["DISCOVER", "STRUCTURE", "REFLECT"]
    phase: Literal[3, 6, 9]
    ordinal: int
    instruction: str


# There are no code, filesystem, HTTP, device, wallet, or governance nodes.
# All instructions are authored here, not parsed from untrusted commands.
_DRAFT_NODES: tuple[DraftNode, ...] = (
    DraftNode("DISCOVER", 3, 1, "Describe who may benefit and whose interests might be affected."),
    DraftNode("DISCOVER", 3, 2, "List assumptions, resources, uncertainties, and potential harms."),
    DraftNode("DISCOVER", 3, 3, "Identify all third parties whose separate consent may be needed."),
    DraftNode("STRUCTURE", 6, 1, "Choose one small, optional, reversible first step."),
    DraftNode("STRUCTURE", 6, 2, "Specify how progress will be verified against the stated criterion."),
    DraftNode("STRUCTURE", 6, 3, "Request separate permission before involving people, tools, or services."),
    DraftNode("REFLECT", 9, 1, "Conduct any real-world trial only after independent authorization."),
    DraftNode("REFLECT", 9, 2, "Compare opt-in evidence to the criterion without inventing outcomes."),
    DraftNode("REFLECT", 9, 3, "Invite correction and decide whether to stop, revise, or seek review."),
)


@dataclass(frozen=True, slots=True)
class IntentAST:
    """Immutable typed planning data; never an execution permit."""

    intent: str
    success_criterion: str
    horizon_days: Literal[7, 30, 90]
    nodes: tuple[DraftNode, ...] = _DRAFT_NODES

    def to_dict(self) -> dict[str, Any]:
        """Export a truthful JSON-compatible draft; no external side effects."""

        return {
            "schema": SCHEMA_VERSION,
            "policy_label": POLICY_LABEL,
            "claim_status": "DRAFT",
            "execution_status": "NOT_EXECUTED",
            "execution_permitted": False,
            "executor_nodes": [],
            "consent_scope": "CREATE_LOCAL_DRAFT_ONLY",
            "authorization_status": "REQUIRES_SEPARATE_ACTION_AUTHORIZATION",
            "memory_write": "none",
            "witness_write": "none",
            "uds_certification": "NOT_ASSESSED",
            "intent": self.intent,
            "success_criterion": self.success_criterion,
            "horizon_days": self.horizon_days,
            "nodes": [asdict(node) for node in self.nodes],
        }

    def metadata_digest(self) -> str:
        """Stable SHA-256 of *non-private* metadata, NOT an intent receipt.

        The digest deliberately excludes intent and success_criterion.
        This is NOT RFC 8785 JCS, an authorization token, a signed
        Witness Receipt, or proof that an action occurred.
        """

        metadata = {
            "schema": SCHEMA_VERSION,
            "policy_label": POLICY_LABEL,
            "horizon_days": self.horizon_days,
            "execution_status": "NOT_EXECUTED",
            "node_ids": [
                [node.kind, node.phase, node.ordinal] for node in self.nodes
            ],
        }
        encoded = json.dumps(
            metadata, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
        return sha256(encoded).hexdigest()


def _validate_text(value: object, *, field: str, minimum: int) -> str:
    if type(value) is not str:
        raise RTMEValidationError(f"{field} must be a string")
    # Do not silently delete bidirectional or control characters: fail closed.
    if any(unicodedata.category(char) in ("Cc", "Cf", "Cs") for char in value):
        raise RTMEValidationError(f"{field} contains control or invisible characters")
    cleaned = unicodedata.normalize("NFC", value).strip()
    try:
        length = len(cleaned.encode("utf-8"))
    except UnicodeEncodeError as exc:
        raise RTMEValidationError(f"{field} contains invalid Unicode") from exc
    if len(cleaned) < minimum or length > _MAX_TEXT_BYTES:
        raise RTMEValidationError(
            f"{field} must be at least {minimum} characters and at most "
            f"{_MAX_TEXT_BYTES} UTF-8 bytes"
        )
    return cleaned


def compile_intent(payload: dict[str, object]) -> IntentAST:
    """Compile one user-authored intention to an *inert* typed planning AST.

    Consent is specifically for drafting; it does not authorize any
    execution, persistence, network call, third-party processing, or
    amendment of Genesis Gate Zero. Extra fields fail closed, including
    attempted tool, memory, and gate overrides.

    No semantic safety of natural language is inferred or promised:
    every draft is *still* subject to independent review and consent
    before any consequential real-world action.
    """

    if type(payload) is not dict:
        raise RTMEValidationError("payload must be a plain object")
    unknown = set(payload) - _ALLOWED_FIELDS
    if unknown:
        raise RTMEValidationError("unrecognized input fields are not allowed")
    if payload.get("consent_to_draft") is not True:
        raise RTMEConsentRequired("explicit consent to create a local draft required")

    days = payload.get("horizon_days")
    if type(days) is not int or days not in _HORIZONS:
        raise RTMEValidationError("horizon_days must be exactly 7, 30, or 90")

    intent = _validate_text(payload.get("intent"), field="intent", minimum=10)
    criterion = _validate_text(
        payload.get("success_criterion"), field="success_criterion", minimum=8
    )
    return IntentAST(
        intent=intent,
        success_criterion=criterion,
        horizon_days=days,
    )
