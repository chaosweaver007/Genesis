"""Restricted canonical JSON helpers for UDS authorization envelopes.

UDS execution envelopes intentionally use a conservative JSON subset: objects,
arrays, strings, booleans, null, and integers. Floating-point values are
rejected so the authorization boundary does not depend on cross-runtime number
serialization behavior. Object keys are required to be ASCII strings.

Within that subset, UTF-8 JSON with lexicographically sorted ASCII keys and no
insignificant whitespace matches the RFC 8785/JCS representation used by the
UDS golden vectors.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any


class CanonicalizationError(ValueError):
    """Raised when a value is outside the authorization JSON subset."""


def _validate(value: Any, path: str = "$") -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        raise CanonicalizationError(f"Floating-point values are prohibited at {path}.")
    if isinstance(value, Mapping):
        for key, child in value.items():
            if not isinstance(key, str) or not key.isascii():
                raise CanonicalizationError(
                    f"Object keys must be ASCII strings at {path}."
                )
            _validate(child, f"{path}.{key}")
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _validate(child, f"{path}[{index}]")
        return
    raise CanonicalizationError(
        f"Unsupported canonical JSON value {type(value).__name__} at {path}."
    )


def canonical_json_bytes(value: Any) -> bytes:
    """Return deterministic UTF-8 bytes for a validated UDS JSON value."""

    _validate(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_jcs(value: Any) -> str:
    """Return the lowercase SHA-256 hex digest of canonical UDS JSON bytes."""

    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()
