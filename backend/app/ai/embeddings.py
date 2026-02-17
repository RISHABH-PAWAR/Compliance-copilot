"""Embedding Generation Module"""
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.core.config import settings
from functools import lru_cache

@lru_cache()
def get_embeddings():
    """
    Returns the configured embedding model.
    Uses local HuggingFace embeddings (all-MiniLM-L6-v2) by default.
    """
    model_name = settings.EMBEDDING_MODEL
    # Local fallback if not specified
    if not model_name: 
        model_name = "all-MiniLM-L6-v2"
        
    return HuggingFaceEmbeddings(model_name=model_name)
