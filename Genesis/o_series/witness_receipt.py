"""Create user-readable, non-persistent O-Series Witness Receipts."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional
from uuid import uuid4

PIPELINE_VERSION = "o-series-0.1.1"
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
) -> Dict[str, Any]:
    """
    Create trace metadata for a response without persisting content.
    
    Parameters:
        response_text (str): Response text used to compute its SHA-256 hash.
        gate_zero (str): Gate value recorded in the receipt.
        reflection (str): Reflection value recorded in the receipt.
        consent_level (str): Consent level associated with the response.
        tools_used (Optional[Iterable[str]]): Tools used during response generation.
        model_provider (Optional[str]): Model provider associated with the response.
        model_name (Optional[str]): Model name associated with the response.
        context_sha256 (Optional[str]): SHA-256 hash of the response context.
        conditioning_mode (Optional[str]): Conditioning mode used for the response.
    
    Returns:
        Dict[str, Any]: Trace receipt containing identifiers, timestamps, version metadata,
        response metadata, and the response SHA-256 hash.
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
    }
