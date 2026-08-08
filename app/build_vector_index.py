"""One-time local embedding-index build command for AuraWealth."""

from pathlib import Path

from app.services.vector_index import LocalEmbeddingIndex, MODEL_NAME


def main() -> None:
    app_directory = Path(__file__).resolve().parent
    index = LocalEmbeddingIndex(app_directory / "kb_chunks.json", app_directory / "kb_vectors.npz")
    vectors = index._load_or_build_vectors()
    print(f"Built local {MODEL_NAME} index: {len(vectors)} chunks × {vectors.shape[1]} dimensions")


if __name__ == "__main__":
    main()
