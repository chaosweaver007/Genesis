"""Pluggable permit-signing boundary.

The development signer is intentionally capped at E1. E2/E3 production signing
must be supplied by a separately reviewed signer profile. In particular, this
module does not pretend to implement FROST or DKG.
"""

from __future__ import annotations

import hashlib
import hmac
from typing import Protocol


class PermitSigner(Protocol):
    profile_id: str
    algorithm: str
    key_epoch: int

    def supports_effect_class(self, effect_class: str) -> bool: ...
    def sign(self, message: bytes) -> str: ...
    def verify(self, message: bytes, proof: str) -> bool: ...


class HMACDevelopmentSigner:
    """Development-only isolated signer for E0/E1 integration tests."""

    profile_id = "UDS-DEV-HMAC-SHA256"
    algorithm = "HMAC-SHA256-DEVELOPMENT-ONLY"

    def __init__(self, secret: bytes, *, key_epoch: int = 1) -> None:
        if not isinstance(secret, bytes) or len(secret) < 32:
            raise ValueError("Development signer secret must be at least 32 bytes.")
        if key_epoch < 1:
            raise ValueError("key_epoch must be positive.")
        self._secret = secret
        self.key_epoch = key_epoch

    def supports_effect_class(self, effect_class: str) -> bool:
        return effect_class in {"E0", "E1"}

    def sign(self, message: bytes) -> str:
        return hmac.new(self._secret, message, hashlib.sha256).hexdigest()

    def verify(self, message: bytes, proof: str) -> bool:
        return hmac.compare_digest(self.sign(message), proof)
