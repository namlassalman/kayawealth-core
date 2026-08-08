from app.services.search import SearchService


def test_search_service_hybrid_deduplicates_and_reranks_recent_chunks():
    service = SearchService("app/kb_chunks.json", semantic_index=FakeSemanticIndex())
    hybrid = service.hybrid_search("tax")
    assert hybrid["results"]
    assert len({chunk["id"] for chunk in hybrid["results"]}) == len(hybrid["results"])
    assert hybrid["results"][0]["rerank_score"] == 1.5
    assert hybrid["results"][0]["id"] == "semantic_result"

    reranked = service.rerank("tax")
    assert reranked[0]["rerank_score"] == 1.5
    assert all(chunk["rerank_score"] in (1.0, 1.5) for chunk in reranked)


def test_real_local_embedding_search_matches_retirement_synonym():
    service = SearchService("app/kb_chunks.json")
    result = service.semantic_filter("life after work financial security")[0]
    assert result["category"] == "retirement_planning"
    assert result["semantic_score"] > 0.5


class FakeSemanticIndex:
    def search(self, query, category=None, year=None, limit=50):
        return [{
            "id": "semantic_result", "document_title": "Semantic retirement match", "category": category or "retirement_planning",
            "text": "Retirement planning guidance", "recency_year": year or 2026, "semantic_score": 0.91,
        }]
