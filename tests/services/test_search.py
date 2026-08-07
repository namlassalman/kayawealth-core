from app.services.search import SearchService


def test_search_service_hybrid_deduplicates_and_reranks_recent_chunks():
    service = SearchService("app/kb_chunks.json")
    hybrid = service.hybrid_search("tax")
    assert hybrid["results"]
    assert len({chunk["id"] for chunk in hybrid["results"]}) == len(hybrid["results"])
    assert hybrid["results"][0]["rerank_score"] == 1.5

    reranked = service.rerank("tax")
    assert reranked[0]["rerank_score"] == 1.5
    assert all(chunk["rerank_score"] in (1.0, 1.5) for chunk in reranked)
