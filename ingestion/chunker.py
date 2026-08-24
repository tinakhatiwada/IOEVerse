"""
Text chunker — split documents into chunks with metadata attached.

No Flask dependency.
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def chunk_documents(
    docs: list[Document],
    metadata: dict,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[dict]:
    """
    Split documents into chunks and attach metadata.

    Returns a list of dicts ready for insertion:
        {"content": str, "subject": str, "chapter": str, "page": int | None}
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", "! ", "? ", ", ", " ", ""],
    )

    split_docs = splitter.split_documents(docs)

    chunks = []
    for doc in split_docs:
        chunks.append({
            "content": doc.page_content,
            "subject": metadata["subject"],
            "chapter": metadata["chapter"],
            "page": doc.metadata.get("page"),
        })

    return chunks
