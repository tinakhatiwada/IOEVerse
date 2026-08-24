"""
Metadata parser — extract subject and chapter from folder/filename convention.

Expected structure:
    documents/
      Digital_Logic/
        chapter_01_number_systems.pdf
      Programming_in_C/
        chapter_03_variables_and_data_types.pdf

Subject = folder name (underscores → spaces, title-cased).
Chapter = everything after `chapter_NN_` (underscores → spaces, title-cased).
"""

import os
import re


def parse_path(filepath: str) -> dict:
    """
    Parse a file path into subject and chapter metadata.

    Returns {"subject": str, "chapter": str, "source_filename": str}.
    Raises ValueError if the path doesn't match the expected convention.
    """
    # Normalise separators
    parts = os.path.normpath(filepath).replace("\\", "/").split("/")

    # We need at least: .../Subject_Folder/chapter_NN_name.pdf
    if len(parts) < 2:
        raise ValueError(f"Path too short to extract metadata: {filepath}")

    # Subject from parent folder
    subject_raw = parts[-2]
    subject = subject_raw.replace("_", " ").title()

    # Chapter from filename
    filename = os.path.splitext(parts[-1])[0]  # strip extension
    match = re.match(r"chapter_(\d+)_(.+)", filename, re.IGNORECASE)
    if match:
        chapter_raw = match.group(2)
        chapter = chapter_raw.replace("_", " ").title()
    else:
        # Fallback: use the whole filename as chapter name
        chapter = filename.replace("_", " ").title()

    return {
        "subject": subject,
        "chapter": chapter,
        "source_filename": parts[-1],
    }
