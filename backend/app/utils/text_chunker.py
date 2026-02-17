"""Text Chunking Strategies"""
from typing import List
import tiktoken


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[dict]:
    """Split text into overlapping chunks with token counting"""
    enc = tiktoken.get_encoding("cl100k_base")
    words = text.split()
    chunks = []
    i = 0
    idx = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunk_text = " ".join(chunk_words)
        token_count = len(enc.encode(chunk_text))
        chunks.append({"text": chunk_text, "chunk_index": idx, "token_count": token_count, "start_word": i})
        i += chunk_size - overlap
        idx += 1
    return chunks
