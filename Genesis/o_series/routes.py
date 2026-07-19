"""Flask route registration for the O-Series Gate 0 node."""

from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID, uuid4

from flask import Blueprint, Flask, jsonify, request, session

from .pipeline import OSeriesPipeline

logger = logging.getLogger(__name__)


def register_o_series_routes(
    app: Flask,
    pipeline: Optional[OSeriesPipeline] = None,
) -> None:
    """Register the isolated shadow endpoint once on a Flask application."""

    if "o_series" in app.blueprints:
        return

    active_pipeline = pipeline or OSeriesPipeline()
    blueprint = Blueprint("o_series", __name__)

    @blueprint.get("/api/o-series/status")
    def o_series_status():
        return jsonify(
            {
                "node": "Genesis O-Series Gate 0",
                "pipeline_version": "o-series-0.1",
                "mode": "shadow",
                "consent_level": "private",
                "memory_write": "none",
                "tools": [],
                "rtme": "disconnected",
            }
        )

    @blueprint.post("/api/o-series/chat")
    def o_series_chat():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Malformed Ingress Envelope: empty or invalid JSON."}), 400

        payload_session_id = payload.get("session_id")
        if "session_id" not in session:
            try:
                session["session_id"] = str(UUID(str(payload_session_id)))
            except (ValueError, TypeError, AttributeError):
                session["session_id"] = str(uuid4())

        try:
            result = active_pipeline.run(
                payload=payload,
                session_id=session.get("session_id"),
            )
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

    app.register_blueprint(blueprint)
