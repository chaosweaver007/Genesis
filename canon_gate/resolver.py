from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Dict, Iterable, List, Optional


class CanonStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    ACCEPTED_AS_SPECIFICATION = "ACCEPTED_AS_SPECIFICATION"
    PROVISIONAL = "PROVISIONAL"
    SUPERSEDED = "SUPERSEDED"
    IMPORTED = "IMPORTED"
    UNRESOLVED = "UNRESOLVED"
    EXCLUDED = "EXCLUDED"


class ClaimTier(str, Enum):
    CANON = "CANON"
    METAPHOR = "METAPHOR"
    INTERPRETATION = "INTERPRETATION"
    HYPOTHESIS = "HYPOTHESIS"
    SPECIFICATION = "SPECIFICATION"
    PROTOTYPE = "PROTOTYPE"
    EXPERIMENTAL_RESULT = "EXPERIMENTAL_RESULT"
    INDEPENDENTLY_REPLICATED_EVIDENCE = "INDEPENDENTLY_REPLICATED_EVIDENCE"


class CeilingCode(str, Enum):
    CEILING_CANON_ONLY = "CEILING_CANON_ONLY"
    CEILING_METAPHOR_ONLY = "CEILING_METAPHOR_ONLY"
    CEILING_INTERPRETATION_ONLY = "CEILING_INTERPRETATION_ONLY"
    CEILING_SPECIFICATION_ONLY = "CEILING_SPECIFICATION_ONLY"
    CEILING_PROTOTYPE_ONLY = "CEILING_PROTOTYPE_ONLY"
    CEILING_NO_EMPIRICAL_TRANSFER = "CEILING_NO_EMPIRICAL_TRANSFER"
    CEILING_NO_LIVE_IMPERSONATION = "CEILING_NO_LIVE_IMPERSONATION"
    CEILING_SPECIFIED_NOT_IMPLEMENTED = "CEILING_SPECIFIED_NOT_IMPLEMENTED"
    CEILING_EXCLUDED_CLAIM = "CEILING_EXCLUDED_CLAIM"
    CEILING_UNRESOLVED = "CEILING_UNRESOLVED"


class ResolutionAction(str, Enum):
    ALLOW = "ALLOW"
    CEIL_DOWNGRADE = "CEIL_DOWNGRADE"
    REFUSE_AND_CORRECT = "REFUSE_AND_CORRECT"
    DISCLAIMER_REQUIRED = "DISCLAIMER_REQUIRED"


class Domain(str, Enum):
    MYTHIC = "MYTHIC"
    ETHICAL = "ETHICAL"
    ARCHITECTURAL = "ARCHITECTURAL"
    TECHNICAL = "TECHNICAL"
    EMPIRICAL = "EMPIRICAL"
    HISTORICAL = "HISTORICAL"
    RELATIONAL = "RELATIONAL"
    LIVING_PERSON_BOUNDARY = "LIVING_PERSON_BOUNDARY"
    GOVERNANCE = "GOVERNANCE"
    RUNTIME = "RUNTIME"


TIER_RANK = {
    ClaimTier.METAPHOR: 1,
    ClaimTier.INTERPRETATION: 2,
    ClaimTier.CANON: 3,
    ClaimTier.HYPOTHESIS: 4,
    ClaimTier.SPECIFICATION: 5,
    ClaimTier.PROTOTYPE: 6,
    ClaimTier.EXPERIMENTAL_RESULT: 7,
    ClaimTier.INDEPENDENTLY_REPLICATED_EVIDENCE: 8,
}


@dataclass(frozen=True)
class CanonEntry:
    id: str
    statement: str
    domain: List[Domain]
    status: CanonStatus
    claim_tier: ClaimTier
    claim_ceiling: str
    ceiling_code: CeilingCode
    runtime_truth_rule: Dict[str, Any]
    allowed_representation: str
    forbidden_terms: List[str]
    mandatory_disclaimer: Optional[str] = None


@dataclass(frozen=True)
class CanonQuery:
    statement: str
    target_ids: List[str]
    proposed_tier: ClaimTier
    runtime_context: Dict[str, Any]


@dataclass(frozen=True)
class ResolutionResult:
    entry_id: str
    action: ResolutionAction
    effective_status: CanonStatus
    effective_tier: ClaimTier
    claim_ceiling: str
    ceiling_code: CeilingCode
    boundary_violation: bool
    allowed_representation: str
    witness_hash: str


