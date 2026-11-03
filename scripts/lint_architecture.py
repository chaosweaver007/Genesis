#!/usr/bin/env python3
"""Ledger Before Spiral structural lint for newly authored Genesis ADRs/specs.

Only scans docs/architecture/**/{ADR-,SPEC-}*.md, excluding any templates.
No third-party Python dependencies; checks structure, not truth or test outcomes.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Sequence

HEADING = re.compile(r"^[ \t]{0,3}(#{1,6})[ \t]+(.+?)\s*$")
FENCE_OPEN = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})(?:[^\r\n]*)$")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
PLACEHOLDER = re.compile(
    r"^(?:[-*+]\s+|\d+[.)]\s+)?(?:`?\[?(?:TODO|TBD|PENDING|N/A|TBA|FIXME|PLACEHOLDER|NONE)\]?`?)(?:[\s.:;!\-]*)$",
    re.IGNORECASE,
)
REQUIRED = (
    "Evidence Basis",
    "Claim Ceiling",
    "Implementation Safeguard",
    "Verification Method",
)


def strip_code_fences(source: str) -> list[str]:
    """Ignore entire fenced blocks, closing only on same fence and sufficient length."""
    lines = source.splitlines()
    output: list[str] = []
    active_char = ""
    active_width = 0
    for line in lines:
        if not active_char:
            match = FENCE_OPEN.match(line)
            if match:
                fence = match.group(1)
                active_char, active_width = fence[0], len(fence)
                output.append("")
                continue
            output.append(line)
            continue
        # CommonMark: a closing fence has the same character, is at least
        # as wide as the opening fence, and contains no info-string suffix.
        close = re.match(r"^[ \t]{0,3}([`~]{3,})[ \t]*$", line)
        if close and set(close.group(1)) == {active_char} and len(close.group(1)) >= active_width:
            active_char, active_width = "", 0
        output.append("")
    return output


def normalize_heading(value: str) -> str:
    title = re.sub(r"\s+#+\s*$", "", value).strip().replace("**", "")
    title = re.sub(r"^\d+(?:\.\d+)*\s*[.)]?\s*", "", title)
    return title.casefold()


def matches_heading(title: str, required: str) -> bool:
    title = normalize_heading(title)
    key = required.casefold()
    return title == key or any(title.startswith(key + suffix) for suffix in (" &", " (", ":", " —", " -"))


def substantive(body: list[str]) -> bool:
    text = HTML_COMMENT.sub("", "\n".join(body))
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    # Reject stand-in content that mixes placeholder labels with real prose.
    lines = [line for line in lines if not PLACEHOLDER.fullmatch(line)]
    lines = [line for line in lines if not HEADING.match(line)]
    plain = re.sub(r"[\[\]()#*_`>|]", " ", " ".join(lines)).strip()
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", plain)
    return len(plain) >= 35 and len(words) >= 7


def lint_one(path: Path) -> list[str]:
    lines = strip_code_fences(path.read_text(encoding="utf-8"))
    clean = HTML_COMMENT.sub("", "\n".join(lines)).splitlines()
    headings: list[tuple[int, int, str]] = []
    for index, line in enumerate(clean):
        m = HEADING.match(line)
        if m:
            headings.append((index, len(m.group(1)), m.group(2)))
    errors: list[str] = []
    for section in REQUIRED:
        matches = [(i, level, title) for i, level, title in headings if matches_heading(title, section)]
        if not matches:
            errors.append(f"{path}: missing '## {section}' heading outside fenced code")
            continue
        if len(matches) > 1:
            errors.append(f"{path}: duplicate '{section}' headings")
            continue
        start, level, _ = matches[0]
        end = next((i for i, following_level, _ in headings if i > start and following_level <= level), len(clean))
        if not substantive(clean[start + 1:end]):
            errors.append(f"{path}: '{section}' needs substantive non-placeholder explanation")
    return errors


def is_record(path: Path) -> bool:
    return path.suffix.casefold() == ".md" and bool(re.match(r"(?i)^(?:ADR|SPEC)-[a-z0-9].*\.md$", path.name)) and "templates" not in {part.casefold().lstrip("_") for part in path.parts}


def scan(root: Path) -> list[Path]:
    folder = root / "docs" / "architecture"
    return sorted(path for path in folder.rglob("*.md") if path.is_file() and is_record(path)) if folder.exists() else []


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."), help="repository root (defaults to cwd)")
    args = parser.parse_args(argv)
    docs = scan(args.root)
    if not docs:
        print("PASS: No ADR-*.md or SPEC-*.md architecture records yet; new records will be linted.")
        return 0
    failures: list[str] = []
    for doc in docs:
        issues = lint_one(doc)
        failures.extend(issues)
        if not issues:
            print(f"PASS: {doc}")
    for issue in failures:
        print(f"FAIL: {issue}", file=sys.stderr)
    if failures:
        return 1
    print(f"All {len(docs)} architecture record(s) passed structural review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
