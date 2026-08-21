"""Create user-readable, non-persistent O-Series Witness Receipts."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional
from uuid import uuid4

PIPELINE_VERSION = "o-series-0.2.0"
POLICY_VERSION = "uds-0.1.1"


def create_witness_receipt(
    *,
    response_text: str,
    gate_zero: str,
    reflection: str,
    consent_level: str = "private",
    tools_used: Optional[Iterable[str]] = None,
    model_provider: Optional[str] = None,
    model_name: Optional[str] = None,
    context_sha256: Optional[str] = None,
    conditioning_mode: Optional[str] = None,
    registry_version: Optional[str] = None,
    registry_hash: Optional[str] = None,
    registry_source_commit: Optional[str] = None,
    proposed_candidates: Optional[Iterable[str]] = None,
    selected_node: Optional[str] = None,
    challenge_status: Optional[str] = None,
    epistemic_boundary_verified: Optional[bool] = None,
    sovereignty_exit_preserved: Optional[bool] = None,
) -> Dict[str, Any]:
    """Return metadata-only provenance for one externally reportable response.

    The receipt stores hashes and bounded execution metadata, never the raw
    prompt, response, constitutional context, private correction text, or hidden
    reasoning. Sonic Codex fields identify interpretive proposals and the user's
    selector disposition without promoting those proposals to policy authority.
    """

    return {
        "trace_id": f"syn-{uuid4()}",
        "pipeline_version": PIPELINE_VERSION,
        "policy_version": POLICY_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gate_zero": gate_zero,
        "reflection": reflection,
        "consent_level": consent_level,
        "memory_write": "none",
        "tools_used": list(tools_used or []),
        "response_sha256": hashlib.sha256(response_text.encode("utf-8")).hexdigest(),
        "context_sha256": context_sha256,
        "conditioning_mode": conditioning_mode,
        "model_provider": model_provider,
        "model_name": model_name,
        "registry_version": registry_version,
        "registry_hash": registry_hash,
        "registry_source_commit": registry_source_commit,
        "proposed_candidates": list(proposed_candidates or []),
        "selected_node": selected_node,
        "challenge_status": challenge_status,
        "epistemic_boundary_verified": epistemic_boundary_verified,
        "sovereignty_exit_preserved": sovereignty_exit_preserved,
    }
