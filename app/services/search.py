"""Pure local search operations over the AuraWealth knowledge corpus."""

import json
from pathlib import Path
from typing import Any


CLUSTER_CENTERS = {
    "tax_planning": (-4.0, 3.0), "risk_management": (-1.5, 3.0),
    "portfolio_rebalancing": (1.5, 3.0), "fixed_income": (4.0, 3.0),
    "estate_planning": (-4.0, -1.0), "alternative_assets": (-1.5, -1.0),
    "liquidity_management": (1.5, -1.0), "sustainable_investing": (4.0, -1.0),
    "regulatory_compliance": (-1.5, -5.0), "macro_economics": (1.5, -5.0),
}


class SearchService:
    def __init__(self, corpus_path: str | Path) -> None:
        self.corpus_path = Path(corpus_path)
        self.chunks: list[dict[str, Any]] = json.loads(self.corpus_path.read_text())

    def keyword_filter(self, query: str, category: str | None = None, year: int | None = None) -> list[dict[str, Any]]:
        if not query:
            return []
        query_words = query.lower().split()
        return [
            chunk for chunk in self.chunks
            if any(word in chunk["text"].lower() or word in chunk["document_title"].lower() for word in query_words)
            and (not category or chunk["category"] == category)
            and (year is None or chunk["recency_year"] == year)
        ]

    def semantic_filter(self, query: str) -> list[dict[str, Any]]:
        if not query:
            return []
        return [
            chunk for chunk in self.chunks
            if any(word in chunk["document_title"].lower() for word in query.lower().split())
        ]

    def hybrid_search(self, query: str, category: str | None = None, year: int | None = None) -> dict[str, Any]:
        keyword_results = self.keyword_filter(query, category, year)
        semantic_results = [
            chunk for chunk in self.semantic_filter(query)
            if (not category or chunk["category"] == category)
            and (year is None or chunk["recency_year"] == year)
        ]
        combined = {chunk["id"]: chunk for chunk in keyword_results}
        for chunk in semantic_results:
            combined[chunk["id"]] = chunk
        ranked_results = sorted(
            ({**chunk, "rerank_score": 1.5 if chunk["recency_year"] == 2026 else 1.0} for chunk in combined.values()),
            key=lambda chunk: chunk["rerank_score"],
            reverse=True,
        )
        return {
            "results": ranked_results,
            "keyword_pool_size": len(keyword_results),
            "semantic_pool_size": len(semantic_results),
        }

    def rerank(self, query: str, category: str | None = None, year: int | None = None) -> list[dict[str, Any]]:
        raw = self.keyword_filter(query, category, year) + self.semantic_filter(query)
        unique = {chunk["id"]: chunk for chunk in raw}
        scored = [
            {**chunk, "rerank_score": 1.5 if chunk["recency_year"] == 2026 else 1.0}
            for chunk in unique.values()
        ]
        return sorted(scored, key=lambda chunk: chunk["rerank_score"], reverse=True)

    def cluster_points(self) -> list[dict[str, Any]]:
        points = []
        for chunk in self.chunks:
            center_x, center_y = CLUSTER_CENTERS[chunk["category"]]
            index = chunk["chunk_index"]
            points.append({
                "id": chunk["id"],
                "category": chunk["category"],
                "cluster_x": chunk.get("cluster_x", round(center_x + ((index % 10) - 4.5) * 0.12, 2)),
                "cluster_y": chunk.get("cluster_y", round(center_y + ((index // 10) - 4.5) * 0.12, 2)),
            })
        return points
