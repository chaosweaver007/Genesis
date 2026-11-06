from pathlib import Path

from Genesis.steven_ai.canon import CANONICAL_INVARIANTS, STEVENAI_INSTRUCTIONS
from Genesis.steven_ai.retrieval import LocalCorpusRetriever


def test_canonical_direction_is_locked():
    assert "Chaos -> Order -> Harmonization" in CANONICAL_INVARIANTS
    assert "Harmonization preserves distinction" in CANONICAL_INVARIANTS


def test_epistemic_boundary_is_present():
    assert "Epistemic Boundary" in CANONICAL_INVARIANTS
    assert "Do not present metaphor" in CANONICAL_INVARIANTS
    assert "provider replaceable" in STEVENAI_INSTRUCTIONS


def test_retriever_does_not_escape_repo_root(tmp_path: Path):
    corpus = tmp_path / "README.md"
    corpus.write_text("StevenAI sovereignty privacy truth architecture", encoding="utf-8")
    retriever = LocalCorpusRetriever(repo_root=tmp_path)
    hits = retriever.search("privacy architecture")
    assert hits
    assert hits[0][0] == "README.md"
