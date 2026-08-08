import json

import numpy as np

from app.services.vector_index import LocalEmbeddingIndex


class FakeEmbeddingModel:
    def passage_embed(self, texts, **_kwargs):
        for text in texts:
            yield np.array([1.0, 0.0]) if "retirement" in text.lower() else np.array([0.0, 1.0])

    def query_embed(self, texts):
        for text in texts:
            yield np.array([1.0, 0.0]) if "pension" in text.lower() else np.array([0.0, 1.0])


def test_local_vector_index_retrieves_semantic_match_and_persists_vectors(tmp_path):
    corpus_path = tmp_path / "chunks.json"
    corpus_path.write_text(json.dumps([
        {"id": "retirement", "text": "Retirement income planning", "category": "retirement_planning", "recency_year": 2026},
        {"id": "tax", "text": "Tax deduction guidance", "category": "tax_planning", "recency_year": 2024},
    ]))
    index_path = tmp_path / "vectors.npz"
    index = LocalEmbeddingIndex(corpus_path, index_path, embedding_model=FakeEmbeddingModel())

    results = index.search("pension income", limit=1)

    assert results[0]["id"] == "retirement"
    assert results[0]["semantic_score"] == 1.0
    assert index_path.exists()
