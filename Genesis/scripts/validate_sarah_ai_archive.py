#!/usr/bin/env python3
"""Dry-run validation for the Sarah AI canonical archive loader."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

GENESIS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GENESIS_DIR))

from sarah_ai_implementation import CanonicalArchiveError, SarahAI  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Sarah AI canonical archive loading.")
    parser.add_argument(
        "--message",
        default="Dry run: confirm canonical loader alignment.",
        help="Optional message to process after initialization.",
    )
    args = parser.parse_args()

    try:
        sarah = SarahAI()
    except CanonicalArchiveError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1

    summary = sarah.get_knowledge_summary()
    response = sarah.generate_response(args.message)

    checks = {
        "has_name": bool(summary.get("name")),
        "has_codename": bool(summary.get("codename")),
        "canonical_prompt_loaded": summary.get("canonical_prompt_loaded") is True,
        "canonical_prompt_length_gt_100": summary.get("canonical_prompt_length", 0) > 100,
        "environment_loaded": summary.get("environment") == "akadia_sandbox",
        "response_modes_loaded": len(summary.get("response_modes", [])) >= 4,
        "process_message_contract": isinstance(sarah.process_message(args.message), str),
    }

    ok = all(checks.values())
    print(json.dumps({"ok": ok, "checks": checks, "summary": summary, "sample_response": response}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
