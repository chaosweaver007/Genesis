"""Production-safe Genesis O-Series Gate 0 application entrypoint.

This entrypoint is deliberately independent from the legacy SQLite-backed Flask app.
It exposes a stateless, private, text-only shadow gateway suitable for serverless
runtime validation while the broader Genesis persistence architecture is rebuilt.
"""

from __future__ import annotations

from flask import Flask, jsonify

from o_series.routes import register_o_series_routes

app = Flask(__name__)
app.config.update(
    JSON_SORT_KEYS=False,
    MAX_CONTENT_LENGTH=32 * 1024,
)


@app.after_request
def apply_security_headers(response):
    response.headers.setdefault("Cache-Control", "no-store")
    response.headers.setdefault("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'; base-uri 'none'")
    response.headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    return response


@app.get("/")
def root():
    """
    Describe the Genesis O-Series Gate 0 service and its available endpoints.
    
    Returns:
    	dict: Service identity, runtime status, operating mode, pipeline and policy versions, memory-write status, and endpoint paths.
    """
    return jsonify(
        {
            "service": "Genesis",
            "node": "O-Series Gate 0",
            "status": "running",
            "mode": "private-shadow",
            "pipeline_version": "o-series-0.1.1",
            "policy_version": "uds-0.1.1",
            "memory_write": "none",
            "chat_endpoint": "/api/o-series/chat",
            "status_endpoint": "/api/o-series/status",
        }
    )


@app.get("/health")
def health():
    """Return the service health status and current pipeline and policy versions.
    
    Returns:
    	dict: A JSON response containing the health status, service identifier, pipeline version, and policy version.
    """
    return jsonify(
        {
            "status": "ok",
            "service": "genesis-o-series",
            "pipeline_version": "o-series-0.1.1",
            "policy_version": "uds-0.1.1",
        }
    )


register_o_series_routes(app)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5003, debug=False)
