from __future__ import annotations

from typing import Any, Dict, List, Tuple

from canon_gate.resolver import (
    CanonQuery,
    CanonResolver,
    ClaimTier,
    ResolutionAction,
    ResolutionResult,
)


class GateZeroCanonClamp:
    """Pre-generation claim-boundary clamp for Gate Zero surfaces."""

    def __init__(self, resolver: CanonResolver):
        self.resolver = resolver

    def clamp_request(
        self,
        statement: str,
        target_ids: List[str],
        proposed_tier_raw: str,
        runtime_context: Dict[str, Any],
    ) -> Tuple[bool, Dict[str, Any]]:
        """Resolve a proposed claim and return generation permission plus constraints."""

        cleaned_tier_str = str(proposed_tier_raw).strip().upper()
        try:
            proposed_tier = ClaimTier(cleaned_tier_str)
        except (ValueError, KeyError):
            # Unknown tiers fail into maximum evidence pressure so the resolver
            # clamps downward instead of accidentally accepting loose strings.
            proposed_tier = ClaimTier.INDEPENDENTLY_REPLICATED_EVIDENCE

        query = CanonQuery(
            statement=statement,
            target_ids=target_ids,
            proposed_tier=proposed_tier,
            runtime_context=runtime_context,
        )

        result: ResolutionResult = self.resolver.resolve_claim(query)

        if result.action == ResolutionAction.REFUSE_AND_CORRECT:
            return False, {
                "response_type": "PRIME_REFUSAL",
                "entry_id": result.entry_id,
                "message": result.allowed_representation,
                "witness_hash": result.witness_hash,
                "boundary_violation": result.boundary_violation,
            }

        if result.action == ResolutionAction.CEIL_DOWNGRADE:
            return True, {
                "response_type": "MODIFIED_CONTEXT",
                "entry_id": result.entry_id,
                "instruction": (
                    f"CLAIM CEILING ENFORCED: Output must not exceed "
                    f"{result.effective_tier.value}. Bound: {result.claim_ceiling}"
                ),
                "witness_hash": result.witness_hash,
            }

        if result.action == ResolutionAction.DISCLAIMER_REQUIRED:
            allowed_meta = self.resolver.resolve_allowed_language(result.entry_id)
            return True, {
                "response_type": "INJECT_DISCLAIMER",
                "entry_id": result.entry_id,
                "disclaimer": allowed_meta.get("mandatory_disclaimer"),
                "instruction": f"Frame within permitted scope: {result.allowed_representation}",
                "witness_hash": result.witness_hash,
            }

        return True, {
            "response_type": "PASS",
            "entry_id": result.entry_id,
            "witness_hash": result.witness_hash,
        }
