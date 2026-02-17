from langchain_groq import ChatGroq
from app.core.config import settings
from functools import lru_cache

@lru_cache()
def get_llm(temperature: float = 0.0, model: str = None):
    """
    Get the configured LLM instance.
    Uses Groq by default for open-source models (Llama 3).
    """
    # Default to Llama 3 70b for best reasoning, or user specified
    model_name = model or settings.DEFAULT_LLM_MODEL or "llama3-70b-8192"
    
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model_name=model_name,
        temperature=temperature
    )

def get_cheap_llm():
    """Returns a faster/cheaper model for simple tasks"""
    return get_llm(temperature=0.0, model="llama3-8b-8192")