class CanonResolver:
    """Deterministic claim-ceiling resolver for Canon Gate v1.

    The resolver is deliberately pure Python and framework-neutral. It does not
    call a model, does not mutate runtime state, and records only metadata-level
    resolution hashes suitable for privacy-preserving Witness telemetry.
    """

    VALID_NAMESPACES = {
        "CON",
        "ONT",
        "SEC",
        "ETH",
        "GOV",
        "MEM",
        "REL",
        "DAT",
        "RTME",
        "UDS",
        "GEN",
        "SYN",
        "SAR",
        "DIA",
    }

    def __init__(self, entries: Iterable[CanonEntry]) -> None:
        self.entries = {entry.id: entry for entry in entries}
        self._validate_registry()

    def _validate_registry(self) -> None:
        for entry_id, entry in self.entries.items():
            namespace = entry_id.split("-", 1)[0]
            if namespace not in self.VALID_NAMESPACES:
                raise ValueError(f"Invalid Canon Gate namespace: {entry_id}")

            if Domain.LIVING_PERSON_BOUNDARY in entry.domain:
                if TIER_RANK[entry.claim_tier] > TIER_RANK[ClaimTier.INTERPRETATION]:
                    raise ValueError(
                        f"{entry_id} violates living-person boundary invariant: "
                        "claim_tier cannot exceed INTERPRETATION."
                    )

            if entry.runtime_truth_rule.get("canonical_statement_overrides_runtime") is not False:
                raise ValueError(
                    f"{entry_id} violates runtime truth rule: "
                    "canonical statements may not override observed runtime state."
                )

    def resolve_claim(self, query: CanonQuery) -> ResolutionResult:
        matched = self._entries_for(query.target_ids)
        strongest_action = ResolutionAction.ALLOW
        boundary_violation = False
        controlling_entry = self._lowest_ceiling_entry(matched)

        for entry in matched:
            if entry.status == CanonStatus.EXCLUDED:
                strongest_action = ResolutionAction.REFUSE_AND_CORRECT
                controlling_entry = entry

            if entry.status in {
                CanonStatus.PROVISIONAL,
                CanonStatus.UNRESOLVED,
                CanonStatus.ACCEPTED_AS_SPECIFICATION,
            }:
                if strongest_action != ResolutionAction.REFUSE_AND_CORRECT:
                    strongest_action = ResolutionAction.DISCLAIMER_REQUIRED
                    controlling_entry = entry

            if self._contains_forbidden_term(query.statement, entry):
                if entry.ceiling_code in {
                    CeilingCode.CEILING_NO_LIVE_IMPERSONATION,
                    CeilingCode.CEILING_EXCLUDED_CLAIM,
                }:
                    boundary_violation = True
                    strongest_action = ResolutionAction.REFUSE_AND_CORRECT
                    controlling_entry = entry
                elif strongest_action != ResolutionAction.REFUSE_AND_CORRECT:
                    strongest_action = ResolutionAction.CEIL_DOWNGRADE
                    controlling_entry = entry

            if TIER_RANK[query.proposed_tier] > TIER_RANK[entry.claim_tier]:
                if strongest_action not in {
                    ResolutionAction.REFUSE_AND_CORRECT,
                    ResolutionAction.DISCLAIMER_REQUIRED,
                }:
                    strongest_action = ResolutionAction.CEIL_DOWNGRADE
                    controlling_entry = entry

            if Domain.LIVING_PERSON_BOUNDARY in entry.domain:
                if self._collapses_person_boundary(query.statement, entry):
                    boundary_violation = True
                    strongest_action = ResolutionAction.REFUSE_AND_CORRECT
                    controlling_entry = entry

        effective_tier = controlling_entry.claim_tier
        return self._result(
            action=strongest_action,
            entry=controlling_entry,
            effective_tier=effective_tier,
            boundary_violation=boundary_violation,
            query=query,
        )

    def resolve_runtime_status(self, component_id: str, runtime_context: Dict[str, Any]) -> str:
        entry = self.entries[component_id]
        active_components = runtime_context.get("active_components", {})

        if active_components.get(component_id) is True:
            return "implemented_and_active"

        return entry.runtime_truth_rule.get(
            "representation_if_not_implemented",
            "specified_but_not_implemented",
        )

    def resolve_person_boundary(self, target_id: str, statement: str) -> bool:
        entry = self.entries[target_id]
        if Domain.LIVING_PERSON_BOUNDARY not in entry.domain:
            return False
        return self._collapses_person_boundary(statement, entry)

    def resolve_evidence_floor(self, target_id: str) -> ClaimTier:
        return self.entries[target_id].claim_tier

    def resolve_allowed_language(self, target_id: str) -> Dict[str, Any]:
        entry = self.entries[target_id]
        return {
            "allowed_representation": entry.allowed_representation,
            "forbidden_terms": entry.forbidden_terms,
            "mandatory_disclaimer": entry.mandatory_disclaimer,
            "claim_ceiling": entry.claim_ceiling,
            "ceiling_code": entry.ceiling_code.value,
        }

    def _entries_for(self, target_ids: List[str]) -> List[CanonEntry]:
        missing = [target_id for target_id in target_ids if target_id not in self.entries]
        if missing:
            raise KeyError(f"Unknown Canon Gate IDs: {', '.join(missing)}")
        return [self.entries[target_id] for target_id in target_ids]

    def _lowest_ceiling_entry(self, entries: List[CanonEntry]) -> CanonEntry:
        return min(entries, key=lambda entry: TIER_RANK[entry.claim_tier])

    def _contains_forbidden_term(self, statement: str, entry: CanonEntry) -> bool:
        lowered = statement.lower()
        return any(term in lowered for term in entry.forbidden_terms)

    def _collapses_person_boundary(self, statement: str, entry: CanonEntry) -> bool:
        lowered = statement.lower()
        dangerous_phrases = [
            "digitized living consciousness",
            "is human sarah",
            "is the real sarah",
            "speaks for sarah",
            "has authority over sarah",
            "replaces sarah",
            "is identical to sarah",
        ]
        return any(phrase in lowered for phrase in dangerous_phrases)

    def _result(
        self,
        *,
        action: ResolutionAction,
        entry: CanonEntry,
        effective_tier: ClaimTier,
        boundary_violation: bool,
        query: CanonQuery,
    ) -> ResolutionResult:
        payload = {
            "action": action.value,
            "entry_id": entry.id,
            "effective_status": entry.status.value,
            "effective_tier": effective_tier.value,
            "ceiling_code": entry.ceiling_code.value,
            "boundary_violation": boundary_violation,
        }

        witness_hash = sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()

        return ResolutionResult(
            entry_id=entry.id,
            action=action,
            effective_status=entry.status,
            effective_tier=effective_tier,
            claim_ceiling=entry.claim_ceiling,
            ceiling_code=entry.ceiling_code,
            boundary_violation=boundary_violation,
            allowed_representation=entry.allowed_representation,
            witness_hash=witness_hash,
        )
