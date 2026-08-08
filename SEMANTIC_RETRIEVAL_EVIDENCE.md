# Task 33 — Local Semantic Retrieval Evidence

## Implementation decision

AuraWealth uses `fastembed` with the local CPU ONNX model
`BAAI/bge-small-en-v1.5`. The model maps corpus passages and queries into
384-dimensional dense vectors. A normalized NumPy matrix is persisted as
`app/kb_vectors.npz`; cosine similarity ranks matching chunks. The index is
rebuilt when a fingerprint of the corpus changes.

This is a local vector index, not Qdrant/Chroma and not an external embedding
API. The initial public model download is a setup step; corpus and query text
remain on-device while the application runs.

## Corpus and hybrid retrieval

- 1,200 generated chunks from 12 simulated source documents.
- Keyword retrieval remains available for exact terms and metadata filtering.
- Local embedding retrieval supplies semantic candidates with
  `semantic_score` (cosine similarity).
- Hybrid retrieval deduplicates by chunk ID, then applies the existing
  recency score: 2026 = 1.5; 2024 = 1.0.

## Reproducible semantic check

```bash
venv/bin/python -m app.build_vector_index
venv/bin/pytest tests/services/test_search.py -q
```

The test `test_real_local_embedding_search_matches_retirement_synonym` queries
`life after work financial security`. It does not contain the word
`retirement`; the top local-vector result is nevertheless in the
`retirement_planning` category with cosine similarity above 0.5.

## Metrics and limitations

The visible retrieval metric is cosine similarity, a directional measure from
-1 to 1 after L2 normalization; higher is more semantically similar. The
corpus is simulated and the test is a targeted regression check, not a
benchmark of financial-advice quality. No model output is investment advice.
