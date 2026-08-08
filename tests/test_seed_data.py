import json
from pathlib import Path


def test_seeded_corpus_has_metadata_and_cluster_coordinates():
    chunks = json.loads(Path("app/kb_chunks.json").read_text())
    assert len(chunks) == 1200
    assert len({chunk["document_title"] for chunk in chunks}) == 12
    assert all({"category", "recency_year", "cluster_x", "cluster_y"} <= chunk.keys() for chunk in chunks)
