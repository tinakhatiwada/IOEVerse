"""
Embedding model initialisation.

Single shared instance so we don't create a new model object per request.
"""

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import settings

_embeddings = None


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Return the shared embedding model instance (lazy init)."""
    global _embeddings
    if _embeddings is None:
        _embeddings = GoogleGenerativeAIEmbeddings(model=settings.EMBEDDING_MODEL)
    return _embeddings


def embed_text(text: str) -> list[float]:
    """Embed a single text string and return the vector."""
    return get_embeddings().embed_query(text)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of text strings."""
    return get_embeddings().embed_documents(texts)
