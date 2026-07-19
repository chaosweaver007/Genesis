"""Secure application entrypoint with the O-Series Gate 0 routes enabled."""

from __future__ import annotations

import os

from collective_consciousness_home import app
from o_series.routes import register_o_series_routes


def _configure_runtime() -> None:
    secret_key = os.environ.get("FLASK_SECRET_KEY")
    if not secret_key or secret_key == "development_default_key_to_be_replaced":
        raise RuntimeError(
            "FLASK_SECRET_KEY is required; refusing to start with an embedded or placeholder key."
        )

    app.secret_key = secret_key

    database_url = os.environ.get("DATABASE_URL", "sqlite:///local_genesis_dev.db")
    if os.environ.get("VERCEL") == "1" and database_url.startswith("sqlite"):
        raise RuntimeError(
            "DATABASE_URL must use durable external storage when running on Vercel."
        )

    app.config["DATABASE_URL"] = database_url
    app.config["O_SERIES_MODE"] = "shadow"
    app.config["O_SERIES_MEMORY_WRITE"] = "none"


_configure_runtime()
register_o_series_routes(app)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5003, debug=False)
