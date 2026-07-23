"""Create user-readable, non-persistent O-Series witness receipts."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional
from uuid import uuid4

PIPELINE_VERSION = "o-series-0.1"


def create_witness_receipt(
    *,
    response_text: str,
    gate_zero: str,
    reflection: str,
    consent_level: str = "private",
    tools_used: Optional[Iterable[str]] = None,
    model_provider: Optional[str] = None,
    model_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Return trace metadata without writing it to disk or collective memory."""

    return {
        "trace_id": f"syn-{uuid4()}",
        "pipeline_version": PIPELINE_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gate_zero": gate_zero,
        "reflection": reflection,
        "consent_level": consent_level,
        "memory_write": "none",
        "tools_used": list(tools_used or []),
        "response_sha256": hashlib.sha256(response_text.encode("utf-8")).hexdigest(),
        "model_provider": model_provider,
        "model_name": model_name,
    }
