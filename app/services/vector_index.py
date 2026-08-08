"""Local ONNX embedding index with persisted cosine-similarity vectors."""

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import numpy as np
from fastembed import TextEmbedding


MODEL_NAME = "BAAI/bge-small-en-v1.5"


class LocalEmbeddingIndex:
    """Embed corpus passages locally and persist normalized vectors as `.npz`."""

    def __init__(
        self,
        corpus_path: str | Path,
        index_path: str | Path,
        *,
        model_name: str = MODEL_NAME,
        embedding_model: TextEmbedding | Any | None = None,
    ) -> None:
        self.corpus_path = Path(corpus_path)
        self.index_path = Path(index_path)
        self.model_name = model_name
        self._embedding_model = embedding_model
        self.chunks: list[dict[str, Any]] = json.loads(self.corpus_path.read_text())
        self._vectors: np.ndarray | None = None

    def search(
        self,
        query: str,
        category: str | None = None,
        year: int | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        if not query.strip():
            return []
        vectors = self._load_or_build_vectors()
        query_vector = np.asarray(next(self._model().query_embed([query])), dtype=np.float32)
        query_vector = _normalize(query_vector)
        scores = vectors @ query_vector
        ranked_indices = np.argsort(scores)[::-1]

        results = []
        for index in ranked_indices:
            chunk = self.chunks[int(index)]
            if category and chunk["category"] != category:
                continue
            if year is not None and chunk["recency_year"] != year:
                continue
            results.append({**chunk, "semantic_score": round(float(scores[index]), 4)})
            if len(results) == limit:
                break
        return results

    def _load_or_build_vectors(self) -> np.ndarray:
        if self._vectors is not None:
            return self._vectors
        corpus_hash = self._corpus_hash()
        if self.index_path.exists():
            with np.load(self.index_path, allow_pickle=False) as stored:
                stored_hash = str(stored["corpus_hash"].item())
                vectors = stored["vectors"]
            if stored_hash == corpus_hash and len(vectors) == len(self.chunks):
                self._vectors = vectors.astype(np.float32)
                return self._vectors

        passages = [f"{chunk.get('document_title', '')}\n{chunk['text']}" for chunk in self.chunks]
        # The generated corpus intentionally repeats an educational scenario
        # across metadata variants. Embed each distinct passage once, then map
        # that vector back to every matching chunk; this keeps a local rebuild
        # practical on presentation hardware without changing retrieval logic.
        unique_passages = list(dict.fromkeys(passages))
        unique_vectors = np.asarray(
            list(self._model().passage_embed(unique_passages, batch_size=128)),
            dtype=np.float32,
        )
        vector_by_passage = dict(zip(unique_passages, unique_vectors))
        vectors = np.asarray([vector_by_passage[passage] for passage in passages], dtype=np.float32)
        self._vectors = _normalize_rows(vectors)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.index_path.with_suffix(".tmp")
        with temporary_path.open("wb") as index_file:
            np.savez_compressed(index_file, corpus_hash=corpus_hash, vectors=self._vectors)
        os.replace(temporary_path, self.index_path)
        return self._vectors

    def _model(self):
        if self._embedding_model is None:
            self._embedding_model = TextEmbedding(model_name=self.model_name, threads=2)
        return self._embedding_model

    def _corpus_hash(self) -> str:
        fingerprint = [{"id": chunk["id"], "text": chunk["text"]} for chunk in self.chunks]
        return hashlib.sha256(json.dumps(fingerprint, sort_keys=True).encode()).hexdigest()


def _normalize(vector: np.ndarray) -> np.ndarray:
    magnitude = np.linalg.norm(vector)
    return vector if magnitude == 0 else vector / magnitude


def _normalize_rows(vectors: np.ndarray) -> np.ndarray:
    magnitudes = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.where(magnitudes == 0, 1, magnitudes)
