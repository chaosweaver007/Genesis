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
    """Run validation, Gate 0, generation, one reflection, and a witness receipt."""

    def __init__(self, adapter: Optional[ModelAdapter] = None) -> None:
        self.adapter = adapter or PersonaModelAdapter()

    def run(
        self,
        *,
        payload: Mapping[str, Any],
        session_id: Optional[str] = None,
    ) -> PipelineResult:
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

        gate_result = GateZero.evaluate_ingress(envelope)
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
        candidate = self.adapter.generate(system_context=system_context, envelope=envelope)

        reflection = UDSReflector.perform_static_check(candidate.text)
        revision_count = 0
        if reflection["required_revision"]:
            revision_count = 1
            candidate = self.adapter.revise(
                original=candidate,
                revision_instruction=reflection["revision_instruction"],
                system_context=system_context,
                envelope=envelope,
            )
            reflection = UDSReflector.perform_static_check(candidate.text)

        if reflection["required_revision"]:
            message = "The candidate response remained outside the UDS output contract after one bounded revision."
            receipt = create_witness_receipt(
                response_text=message,
                gate_zero="passed",
                reflection="blocked",
                model_provider=candidate.provider,
                model_name=candidate.model,
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
            model_provider=candidate.provider,
            model_name=candidate.model,
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
                },
                "witness_receipt": receipt,
            },
            status_code=200,
        )
