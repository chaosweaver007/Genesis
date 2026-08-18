"""UDS v1.1 hardened authorization primitives.

This package is deliberately independent from language-model generation. Model
output may propose an operation, but it cannot mint or validate execution
authority.
"""

from .authority import AuthorityEvidenceResolver, AuthorityResolution
from .broker import CapabilityBroker
from .models import (
    AuthorityEvidence,
    CanonicalExecutionRequest,
    ConsentObject,
    ExecutionPermit,
)
from .outcome import EvidenceLevel, OutcomeEvidence, OutcomeRecord
from .signing import HMACDevelopmentSigner, PermitSigner
from .state import AuthorizationStateRegistry
from .verifier import ExecutionPermitVerifier

__all__ = [
    "AuthorityEvidence",
    "AuthorityEvidenceResolver",
    "AuthorityResolution",
    "AuthorizationStateRegistry",
    "CanonicalExecutionRequest",
    "CapabilityBroker",
    "ConsentObject",
    "EvidenceLevel",
    "ExecutionPermit",
    "ExecutionPermitVerifier",
    "HMACDevelopmentSigner",
    "OutcomeEvidence",
    "OutcomeRecord",
    "PermitSigner",
]
