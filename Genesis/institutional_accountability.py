"""Reference-only institutional due-process kernel for Synthsara.

This module never accepts raw complaint narratives or personal evidence, performs
no irreversible operations, and is NOT an authenticated public service.
The trusted host must establish Principal identity/roles independently.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
import secrets
from typing import FrozenSet, Optional
from uuid import uuid4


PROTOCOL_VERSION = "synthsara-accountability-0.1"
CATEGORIES = frozenset({
    "access", "governance", "resources", "privacy", "institutional_conduct"
})
DECISIONS = frozenset({
    "RESTORE", "CORRECT", "RESTITUTION", "DISMISS", "ESCALATE"
})
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


class AccountabilityError(ValueError):
    """A constitutional boundary or state-machine transition was rejected."""


@dataclass(frozen=True)
class Principal:
    """Trusted *server-authenticated* principal, never built from public JSON."""

    subject_id: str
    roles: FrozenSet[str] = frozenset()
    authenticated: bool = False


@dataclass
class _Case:
    claimant_id: str
    institution_id: str
    category: str
    state: str = "OPEN"
    reviewer_id: Optional[str] = None
    appeal_reviewer_id: Optional[str] = None
    decision: Optional[str] = None
    appealed: bool = False


class AccountabilityKernel:
    """In-memory reference engine with a hash-chained, metadata-only audit trail.

    A hash chain detects modified/reordered events given an independently held
    head digest. It is not a signature, durable store, or trusted timestamp.
    The engine deliberately does not adjudicate evidence or execute remedies.
    """

    def __init__(self, *, commitment_key: Optional[bytes] = None) -> None:
        self._commitment_key = commitment_key or secrets.token_bytes(32)
        if len(self._commitment_key) < 32:
            raise ValueError("commitment_key must contain at least 32 bytes")
        self._cases: dict[str, _Case] = {}
        self._events: dict[str, list[dict]] = {}

    @staticmethod
    def _identity(principal: Principal, role: str) -> str:
        if (
            not isinstance(principal, Principal)
            or not principal.authenticated
            or not isinstance(principal.subject_id, str)
            or not principal.subject_id.strip()
            or role not in principal.roles
        ):
            raise AccountabilityError("Missing trusted identity or required role")
        return principal.subject_id

    @staticmethod
    def _evidence(digest: str) -> str:
        if not isinstance(digest, str) or _SHA256.fullmatch(digest) is None:
            raise AccountabilityError("Evidence requires a lowercase SHA-256 digest")
        return digest

    @staticmethod
    def _canonical(value: dict) -> bytes:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("ascii")

    def _commitment(self, digest: str) -> str:
        """Hide even the submitted evidence digest from public receipts."""
        return hmac.new(
            self._commitment_key, digest.encode("ascii"), hashlib.sha256
        ).hexdigest()

    def _record(self, case_id: str, action: str, state: str, *, details: dict) -> dict:
        events = self._events[case_id]
        previous = events[-1]["sha256"] if events else "0" * 64
        envelope = {
            "protocol": PROTOCOL_VERSION,
            "case_id": case_id,
            "sequence": len(events) + 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "previous_sha256": previous,
            "action": action,
            "state": state,
            "details": details,
        }
        event = dict(envelope, sha256=hashlib.sha256(self._canonical(envelope)).hexdigest())
        events.append(event)
        return dict(event, details=dict(details))

    def _require_case(self, case_id: str) -> _Case:
        if case_id not in self._cases:
            raise AccountabilityError("Unknown case")
        return self._cases[case_id]

    def open_case(
        self, claimant: Principal, institution_id: str,
        category: str, evidence_sha256: str,
    ) -> tuple[str, dict]:
        claimant_id = self._identity(claimant, "participant")
        if not isinstance(institution_id, str) or not institution_id.strip():
            raise AccountabilityError("Institution identifier required")
        if claimant_id == institution_id:
            raise AccountabilityError("Claimant and respondent must differ")
        if category not in CATEGORIES:
            raise AccountabilityError("Unsupported complaint category")
        digest = self._evidence(evidence_sha256)
        case_id = uuid4().hex
        self._cases[case_id] = _Case(claimant_id, institution_id, category)
        self._events[case_id] = []
        return case_id, self._record(
            case_id, "OPENED", "OPEN",
            details={"category": category, "evidence_commitment": self._commitment(digest)},
        )

    def assign_reviewer(self, case_id: str, reviewer: Principal) -> dict:
        reviewer_id = self._identity(reviewer, "reviewer")
        case = self._require_case(case_id)
        if case.state != "OPEN":
            raise AccountabilityError("Case is not awaiting initial review")
        if reviewer_id in {case.claimant_id, case.institution_id}:
            raise AccountabilityError("Conflicted reviewer")
        case.reviewer_id = reviewer_id
        case.state = "REVIEWING"
        return self._record(case_id, "REVIEW_ASSIGNED", case.state, details={})

    def decide(self, case_id: str, reviewer: Principal, decision: str) -> dict:
        reviewer_id = self._identity(reviewer, "reviewer")
        case = self._require_case(case_id)
        if case.state != "REVIEWING" or reviewer_id != case.reviewer_id:
            raise AccountabilityError("Only assigned independent reviewer can decide")
        if decision not in DECISIONS:
            raise AccountabilityError("Unsupported disposition")
        case.decision = decision
        case.state = "DECIDED"
        return self._record(
            case_id, "DECISION_RECORDED", case.state, details={"decision": decision},
        )

    def appeal(
        self, case_id: str, claimant: Principal, evidence_sha256: str,
    ) -> dict:
        claimant_id = self._identity(claimant, "participant")
        case = self._require_case(case_id)
        if case.claimant_id != claimant_id or case.state != "DECIDED" or case.appealed:
            raise AccountabilityError("Appeal unavailable or unauthorized")
        digest = self._evidence(evidence_sha256)
        case.appealed = True
        case.state = "APPEALED"
        return self._record(
            case_id, "APPEAL_REQUESTED", case.state,
            details={"evidence_commitment": self._commitment(digest)},
        )

    def resolve_appeal(
        self, case_id: str, reviewer: Principal, decision: str,
    ) -> dict:
        reviewer_id = self._identity(reviewer, "reviewer")
        case = self._require_case(case_id)
        if case.state != "APPEALED":
            raise AccountabilityError("Case is not awaiting an appeal decision")
        if reviewer_id in {
            case.claimant_id, case.institution_id, case.reviewer_id
        }:
            raise AccountabilityError("Appeal reviewer must be independent")
        if decision not in DECISIONS:
            raise AccountabilityError("Unsupported appeal disposition")
        case.appeal_reviewer_id = reviewer_id
        case.decision = decision
        case.state = "DECIDED"
        return self._record(
            case_id, "APPEAL_DECIDED", case.state, details={"decision": decision},
        )

    def verify_remedy(
        self, case_id: str, auditor: Principal, evidence_sha256: str,
    ) -> dict:
        auditor_id = self._identity(auditor, "auditor")
        case = self._require_case(case_id)
        if case.state != "DECIDED" or case.decision not in {
            "RESTORE", "CORRECT", "RESTITUTION"
        }:
            raise AccountabilityError("No reviewable remedy was ordered")
        if auditor_id in {
            case.claimant_id, case.institution_id,
            case.reviewer_id, case.appeal_reviewer_id
        }:
            raise AccountabilityError("Remedy verification must be independent")
        digest = self._evidence(evidence_sha256)
        case.state = "REMEDY_VERIFIED"
        return self._record(
            case_id, "REMEDY_VERIFIED", case.state,
            details={"evidence_commitment": self._commitment(digest)},
        )

    def close(self, case_id: str, auditor: Principal) -> dict:
        auditor_id = self._identity(auditor, "auditor")
        case = self._require_case(case_id)
        if auditor_id in {
            case.claimant_id, case.institution_id,
            case.reviewer_id, case.appeal_reviewer_id
        }:
            raise AccountabilityError("Independent closure required")
        # Initial dismissals must stay appealable; no artificial appeal clock
        # exists in the reference engine.
        if not (
            case.state == "REMEDY_VERIFIED"
            or (case.state == "DECIDED" and case.appealed and case.decision == "DISMISS")
        ):
            raise AccountabilityError("Closure requires verified remedy or appealed dismissal")
        case.state = "CLOSED"
        return self._record(case_id, "CLOSED", case.state, details={})

    def receipts(self, case_id: str) -> list[dict]:
        """Return isolated metadata copies. Never return private _Case values."""
        self._require_case(case_id)
        return [dict(event, details=dict(event["details"])) for event in self._events[case_id]]

    def verify_chain(self, case_id: str, *, expected_head: Optional[str] = None) -> bool:
        self._require_case(case_id)
        events = self._events[case_id]
        if not events:
            return False
        previous = "0" * 64
        for position, event in enumerate(events, 1):
            envelope = {key: value for key, value in event.items() if key != "sha256"}
            actual = hashlib.sha256(self._canonical(envelope)).hexdigest()
            if (
                event["sequence"] != position
                or event["previous_sha256"] != previous
                or not hmac.compare_digest(event["sha256"], actual)
            ):
                return False
            previous = event["sha256"]
        return expected_head is None or hmac.compare_digest(previous, expected_head)
