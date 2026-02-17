"""Pinecone Vector Store Operations"""
from typing import List, Dict, Optional
from app.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger("vectorstore")


class VectorStoreService:
    """Manages Pinecone vector store for policy and regulation embeddings"""

    def __init__(self):
        self._index = None

    @property
    def index(self):
        if self._index is None and settings.PINECONE_API_KEY:
            try:
                from pinecone import Pinecone
                pc = Pinecone(api_key=settings.PINECONE_API_KEY)
                self._index = pc.Index(settings.PINECONE_INDEX_NAME)
            except Exception as e:
                logger.warning("pinecone_connection_failed", error=str(e))
        return self._index

    def upsert(self, vectors: List[Dict], namespace: str = "default") -> bool:
        """Upsert vectors to Pinecone with namespace isolation"""
        if not self.index:
            logger.info("pinecone_skip", reason="no_connection", namespace=namespace)
            return False

        try:
            self.index.upsert(vectors=vectors, namespace=namespace)
            logger.info("pinecone_upsert", count=len(vectors), namespace=namespace)
            return True
        except Exception as e:
            logger.error("pinecone_upsert_error", error=str(e))
            return False

    def search(self, query: str, namespace: str = "default", top_k: int = 10) -> List[Dict]:
        """Search for similar vectors"""
        if not self.index:
            return []

        try:
            from app.ai.embeddings import get_embeddings
            embeddings = get_embeddings()
            query_embedding = embeddings.embed_query(query)

            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=namespace,
                include_metadata=True,
            )

            return [
                {"id": match.id, "score": match.score, **match.metadata}
                for match in results.matches
            ]
        except Exception as e:
            logger.error("pinecone_search_error", error=str(e))
            return []

    def delete_by_filter(self, filter_dict: Dict, namespace: str = "default") -> bool:
        """Delete vectors by metadata filter"""
        if not self.index:
            return False
        try:
            self.index.delete(filter=filter_dict, namespace=namespace)
            logger.info("pinecone_delete_filter", filter=filter_dict, namespace=namespace)
            return True
        except Exception as e:
            logger.error("pinecone_delete_error", error=str(e))
            return False

    def delete_namespace(self, namespace: str) -> bool:
        """Delete all vectors in a namespace (for tenant data deletion)"""
        if not self.index:
            return False
        try:
            self.index.delete(delete_all=True, namespace=namespace)
            return True
        except Exception as e:
            logger.error("pinecone_delete_error", error=str(e))
            return False
