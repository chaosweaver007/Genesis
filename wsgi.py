"""WSGI entrypoint for the secured Genesis O-Series deployment."""

import sys
from pathlib import Path


def _add_project_to_path() -> None:
    """Ensure the Genesis project directory is on ``sys.path``."""

    project_root = Path(__file__).resolve().parent
    genesis_dir = project_root / "Genesis"

    if genesis_dir.exists() and str(genesis_dir) not in sys.path:
        sys.path.insert(0, str(genesis_dir))


_add_project_to_path()

from o_series_app import app  # noqa: E402

# The secured Flask app, including Gate 0 shadow routes, is exposed to WSGI.
