"""Policy Document - MongoDB Model"""
from datetime import datetime
from typing import Optional, List, Dict


class PolicyDocument:
    """Schema for company policy documents stored in MongoDB"""
    
    COLLECTION = "policy_documents"
    
    @staticmethod
    def create(
        company_id: int,
        filename: str,
        policy_type: str,
        state: str = "all",
        **kwargs
    ) -> dict:
        return {
            "company_id": company_id,
            "filename": filename,
            "original_filename": kwargs.get("original_filename", filename),
            "policy_type": policy_type,  # wage_policy, shift_policy, overtime_policy, attendance, handbook, leave_policy
            "state": state,
            "version": kwargs.get("version", 1),
            "status": kwargs.get("status", "processing"),  # processing, processed, failed
            
            # Content
            "raw_text": kwargs.get("raw_text", ""),
            "content_hash": kwargs.get("content_hash", ""),
            "file_size": kwargs.get("file_size", 0),
            "file_type": kwargs.get("file_type", "pdf"),  # pdf, docx, txt
            
            # Metadata
            "tags": kwargs.get("tags", []),
            "department": kwargs.get("department", ""),
            "uploaded_by": kwargs.get("uploaded_by", None),
            
            # Processing
            "chunk_count": kwargs.get("chunk_count", 0),
            "embedding_status": kwargs.get("embedding_status", "pending"),
            "pinecone_namespace": f"company_{company_id}",
            
            # Encryption
            "is_encrypted": kwargs.get("is_encrypted", True),
            
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
