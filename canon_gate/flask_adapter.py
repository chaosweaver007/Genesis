from __future__ import annotations

from flask import Blueprint, g, jsonify, request

from canon_gate.clamp import GateZeroCanonClamp

canon_bp = Blueprint("canon_gate", __name__)

# Reference adapter routes. Production O-Series enforcement must register this
# blueprint before generation and route canon_injection into the conditioned
# O-Series context before model generation.
TARGET_O_SERIES_ROUTES = {
    "/api/v1/generate",
    "/api/o-series/chat",
    "/api/o-series/selector/propose",
    "/api/o-series/selector/confirm",
}


@canon_bp.before_app_request
def intercept_epistemic_boundaries():
    """Apply Canon Gate checks to claim-bearing JSON ingress routes."""

    if request.path not in TARGET_O_SERIES_ROUTES or not request.is_json:
        return None

    data = request.get_json(silent=True) or {}
    target_ids = data.get("target_ids", [])

    if not target_ids:
        return None

    clamp: GateZeroCanonClamp = g.canon_clamp
    allowed, payload = clamp.clamp_request(
        statement=data.get("prompt") or data.get("statement") or data.get("message", ""),
        target_ids=target_ids,
        proposed_tier_raw=data.get("proposed_tier", "HYPOTHESIS"),
        runtime_context=g.get("runtime_context", {}),
    )

    if not allowed and payload["response_type"] == "PRIME_REFUSAL":
        return (
            jsonify(
                {
                    "status": "REFUSED",
                    "entry_id": payload["entry_id"],
                    "error": "Epistemic boundary or living-person invariant breach",
                    "correction": payload["message"],
                    "witness_hash": payload["witness_hash"],
                }
            ),
            403,
        )

    g.witness_hash = payload.get("witness_hash")
    g.canon_injection = payload.get("instruction") or payload.get("disclaimer")
    return None
