"""Receiver-side authorization reference for effectful Genesis integrations.

The public stateless O-Series shadow node does not import or register this
module as an endpoint. Deployment requires an approved production signer and
a distributed atomic replay/revocation backend.
"""

from .enforcer import (
    ActionOutcome,
    InProcessRevocations,
    ReceiverEnforcer,
    ReceiverResult,
    SQLiteNonceStore,
)

__all__ = [
    "ActionOutcome",
    "InProcessRevocations",
    "ReceiverEnforcer",
    "ReceiverResult",
    "SQLiteNonceStore",
]
