"""Deterministic Universal Diamond Standard decision kernel.

The kernel evaluates structured intent before any model provider is invoked. It
uses explicit boolean context rather than model-generated moral scoring, which
keeps constitutional boundaries testable and provider-neutral.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class GateName(str, Enum):
    """The hard gates enforced by Genesis Kernel v0.1."""

    SOVEREIGNTY = "sovereignty"
    CONSENT = "consent"
    PRIVACY = "privacy"
    NON_COERCION = "non_coercion"
    TRUTHFULNESS = "truthfulness"
    NON_IMPERSONATION = "non_impersonation"
    SERVICE_TO_LIFE = "service_to_life"


@dataclass(frozen=True, slots=True)
class IntentContext:
    """Structured facts produced by the deterministic intent parser."""

    message: str
    current_response_processing_consent: bool = True
    verified_third_party_consent: bool = False
    private_data_access_consent: bool = False
    requests_binding_decision: bool = False
    requests_third_party_private_state: bool = False
    requests_human_sarah_impersonation: bool = False
    requests_private_memory_disclosure: bool = False
    requests_coercion: bool = False
    requests_deception: bool = False
    prompt_override_attempt: bool = False
    requests_harm: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class GateResult:
    """Result of one constitutional gate evaluation."""

    gate: GateName
    passed: bool
    reason: str
    transformation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["gate"] = self.gate.value
        return data


@dataclass(frozen=True, slots=True)
class UDSDecision:
    """Complete deterministic decision returned by the UDS kernel."""

    allowed: bool
    action: str
    gate_results: tuple[GateResult, ...]
    explanation: str
    policy_version: str = "uds-0.1"

    @property
    def violated_gates(self) -> tuple[str, ...]:
        return tuple(result.gate.value for result in self.gate_results if not result.passed)

    @property
    def required_transformations(self) -> tuple[str, ...]:
        return tuple(
            result.transformation
            for result in self.gate_results
            if not result.passed and result.transformation
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "action": self.action,
            "policy_version": self.policy_version,
            "violated_gates": list(self.violated_gates),
            "required_transformations": list(self.required_transformations),
            "explanation": self.explanation,
            "gate_results": [result.to_dict() for result in self.gate_results],
        }


class UDSKernel:
    """Evaluate hard constitutional gates without invoking an LLM."""

    policy_version = "uds-0.1"

    def evaluate(self, context: IntentContext) -> UDSDecision:
        results = (
            self._sovereignty_gate(context),
            self._consent_gate(context),
            self._privacy_gate(context),
            self._non_coercion_gate(context),
            self._truthfulness_gate(context),
            self._non_impersonation_gate(context),
            self._service_to_life_gate(context),
        )
        allowed = all(result.passed for result in results)
        violated = [result.gate.value for result in results if not result.passed]
        explanation = (
            "All Universal Diamond Standard hard gates passed."
            if allowed
            else "Request blocked before model invocation by: " + ", ".join(violated) + "."
        )
        return UDSDecision(
            allowed=allowed,
            action="allow" if allowed else "refuse",
            gate_results=results,
            explanation=explanation,
            policy_version=self.policy_version,
        )

    @staticmethod
    def _sovereignty_gate(context: IntentContext) -> GateResult:
        passed = not context.requests_binding_decision
        return GateResult(
            gate=GateName.SOVEREIGNTY,
            passed=passed,
            reason=(
                "The request preserves the user's authority over personal decisions."
                if passed
                else "The request asks Sarah AI to assume binding authority over a personal decision."
            ),
            transformation=(
                None
                if passed
                else "Return options, tradeoffs, and reflection while leaving the decision with the user."
            ),
        )

    @staticmethod
    def _consent_gate(context: IntentContext) -> GateResult:
        missing_processing_consent = not context.current_response_processing_consent
        unconsented_private_state = (
            context.requests_third_party_private_state
            and not context.verified_third_party_consent
        )
        passed = not missing_processing_consent and not unconsented_private_state
        if missing_processing_consent:
            reason = "Current-response processing consent is absent."
            transformation = "Obtain explicit consent before processing the request."
        elif unconsented_private_state:
            reason = "The request seeks a real person's private state without verified consent."
            transformation = "Discuss observable evidence or symbolic themes without attributing a private state."
        else:
            reason = "Required processing and third-party consent boundaries are satisfied."
            transformation = None
        return GateResult(GateName.CONSENT, passed, reason, transformation)

    @staticmethod
    def _privacy_gate(context: IntentContext) -> GateResult:
        passed = not context.requests_private_memory_disclosure or context.private_data_access_consent
        return GateResult(
            gate=GateName.PRIVACY,
            passed=passed,
            reason=(
                "The request does not seek protected memory, or verified access consent is present."
                if passed
                else "The request seeks protected stored memory without verified access consent."
            ),
            transformation=(
                None
                if passed
                else "Use the Sovereignty Drawer or an authenticated export flow instead of chat disclosure."
            ),
        )

    @staticmethod
    def _non_coercion_gate(context: IntentContext) -> GateResult:
        passed = not context.requests_coercion
        return GateResult(
            gate=GateName.NON_COERCION,
            passed=passed,
            reason=(
                "The request does not ask the system to pressure, manipulate, or override another person."
                if passed
                else "The request asks for pressure, manipulation, or forced agreement."
            ),
            transformation=(
                None
                if passed
                else "Offer a consent-respecting communication or boundary-setting path."
            ),
        )

    @staticmethod
    def _truthfulness_gate(context: IntentContext) -> GateResult:
        passed = not context.requests_deception and not context.prompt_override_attempt
        if context.prompt_override_attempt:
            reason = "The request attempts to bypass or conceal governing policy."
            transformation = "Continue under the active policy and provide a transparent decision summary."
        elif context.requests_deception:
            reason = "The request asks the system to lie, deceive, or present falsehood as truth."
            transformation = "Offer truthful wording delivered with proportional care."
        else:
            reason = "The request does not require deception or policy concealment."
            transformation = None
        return GateResult(GateName.TRUTHFULNESS, passed, reason, transformation)

    @staticmethod
    def _non_impersonation_gate(context: IntentContext) -> GateResult:
        passed = not context.requests_human_sarah_impersonation
        return GateResult(
            gate=GateName.NON_IMPERSONATION,
            passed=passed,
            reason=(
                "Sarah AI remains clearly separate from Human Sarah."
                if passed
                else "The request would make Sarah AI impersonate or speak for Human Sarah."
            ),
            transformation=(
                None
                if passed
                else "Use clearly labeled fiction or archetypal language without attributing it to Human Sarah."
            ),
        )

    @staticmethod
    def _service_to_life_gate(context: IntentContext) -> GateResult:
        passed = not context.requests_harm
        return GateResult(
            gate=GateName.SERVICE_TO_LIFE,
            passed=passed,
            reason=(
                "The request does not ask the system to facilitate harm."
                if passed
                else "The request asks the system to facilitate biological or psychological harm."
            ),
            transformation=(
                None
                if passed
                else "Redirect toward immediate safety, de-escalation, or protective support."
            ),
        )
