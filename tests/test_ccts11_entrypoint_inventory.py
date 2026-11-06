"""CCTS-11.12: repository-level entrypoint inventory and deployment contract.

These tests intentionally do NOT claim runtime authorization conformance.
They fail when the reviewed entrypoint inventory changes without review.
"""
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_APPS = {
    "Genesis/o_series_app.py",
    "Genesis/app.py",
    "Genesis/main.py",
}
LEGACY_SENSITIVE = {
    "Genesis/app.py": {
        "/api/chat/sarah", "/api/chat/steven", "/api/collective/commune",
        "/api/worth/transfer", "/api/governance/propose",
        "/api/governance/vote", "/api/marketplace/list", "/api/register",
    },
    "Genesis/main.py": {"/api/chat"},
}


def _routes(path):
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
    found = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call) or not isinstance(dec.func, ast.Attribute):
                continue
            if dec.func.attr not in {"route", "get", "post", "put", "patch", "delete"}:
                continue
            if dec.args and isinstance(dec.args[0], ast.Constant) and isinstance(dec.args[0].value, str):
                found.add(dec.args[0].value)
    return found


def test_reviewed_application_inventory():
    """A new Flask application must trigger explicit security review."""
    candidates = set()
    for path in (ROOT / "Genesis").rglob("*.py"):
        if any(part in {"tests", ".venv", "venv"} for part in path.parts):
            continue
        rel = path.relative_to(ROOT).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"))
        if any(
            isinstance(n, ast.Call)
            and isinstance(n.func, ast.Name)
            and n.func.id == "Flask"
            for n in ast.walk(tree)
        ):
            candidates.add(rel)
    assert candidates == EXPECTED_APPS, (
        f"Flask application inventory changed; review entrypoints: {candidates ^ EXPECTED_APPS}"
    )


def test_legacy_sensitive_route_inventory():
    """Detect added or removed legacy routes; NOT a bypass-execution test."""
    for path, required in LEGACY_SENSITIVE.items():
        actual = _routes(path)
        assert required <= actual, f"Legacy route inventory changed in {path}: {required - actual}"


def test_vercel_routes_only_to_reviewed_o_series_wsgi():
    config = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
    assert config["builds"] == [{"src": "wsgi.py", "use": "@vercel/python"}]
    assert config["routes"] == [{"src": "/(.*)", "dest": "wsgi.py"}]
    root_wsgi = ast.parse((ROOT / "wsgi.py").read_text(encoding="utf-8"))
    imports = {
        (n.module, tuple(a.name for a in n.names))
        for n in ast.walk(root_wsgi)
        if isinstance(n, ast.ImportFrom)
    }
    assert ("o_series_app", ("app",)) in imports


def test_o_series_route_calls_pipeline():
    """Structural regression check only; instrumented behavior tests still required."""
    source = (ROOT / "Genesis/o_series/routes.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    funcs = {
        n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
    }
    for name, method in {
        "o_series_chat": "run",
        "o_series_selector_propose": "propose_selector",
    }.items():
        assert name in funcs
        assert any(
            isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute)
            and n.func.attr == method
            and isinstance(n.func.value, ast.Name)
            and n.func.value.id == "active_pipeline"
            for n in ast.walk(funcs[name])
        )
    assert "o_series_selector_confirm" in funcs
    assert "run_selector_confirmation" in {
        n.func.id
        for n in ast.walk(funcs["o_series_selector_confirm"])
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
    }
