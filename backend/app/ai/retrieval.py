"""Hybrid Retrieval System - BM25 + Pinecone Vector Search"""
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
from app.ai.vectorstore import VectorStoreService
from app.core.logging import get_logger

logger = get_logger("retrieval")


class HybridRetrieval:
    """Combines BM25 keyword search with Pinecone semantic search"""

    def __init__(self, bm25_weight: float = 0.3, vector_weight: float = 0.7):
        self.bm25_weight = bm25_weight
        self.vector_weight = vector_weight
        self.vectorstore = VectorStoreService()

    def search(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        namespace: str = "regulations",
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining BM25 and vector similarity.
        
        Args:
            query: Search query text
            documents: List of documents with 'text' field for BM25
            namespace: Pinecone namespace for vector search
            top_k: Number of results to return
        """
        # BM25 keyword search
        bm25_results = self._bm25_search(query, documents, top_k)
        
        # Vector search via Pinecone
        vector_results = self.vectorstore.search(query, namespace, top_k)
        
        # Merge and re-rank results
        merged = self._merge_results(bm25_results, vector_results, top_k)
        
        logger.info("hybrid_search", query=query[:100], bm25_count=len(bm25_results),
                    vector_count=len(vector_results), merged_count=len(merged))
        
        return merged

    def _bm25_search(self, query: str, documents: List[Dict], top_k: int) -> List[Dict]:
        """BM25 keyword matching - great for legal terms"""
        if not documents:
            return []

        tokenized_docs = [doc.get("text", "").lower().split() for doc in documents]
        bm25 = BM25Okapi(tokenized_docs)
        
        tokenized_query = query.lower().split()
        scores = bm25.get_scores(tokenized_query)
        
        scored_docs = list(zip(documents, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        return [
            {**doc, "bm25_score": float(score), "source": "bm25"}
            for doc, score in scored_docs[:top_k]
            if score > 0
        ]

    def _merge_results(
        self,
        bm25_results: List[Dict],
        vector_results: List[Dict],
        top_k: int,
    ) -> List[Dict]:
        """Merge and re-rank BM25 + vector results using weighted scoring"""
        seen = {}
        
        for doc in bm25_results:
            doc_id = doc.get("id", doc.get("text", "")[:50])
            if doc_id not in seen:
                seen[doc_id] = {"doc": doc, "bm25_score": doc.get("bm25_score", 0), "vector_score": 0}
            else:
                seen[doc_id]["bm25_score"] = doc.get("bm25_score", 0)

        for doc in vector_results:
            doc_id = doc.get("id", doc.get("text", "")[:50])
            if doc_id not in seen:
                seen[doc_id] = {"doc": doc, "bm25_score": 0, "vector_score": doc.get("score", 0)}
            else:
                seen[doc_id]["vector_score"] = doc.get("score", 0)

        # Calculate hybrid score
        merged = []
        for doc_id, data in seen.items():
            hybrid_score = (
                self.bm25_weight * data["bm25_score"] +
                self.vector_weight * data["vector_score"]
            )
            merged.append({
                **data["doc"],
                "hybrid_score": hybrid_score,
                "bm25_score": data["bm25_score"],
                "vector_score": data["vector_score"],
            })

        merged.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return merged[:top_k]
