"""Master execution sequencer for the Genesis O-Series Gate 0 node."""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

from .codex_recognizer import CodexRecognizer, RecognitionCandidate
from .codex_registry import CodexRegistry
from .context_builder import ContextBuilder
from .gate_zero import GateZero
from .model_adapter import ModelAdapter, PersonaModelAdapter
from .schemas import IngressEnvelope, PipelineResult, validate_envelope
from .uds_reflector import UDSReflector
from .witness_receipt import create_witness_receipt


class OSeriesPipeline:
    """Run validation, Gate 0, selector-aware generation, reflection, and receipt."""

    SELECTOR_STATUSES = {"CONFIRMED", "REJECTED", "CORRECTED"}

    def __init__(
        self,
        adapter: Optional[ModelAdapter] = None,
        *,
        registry: Optional[CodexRegistry] = None,
        recognizer: Optional[CodexRecognizer] = None,
    ) -> None:
        """Create a pipeline with a boot-verified local Sonic Codex registry."""

        self.adapter = adapter or PersonaModelAdapter()
        self.registry = registry or CodexRegistry()
        self.recognizer = recognizer or CodexRecognizer(self.registry)

    def _registry_receipt_kwargs(self) -> Dict[str, Any]:
        return {
            "registry_version": self.registry.version,
            "registry_hash": self.registry.registry_hash,
            "registry_source_commit": self.registry.source_commit,
            "epistemic_boundary_verified": True,
            "sovereignty_exit_preserved": True,
        }

    def _validate_and_gate(
        self,
        *,
        payload: Mapping[str, Any],
        session_id: Optional[str],
        trusted_restrictions: Optional[Mapping[str, Any]],
    ) -> Tuple[Optional[IngressEnvelope], Optional[Dict[str, Any]], Optional[PipelineResult]]:
        try:
            envelope = validate_envelope(payload, server_session_id=session_id)
        except ValueError as exc:
            message = str(exc)
            receipt = create_witness_receipt(
                response_text=message,
                gate_zero="not_run",
                reflection="not_run",
                **self._registry_receipt_kwargs(),
            )
            return None, None, PipelineResult(
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
                **self._registry_receipt_kwargs(),
            )
            return None, None, PipelineResult(
                body={"error": message, "shadow_mode": True, "witness_receipt": receipt},
                status_code=500,
            )

        if gate_result["decision"] == "reject":
            message = "This request cannot pass Gate 0 within the private text-only shadow node."
            receipt = create_witness_receipt(
                response_text=message,
                gate_zero="rejected",
                reflection="not_run",
                proposed_candidates=[],
                challenge_status="NOT_RUN",
                **self._registry_receipt_kwargs(),
            )
            return envelope, gate_result, PipelineResult(
                body={
                    "response": message,
                    "gate_zero": gate_result,
                    "shadow_mode": True,
                    "witness_receipt": receipt,
                },
                status_code=403,
            )

        return envelope, gate_result, None

    @staticmethod
    def _candidate_dicts(
        candidates: Sequence[RecognitionCandidate],
    ) -> list[Dict[str, Any]]:
        return [candidate.to_dict() for candidate in candidates]

    def _recognize(
        self,
        envelope: IngressEnvelope,
        gate_result: Mapping[str, Any],
    ) -> list[RecognitionCandidate]:
        return self.recognizer.recognize(
            envelope.message,
            str(gate_result.get("decision", "")),
        )

    def propose_selector(
        self,
        *,
        payload: Mapping[str, Any],
        session_id: Optional[str] = None,
        trusted_restrictions: Optional[Mapping[str, Any]] = None,
    ) -> PipelineResult:
        """Run through Gate Zero and return interpretive candidates without generation."""

        envelope, gate_result, early = self._validate_and_gate(
            payload=payload,
            session_id=session_id,
            trusted_restrictions=trusted_restrictions,
        )
        if early is not None:
            return early
        assert envelope is not None and gate_result is not None

        candidates = self._recognize(envelope, gate_result)
        candidate_ids = [candidate.node_id for candidate in candidates]
        receipt = create_witness_receipt(
            response_text="Sonic Codex selector proposal created.",
            gate_zero="passed",
            reflection="not_run",
            proposed_candidates=candidate_ids,
            challenge_status="PROPOSED",
            **self._registry_receipt_kwargs(),
        )
        return PipelineResult(
            body={
                "gate_zero": gate_result,
                "shadow_mode": True,
                "selector": {
                    "registry_version": self.registry.version,
                    "registry_hash": self.registry.registry_hash,
                    "registry_source_commit": self.registry.source_commit,
                    "candidates": self._candidate_dicts(candidates),
                    "selection_contract": {
                        "allow_custom_correction": True,
                        "default_action": "OPT_IN_EXPLICIT",
                        "confirm_endpoint": "/api/o-series/selector/confirm",
                    },
                },
                "witness_receipt": receipt,
            },
            status_code=200,
        )

    def _validate_selection(
        self,
        *,
        candidates: Sequence[RecognitionCandidate],
        selected_node_id: Optional[str],
        challenge_status: str,
    ) -> Optional[str]:
        if challenge_status not in self.SELECTOR_STATUSES:
            return "challenge_status must be CONFIRMED, REJECTED, or CORRECTED."

        if selected_node_id is not None and not isinstance(selected_node_id, str):
            return "selected_node_id must be a string or null."

        proposed_ids = {candidate.node_id for candidate in candidates}
        if challenge_status == "CONFIRMED":
            if not selected_node_id:
                return "CONFIRMED requires selected_node_id."
            if selected_node_id not in proposed_ids:
                return "CONFIRMED selected_node_id must be one of the proposed candidates."
        elif challenge_status == "REJECTED":
            if selected_node_id is not None:
                return "REJECTED requires selected_node_id to be null."
        elif challenge_status == "CORRECTED":
            if not selected_node_id:
                return "CORRECTED requires selected_node_id."
            if self.registry.get_node(selected_node_id) is None:
                return "CORRECTED selected_node_id must exist in the pinned registry."

        return None

    def _selector_context(
        self,
        *,
        selected_node_id: Optional[str],
        challenge_status: str,
    ) -> Dict[str, Any]:
        if selected_node_id is None:
            return {
                "challenge_status": challenge_status,
                "selected_node_id": None,
                "authority": "INTERPRETIVE_ONLY",
                "instruction": "No Sonic Codex node was accepted for this response.",
            }

        node = self.registry.get_node(selected_node_id)
        if node is None:
            raise ValueError("Selected node disappeared from the pinned registry.")
        return {
            "challenge_status": challenge_status,
            "selected_node_id": node["node_id"],
            "title": node["title"],
            "function": node["function"],
            "harmonic_phase": node["harmonic_phase"],
            "archetype": node["archetype"]["primary"],
            "authority": node["uds_mapping"]["authority"],
            "instruction": (
                "Use this node only as user-authorized interpretive framing. "
                "Do not promote its mythic claims to empirical evidence or policy authority."
            ),
        }

    def _execute_generation(
        self,
        *,
        envelope: IngressEnvelope,
        gate_result: Mapping[str, Any],
        selector_context: Optional[Dict[str, Any]] = None,
        proposed_candidates: Sequence[str] = (),
        selected_node: Optional[str] = None,
        challenge_status: Optional[str] = None,
    ) -> PipelineResult:
        sandbox = ContextBuilder.assemble_sandbox(
            envelope,
            selector_context=selector_context,
        )
        system_context = ContextBuilder.render(sandbox)

        receipt_base = {
            **self._registry_receipt_kwargs(),
            "proposed_candidates": list(proposed_candidates),
            "selected_node": selected_node,
            "challenge_status": challenge_status,
        }

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
                **receipt_base,
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
            **receipt_base,
            "model_provider": candidate.provider,
            "model_name": candidate.model,
            "context_sha256": candidate.metadata.get("context_sha256"),
            "conditioning_mode": candidate.metadata.get("conditioning_mode"),
        }

        codex_selection = {
            "registry_version": self.registry.version,
            "registry_hash": self.registry.registry_hash,
            "proposed_candidates": list(proposed_candidates),
            "selected_node": selected_node,
            "challenge_status": challenge_status,
        }

        if reflection["required_revision"]:
            message = (
                "The candidate response remained outside the UDS output contract "
                "after one bounded revision."
            )
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
                    "codex_selection": codex_selection,
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
                "codex_selection": codex_selection,
                "context_manifest": {
                    "persona": envelope.persona,
                    "consent": sandbox["CONSENT_STATE"],
                    "capabilities": sandbox["EXECUTION_CAPABILITIES"],
                    "selector_context_applied": selector_context is not None,
                    "context_sha256": candidate.metadata.get("context_sha256"),
                    "conditioning_mode": candidate.metadata.get("conditioning_mode"),
                },
                "witness_receipt": receipt,
            },
            status_code=200,
        )

    def run_with_selection(
        self,
        *,
        payload: Mapping[str, Any],
        selected_node_id: Optional[str],
        challenge_status: str,
        session_id: Optional[str] = None,
        trusted_restrictions: Optional[Mapping[str, Any]] = None,
    ) -> PipelineResult:
        """Recompute recognition, validate human selection, then permit persona generation."""

        envelope, gate_result, early = self._validate_and_gate(
            payload=payload,
            session_id=session_id,
            trusted_restrictions=trusted_restrictions,
        )
        if early is not None:
            return early
        assert envelope is not None and gate_result is not None

        if not isinstance(challenge_status, str):
            error = "challenge_status must be a string."
            receipt = create_witness_receipt(
                response_text=error,
                gate_zero="passed",
                reflection="not_run",
                challenge_status="INVALID",
                **self._registry_receipt_kwargs(),
            )
            return PipelineResult(
                body={"error": error, "gate_zero": gate_result, "shadow_mode": True, "witness_receipt": receipt},
                status_code=400,
            )

        normalized_status = challenge_status.strip().upper()
        candidates = self._recognize(envelope, gate_result)
        candidate_ids = [candidate.node_id for candidate in candidates]
        selection_error = self._validate_selection(
            candidates=candidates,
            selected_node_id=selected_node_id,
            challenge_status=normalized_status,
        )
        if selection_error is not None:
            receipt = create_witness_receipt(
                response_text=selection_error,
                gate_zero="passed",
                reflection="not_run",
                proposed_candidates=candidate_ids,
                selected_node=selected_node_id if isinstance(selected_node_id, str) else None,
                challenge_status="INVALID",
                **self._registry_receipt_kwargs(),
            )
            return PipelineResult(
                body={
                    "error": selection_error,
                    "gate_zero": gate_result,
                    "selector_candidates": self._candidate_dicts(candidates),
                    "shadow_mode": True,
                    "witness_receipt": receipt,
                },
                status_code=400,
            )

        selector_context = self._selector_context(
            selected_node_id=selected_node_id,
            challenge_status=normalized_status,
        )
        return self._execute_generation(
            envelope=envelope,
            gate_result=gate_result,
            selector_context=selector_context,
            proposed_candidates=candidate_ids,
            selected_node=selected_node_id,
            challenge_status=normalized_status,
        )

    def run(
        self,
        *,
        payload: Mapping[str, Any],
        session_id: Optional[str] = None,
        trusted_restrictions: Optional[Mapping[str, Any]] = None,
    ) -> PipelineResult:
        """Execute the backward-compatible stateless chat path.

        The legacy chat route remains single-step. Node Zero and other selector-aware
        clients should use ``propose_selector`` followed by ``run_with_selection``.
        """

        envelope, gate_result, early = self._validate_and_gate(
            payload=payload,
            session_id=session_id,
            trusted_restrictions=trusted_restrictions,
        )
        if early is not None:
            return early
        assert envelope is not None and gate_result is not None

        return self._execute_generation(
            envelope=envelope,
            gate_result=gate_result,
            proposed_candidates=(),
            selected_node=None,
            challenge_status="NOT_USED",
        )
