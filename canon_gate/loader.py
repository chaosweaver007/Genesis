from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

from canon_gate.resolver import (
    CanonEntry,
    CanonResolver,
    CanonStatus,
    CeilingCode,
    ClaimTier,
    Domain,
)


def load_registry_dict(data: Dict[str, Any]) -> CanonResolver:
    """Load a CanonResolver from a parsed registry mapping."""

    if not isinstance(data, dict):
        raise ValueError("Canon Gate registry must be a mapping.")

    raw_entries = data.get("entries", [])
    if not isinstance(raw_entries, list):
        raise ValueError("Canon Gate registry 'entries' must be a list.")

    entries: List[CanonEntry] = []
    for item in raw_entries:
        entries.append(
            CanonEntry(
                id=item["id"],
                statement=item["statement"].strip(),
                domain=[Domain(d) for d in item["domain"]],
                status=CanonStatus(item["status"]),
                claim_tier=ClaimTier(item["claim_tier"]),
                claim_ceiling=item["claim_ceiling"].strip(),
                ceiling_code=CeilingCode(item["ceiling_code"]),
                runtime_truth_rule=item.get("runtime_truth_rule", {}),
                allowed_representation=item["allowed_representation"].strip(),
                forbidden_terms=[t.lower() for t in item.get("forbidden_terms", [])],
                mandatory_disclaimer=(
                    item["mandatory_disclaimer"].strip()
                    if item.get("mandatory_disclaimer")
                    else None
                ),
            )
        )
    return CanonResolver(entries)


def load_registry_file(path: Path | str) -> CanonResolver:
    """Load a CanonResolver from a YAML registry file."""

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Canon Gate registry not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    return load_registry_dict(raw)
