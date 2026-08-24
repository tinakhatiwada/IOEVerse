"""
Ingestion runner — standalone script to ingest PDFs into pgvector.

Usage:
    python -m ingestion.run
    python -m ingestion.run --docs-dir /path/to/documents

No Flask dependency.  Reads DATABASE_URL and GOOGLE_API_KEY from .env.
"""

import argparse
import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

# Ensure the project root is on sys.path so `app.*` imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.config import settings  # noqa: E402 — must come after sys.path fix
from app.rag.embeddings import embed_texts  # noqa: E402
from app.repositories import document_repository  # noqa: E402
from ingestion.chunker import chunk_documents  # noqa: E402
from ingestion.loaders import load_pdf, walk_documents  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def ingest(docs_dir: str = "documents") -> None:
    """Walk the documents directory, chunk, embed, and insert into pgvector."""
    if not os.path.isdir(docs_dir):
        logger.error("Documents directory not found: %s", docs_dir)
        logger.info("Create it and add PDFs in the expected folder structure:")
        logger.info("  documents/Subject_Name/chapter_01_chapter_name.pdf")
        return

    total_chunks = 0

    for filepath, meta in walk_documents(docs_dir):
        source = meta["source_filename"]

        # Idempotency: skip already-ingested files
        if document_repository.document_exists(source):
            logger.info("⏭  Already ingested: %s", source)
            continue

        logger.info("Processing: %s  [%s / %s]", source, meta["subject"], meta["chapter"])

        # Load PDF
        pages = load_pdf(filepath)
        if not pages:
            logger.warning("   No pages loaded — skipping")
            continue

        # Chunk
        chunks = chunk_documents(pages, meta, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
        if not chunks:
            logger.warning("   No chunks produced — skipping")
            continue

        # Embed
        texts = [c["content"] for c in chunks]
        logger.info("   Embedding %d chunks...", len(texts))
        embeddings = embed_texts(texts)

        # Insert document record
        doc_id = document_repository.insert_document(
            subject=meta["subject"],
            chapter=meta["chapter"],
            source_filename=source,
        )

        # Attach doc_id and embeddings to chunks, then insert
        for chunk, emb in zip(chunks, embeddings):
            chunk["document_id"] = doc_id
            chunk["embedding"] = emb

        inserted = document_repository.insert_chunks(chunks)
        total_chunks += inserted
        logger.info(" Inserted %d chunks (doc_id=%d)", inserted, doc_id)

    if total_chunks:
        logger.info("Ingestion complete — %d total chunks inserted", total_chunks)
    else:
        logger.info("No new documents to ingest")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest PDFs into pgvector")
    parser.add_argument(
        "--docs-dir",
        default="documents",
        help="Path to the documents directory (default: documents/)",
    )
    args = parser.parse_args()
    ingest(args.docs_dir)
