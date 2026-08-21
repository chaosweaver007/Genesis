"""Load and verify the pinned Sonic Codex registry snapshot."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


class PinnedRegistryError(RuntimeError):
    """Raised when the local Sonic Codex snapshot violates its pin contract."""


class CodexRegistry:
    """Immutable, network-free loader for the canonical Sonic Codex snapshot."""

    EXPECTED_VERSION = "0.1.0"
    EXPECTED_REGISTRY_ID = "SONIC-CODEX"
    EXPECTED_CONSTELLATION = "AFTER_THE_HUM_FIRST_NINE"
    EXPECTED_SHA256 = "8c47df2e33ffa6402cd83250bf2442e234d9b6a4bf0effb56647aa4fddf72299"
    DEFAULT_PATH = Path(__file__).resolve().parent / "registry" / "sonic-codex-v0.1.json"

    def __init__(
        self,
        registry_path: Optional[Path] = None,
        *,
        expected_hash: Optional[str] = None,
    ) -> None:
        self.registry_path = Path(registry_path or self.DEFAULT_PATH)
        self.registry_hash = ""
        self.source_repository = ""
        self.source_commit = ""
        self._nodes: Dict[str, Dict[str, Any]] = {}
        self._node_order: List[str] = []
        self._load_and_verify(expected_hash or self.EXPECTED_SHA256)

    def _load_and_verify(self, expected_hash: str) -> None:
        if not self.registry_path.is_file():
            raise PinnedRegistryError(f"Pinned registry missing: {self.registry_path}")

        raw = self.registry_path.read_bytes()
        self.registry_hash = hashlib.sha256(raw).hexdigest()
        if self.registry_hash != expected_hash:
            raise PinnedRegistryError(
                "Pinned registry integrity check failed: "
                f"{self.registry_hash} != {expected_hash}"
            )

        try:
            snapshot = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PinnedRegistryError("Pinned registry is not valid UTF-8 JSON.") from exc

        if snapshot.get("registry_id") != self.EXPECTED_REGISTRY_ID:
            raise PinnedRegistryError("Pinned registry_id mismatch.")
        if snapshot.get("version") != self.EXPECTED_VERSION:
            raise PinnedRegistryError("Pinned registry version mismatch.")
        if snapshot.get("constellation") != self.EXPECTED_CONSTELLATION:
            raise PinnedRegistryError("Pinned constellation mismatch.")

        nodes = snapshot.get("nodes")
        if not isinstance(nodes, list) or not nodes:
            raise PinnedRegistryError("Pinned registry must contain a non-empty node list.")

        seen: set[str] = set()
        for node in nodes:
            if not isinstance(node, dict):
                raise PinnedRegistryError("Pinned registry node must be an object.")
            node_id = node.get("node_id")
            if not isinstance(node_id, str) or node_id in seen:
                raise PinnedRegistryError(f"Invalid or duplicate node_id: {node_id!r}")
            if node.get("registry_version") != self.EXPECTED_VERSION:
                raise PinnedRegistryError(f"Node {node_id} registry_version mismatch.")

            uds_mapping = node.get("uds_mapping")
            if not isinstance(uds_mapping, dict):
                raise PinnedRegistryError(f"Node {node_id} lacks uds_mapping.")
            if uds_mapping.get("authority") != "INTERPRETIVE_ONLY":
                raise PinnedRegistryError(
                    f"Node {node_id} exceeds INTERPRETIVE_ONLY authority."
                )
            if uds_mapping.get("sovereignty_exit_preserved") is not True:
                raise PinnedRegistryError(
                    f"Node {node_id} does not preserve sovereign exit."
                )

            recognition = node.get("recognition")
            if not isinstance(recognition, dict):
                raise PinnedRegistryError(f"Node {node_id} lacks recognition metadata.")
            themes = recognition.get("themes")
            reason_codes = recognition.get("reason_codes")
            if not isinstance(themes, list) or not all(
                isinstance(theme, str) and theme.strip() for theme in themes
            ):
                raise PinnedRegistryError(f"Node {node_id} has invalid recognition themes.")
            if not isinstance(reason_codes, list) or not all(
                isinstance(code, str) and code.strip() for code in reason_codes
            ):
                raise PinnedRegistryError(f"Node {node_id} has invalid reason codes.")

            seen.add(node_id)
            self._node_order.append(node_id)
            self._nodes[node_id] = node

        expected_ids = [f"SC-{index:03d}" for index in range(10)]
        if self._node_order != expected_ids:
            raise PinnedRegistryError(
                "First Nine registry order mismatch: " + ", ".join(self._node_order)
            )

        for node_id, node in self._nodes.items():
            related = node.get("related_nodes", [])
            if not isinstance(related, list) or any(
                target not in self._nodes for target in related
            ):
                raise PinnedRegistryError(f"Node {node_id} contains an orphan relation.")

        self.source_repository = str(snapshot.get("source_repository", ""))
        self.source_commit = str(snapshot.get("source_commit", ""))

    @property
    def version(self) -> str:
        return self.EXPECTED_VERSION

    @property
    def constellation(self) -> str:
        return self.EXPECTED_CONSTELLATION

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Return a defensive copy of one canonical node, or None."""

        node = self._nodes.get(node_id)
        if node is None:
            return None
        return json.loads(json.dumps(node))

    def list_nodes(self) -> List[str]:
        """Return canonical node identifiers in pinned order."""

        return list(self._node_order)

    def iter_nodes(self) -> Iterable[Dict[str, Any]]:
        """Yield defensive node copies in pinned order."""

        for node_id in self._node_order:
            node = self.get_node(node_id)
            if node is not None:
                yield node
