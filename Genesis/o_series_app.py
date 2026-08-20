"""Genesis O-Series Gate 0 application entrypoint.

The root route serves a first-party web interface to browsers while preserving
JSON discovery for API clients. The underlying O-Series runtime remains
stateless, private, text-only, and independent from the legacy SQLite-backed
application.
"""

from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from o_series.routes import register_o_series_routes

app = Flask(__name__)
app.config.update(
    JSON_SORT_KEYS=False,
    MAX_CONTENT_LENGTH=32 * 1024,
)

ROOT_INFO = {
    "service": "Genesis",
    "node": "O-Series Gate 0",
    "status": "running",
    "mode": "private-shadow",
    "pipeline_version": "o-series-0.1.1",
    "policy_version": "uds-0.1.1",
    "memory_write": "none",
    "chat_endpoint": "/api/o-series/chat",
    "status_endpoint": "/api/o-series/status",
    "web_interface": "/app",
}


@app.after_request
def apply_security_headers(response):
    """Attach no-store and browser hardening headers to every response."""

    response.headers.setdefault("Cache-Control", "no-store")
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self'; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "font-src 'self'; "
        "object-src 'none'; "
        "frame-ancestors 'none'; "
        "base-uri 'none'; "
        "form-action 'self'",
    )
    response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
    response.headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    return response


def _browser_prefers_html() -> bool:
    """Return True only when the client explicitly advertises HTML support."""

    accept = request.headers.get("Accept", "")
    if "text/html" not in accept:
        return False
    return request.accept_mimetypes["text/html"] >= request.accept_mimetypes["application/json"]


@app.get("/")
def root():
    """Serve the Genesis interface to browsers and JSON discovery to API clients."""

    if _browser_prefers_html():
        return render_template("o_series_home.html")
    return jsonify(ROOT_INFO)


@app.get("/app")
def web_app():
    """Serve the Genesis O-Series web interface explicitly."""

    return render_template("o_series_home.html")


@app.get("/api/o-series/info")
def api_info():
    """Return stable machine-readable service discovery metadata."""

    return jsonify(ROOT_INFO)


@app.get("/health")
def health():
    """Return the minimal liveness and deployed-version contract."""

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
