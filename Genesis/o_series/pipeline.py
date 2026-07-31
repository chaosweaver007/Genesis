"""Master execution sequencer for the Genesis O-Series Gate 0 node."""

from __future__ import annotations

from typing import Any, Mapping, Optional

from .context_builder import ContextBuilder
from .gate_zero import GateZero
from .model_adapter import ModelAdapter, PersonaModelAdapter
from .schemas import PipelineResult, validate_envelope
from .uds_reflector import UDSReflector
from .witness_receipt import create_witness_receipt


class OSeriesPipeline:
    """Run validation, Gate 0, conditioned generation, reflection, and receipt."""

    def __init__(self, adapter: Optional[ModelAdapter] = None) -> None:
        """Create a pipeline with the production adapter or an injected test double."""

        self.adapter = adapter or PersonaModelAdapter()

    def run(
        self,
        *,
        payload: Mapping[str, Any],
        session_id: Optional[str] = None,
        trusted_restrictions: Optional[Mapping[str, Any]] = None,
    ) -> PipelineResult:
        """Execute one stateless request through the constitutional pipeline.

        The sequence implements the externally reportable O-Series contract:
        strict ingress validation, monotonic pre-generation gates, verified
        constitutional conditioning, six-layer output reflection, at most one
        bounded revision, and a metadata-only Witness Receipt.

        ``trusted_restrictions`` is an internal server-side channel. The public
        Flask route never accepts or forwards it, and Gate Zero treats it as
        add-only.
        """

        try:
            envelope = validate_envelope(payload, server_session_id=session_id)
        except ValueError as exc:
            message = str(exc)
            receipt = create_witness_receipt(
                response_text=message,
                gate_zero="not_run",
                reflection="not_run",
            )
            return PipelineResult(
                body={"error": message, "shadow_mode": True, "witness_receipt": receipt},
                status_code=400,
            )

        try:
            gate_result = GateZero.evaluate_ingress(
                envelope,
                trusted_restrictions=trusted_restrictions,
            )
        except ValueError as exc:
            message = str(exc)
            receipt = create_witness_receipt(
                response_text=message,
                gate_zero="configuration_error",
                reflection="not_run",
            )
            return PipelineResult(
                body={"error": message, "shadow_mode": True, "witness_receipt": receipt},
                status_code=500,
            )

        if gate_result["decision"] == "reject":
            message = "This request cannot pass Gate 0 within the private text-only shadow node."
            receipt = create_witness_receipt(
                response_text=message,
                gate_zero="rejected",
                reflection="not_run",
            )
            return PipelineResult(
                body={
                    "response": message,
                    "gate_zero": gate_result,
                    "shadow_mode": True,
                    "witness_receipt": receipt,
                },
                status_code=403,
            )

        sandbox = ContextBuilder.assemble_sandbox(envelope)
        system_context = ContextBuilder.render(sandbox)

        try:
            candidate = self.adapter.generate(
                system_context=system_context,
                envelope=envelope,
            )
        except (TypeError, ValueError) as exc:
            message = f"Model adapter rejected the conditioned request: {exc}"
            receipt = create_witness_receipt(
                response_text=message,
                gate_zero="passed",
                reflection="adapter_error",
            )
            return PipelineResult(
                body={
                    "error": message,
                    "gate_zero": gate_result,
                    "shadow_mode": True,
                    "witness_receipt": receipt,
                },
                status_code=502,
            )

        reflection = UDSReflector.perform_static_check(
            candidate.text,
            persona=envelope.persona,
        )
        revision_count = 0
        if reflection["required_revision"]:
            revision_count = 1
            candidate = self.adapter.revise(
                original=candidate,
                revision_instruction=reflection["revision_instruction"],
                system_context=system_context,
                envelope=envelope,
            )
            reflection = UDSReflector.perform_static_check(
                candidate.text,
                persona=envelope.persona,
            )

        receipt_kwargs = {
            "model_provider": candidate.provider,
            "model_name": candidate.model,
            "context_sha256": candidate.metadata.get("context_sha256"),
            "conditioning_mode": candidate.metadata.get("conditioning_mode"),
        }

        if reflection["required_revision"]:
            message = "The candidate response remained outside the UDS output contract after one bounded revision."
            receipt = create_witness_receipt(
                response_text=message,
                gate_zero="passed",
                reflection="blocked",
                **receipt_kwargs,
            )
            return PipelineResult(
                body={
                    "response": message,
                    "gate_zero": gate_result,
                    "reflection": reflection,
                    "revision_count": revision_count,
                    "shadow_mode": True,
                    "witness_receipt": receipt,
                },
                status_code=422,
            )

        receipt = create_witness_receipt(
            response_text=candidate.text,
            gate_zero="passed",
            reflection="revised" if revision_count else "passed",
            **receipt_kwargs,
        )
        return PipelineResult(
            body={
                "response": candidate.text,
                "gate_zero": gate_result,
                "reflection": reflection,
                "revision_count": revision_count,
                "shadow_mode": True,
                "context_manifest": {
                    "persona": envelope.persona,
                    "consent": sandbox["CONSENT_STATE"],
                    "capabilities": sandbox["EXECUTION_CAPABILITIES"],
                    "context_sha256": candidate.metadata.get("context_sha256"),
                    "conditioning_mode": candidate.metadata.get("conditioning_mode"),
                },
                "witness_receipt": receipt,
            },
            status_code=200,
        )
