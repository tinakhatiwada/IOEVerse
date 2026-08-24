"""
Document loaders — walk the documents directory, load PDFs.

No Flask dependency.  Uses PyPDFLoader from langchain_community.
"""

import logging
import os
from typing import Generator, Tuple

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from ingestion.metadata import parse_path

logger = logging.getLogger(__name__)


def walk_documents(
    docs_dir: str = "documents",
) -> Generator[Tuple[str, dict], None, None]:
    """
    Walk the documents directory and yield (filepath, metadata) pairs.

    Only yields .pdf files.
    """
    for root, _dirs, files in os.walk(docs_dir):
        for filename in sorted(files):
            if not filename.lower().endswith(".pdf"):
                continue
            filepath = os.path.join(root, filename)
            try:
                meta = parse_path(filepath)
                yield filepath, meta
            except ValueError as e:
                logger.warning("Skipping %s: %s", filepath, e)


def load_pdf(filepath: str) -> list[Document]:
    """Load a PDF and return a list of langchain Documents (one per page)."""
    loader = PyPDFLoader(filepath)
    return loader.load()
