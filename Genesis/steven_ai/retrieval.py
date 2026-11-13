"""Small local retrieval layer for StevenAI v1.

This deliberately starts simple and inspectable.  It can later be replaced by an
OpenAI vector store or another retrieval backend without changing the agent contract.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable, List, Tuple


DEFAULT_CORPUS_FILES = (
    "Processed Training Data Package for Steven AI.md",
    "MindStudio Implementation Guide_ Steven AI (Chaos Weaver).md",
    "README.md",
)


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-zA-Z0-9_'-]{3,}", text.lower())
        if token not in {"the", "and", "for", "that", "with", "this", "from", "are", "was", "you", "your"}
    }


def _chunk(text: str, max_chars: int = 2200) -> List[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: List[str] = []
    current: List[str] = []
    size = 0
    for paragraph in paragraphs:
        if current and size + len(paragraph) > max_chars:
            chunks.append("\n\n".join(current))
            current = []
            size = 0
        current.append(paragraph)
        size += len(paragraph)
    if current:
        chunks.append("\n\n".join(current))
    return chunks


class LocalCorpusRetriever:
    """Transparent lexical retriever over StevenAI's checked-in public corpus."""

    def __init__(self, repo_root: Path | None = None):
        if repo_root is None:
            repo_root = Path(__file__).resolve().parents[2]
        self.repo_root = repo_root
        self._chunks: List[Tuple[str, str]] = []
        self._load()

    def _configured_files(self) -> Iterable[Path]:
        configured = os.getenv("STEVENAI_CORPUS_FILES", "").strip()
        names = [x.strip() for x in configured.split(",") if x.strip()] if configured else list(DEFAULT_CORPUS_FILES)
        for name in names:
            path = (self.repo_root / name).resolve()
            try:
                path.relative_to(self.repo_root.resolve())
            except ValueError:
                continue
            if path.is_file() and path.suffix.lower() in {".md", ".txt"}:
                yield path

    def _load(self) -> None:
        for path in self._configured_files():
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for chunk in _chunk(text):
                self._chunks.append((path.name, chunk))

    def search(self, query: str, limit: int = 5) -> List[Tuple[str, str, float]]:
        q = _tokens(query)
        if not q:
            return []
        ranked: List[Tuple[str, str, float]] = []
        for source, chunk in self._chunks:
            c = _tokens(chunk)
            overlap = q & c
            if not overlap:
                continue
            # Simple, deterministic score.  Transparent enough to audit and replace later.
            score = len(overlap) / max(len(q), 1)
            ranked.append((source, chunk, score))
        ranked.sort(key=lambda row: row[2], reverse=True)
        return ranked[:limit]

    def context_for(self, query: str, limit: int = 5) -> str:
        hits = self.search(query, limit=limit)
        if not hits:
            return "No relevant local corpus passage was retrieved."
        blocks = []
        for source, chunk, score in hits:
            blocks.append(f"[SOURCE: {source} | relevance={score:.2f}]\n{chunk}")
        return "\n\n---\n\n".join(blocks)
