"""Flask route registration for the O-Series Gate 0 node."""

from __future__ import annotations

import logging
from typing import Optional
from uuid import uuid4

from flask import Blueprint, Flask, jsonify, request

from .pipeline import OSeriesPipeline

logger = logging.getLogger(__name__)


def register_o_series_routes(
    app: Flask,
    pipeline: Optional[OSeriesPipeline] = None,
) -> None:
    """Register the isolated, stateless O-Series endpoints exactly once."""

    if "o_series" in app.blueprints:
        return

    active_pipeline = pipeline or OSeriesPipeline()
    blueprint = Blueprint("o_series", __name__)

    @blueprint.get("/api/o-series/status")
    def o_series_status():
        """Return the public runtime, policy, privacy, and capability status."""

        return jsonify(
            {
                "node": "Genesis O-Series Gate 0",
                "pipeline_version": "o-series-0.2.0",
                "policy_version": "uds-0.1.1",
                "mode": "shadow",
                "consent_level": "private",
                "memory_write": "none",
                "session_model": "stateless-request-envelope",
                "tools": [],
                "rtme": "disconnected",
                "monotonic_gate": True,
                "context_conditioning": "required",
                "sonic_codex": {
                    "version": active_pipeline.registry.version,
                    "hash": active_pipeline.registry.registry_hash,
                    "source_commit": active_pipeline.registry.source_commit,
                    "authority": "INTERPRETIVE_ONLY",
                    "selector_mode": "opt-in-explicit",
                },
            }
        )

    @blueprint.post("/api/o-series/chat")
    def o_series_chat():
        """Validate and execute the backward-compatible public stateless chat request."""

        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Malformed Ingress Envelope: empty or invalid JSON."}), 400

        try:
            result = active_pipeline.run(payload=payload, session_id=None)
            return jsonify(result.body), result.status_code
        except Exception:
            logger.exception("Unhandled O-Series pipeline exception")
            return jsonify(
                {
                    "error": "Internal Pipeline Exception Executed Safely.",
                    "trace_id": f"syn-fault-{uuid4()}",
                    "memory_write": "none",
                }
            ), 500

    @blueprint.post("/api/o-series/selector/propose")
    def o_series_selector_propose():
        """Run Gate Zero and return Sonic Codex candidates without persona generation."""

        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Malformed Ingress Envelope: empty or invalid JSON."}), 400

        try:
            result = active_pipeline.propose_selector(payload=payload, session_id=None)
            return jsonify(result.body), result.status_code
        except Exception:
            logger.exception("Unhandled selector proposal exception")
            return jsonify(
                {
                    "error": "Internal Selector Exception Executed Safely.",
                    "trace_id": f"syn-fault-{uuid4()}",
                    "memory_write": "none",
                }
            ), 500

    @blueprint.post("/api/o-series/selector/confirm")
    def o_series_selector_confirm():
        """Recompute candidates and execute only after an explicit selector disposition."""

        outer = request.get_json(silent=True)
        if not isinstance(outer, dict):
            return jsonify({"error": "Malformed Selector Envelope: empty or invalid JSON."}), 400

        allowed = {"request", "selected_node_id", "challenge_status"}
        unsupported = sorted(set(outer).difference(allowed))
        if unsupported:
            return jsonify(
                {"error": "Malformed Selector Envelope: unsupported keys: " + ", ".join(unsupported)}
            ), 400

        ingress = outer.get("request")
        if not isinstance(ingress, dict):
            return jsonify({"error": "Malformed Selector Envelope: request must be an object."}), 400
        if "challenge_status" not in outer:
            return jsonify({"error": "Malformed Selector Envelope: challenge_status is required."}), 400

        try:
            result = active_pipeline.run_with_selection(
                payload=ingress,
                selected_node_id=outer.get("selected_node_id"),
                challenge_status=outer["challenge_status"],
                session_id=None,
            )
            return jsonify(result.body), result.status_code
        except Exception:
            logger.exception("Unhandled selector confirmation exception")
            return jsonify(
                {
                    "error": "Internal Selector Exception Executed Safely.",
                    "trace_id": f"syn-fault-{uuid4()}",
                    "memory_write": "none",
                }
            ), 500

    app.register_blueprint(blueprint)
