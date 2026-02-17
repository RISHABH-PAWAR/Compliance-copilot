"""Document Chunk - MongoDB Model"""
from datetime import datetime


class DocumentChunk:
    """Schema for chunked document text stored in MongoDB"""
    
    COLLECTION = "document_chunks"
    
    @staticmethod
    def create(
        document_id: str,
        company_id: int,
        chunk_index: int,
        text: str,
        **kwargs
    ) -> dict:
        return {
            "document_id": document_id,
            "company_id": company_id,
            "chunk_index": chunk_index,
            "text": text,
            "token_count": kwargs.get("token_count", 0),
            
            # Metadata for retrieval
            "policy_type": kwargs.get("policy_type", ""),
            "state": kwargs.get("state", "all"),
            "section_title": kwargs.get("section_title", ""),
            
            # Embedding reference
            "pinecone_id": kwargs.get("pinecone_id", ""),
            "embedding_model": kwargs.get("embedding_model", "text-embedding-3-small"),
            
            "created_at": datetime.utcnow(),
        }
