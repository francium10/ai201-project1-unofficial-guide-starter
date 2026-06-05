"""
ingest.py — Document ingestion and chunking pipeline
Loads all .txt files from documents/, cleans them, and splits into chunks.

Chunking strategy:
  - Chunk size: 400 characters
  - Overlap:    80 characters
  - Rationale: Our documents are review-style (Reddit/Glassdoor posts).
    Key facts — interview rounds, salaries, return rates — appear in
    short 1–3 sentence bursts. 400-char chunks capture ~one topic unit
    without mixing multiple ideas. 80-char overlap prevents facts from
    being cut across chunk boundaries.
"""

import os
import re
from dataclasses import dataclass
from typing import List

# Path relative to project root
DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), "../documents")

CHUNK_SIZE = 400
CHUNK_OVERLAP = 80


@dataclass
class Chunk:
    chunk_id: str
    source_file: str
    source_title: str
    company: str
    role_type: str
    text: str


def extract_metadata(filename: str, text: str) -> dict:
    """Extract company, role type, and title from document header."""
    meta = {"source_title": "", "company": "General", "role_type": "general"}

    for line in text.split("\n")[:6]:
        if line.startswith("Title:"):
            meta["source_title"] = line.replace("Title:", "").strip()

    fname = filename.lower()
    company_map = {
        "genentech": "Genentech",
        "veeva": "Veeva Systems",
        "benchling": "Benchling",
        "merck": "Merck",
        "pfizer": "Pfizer",
        "tempus": "Tempus AI",
        "bms": "Bristol Myers Squibb",
        "jnj": "Johnson & Johnson",
        "recursion": "Recursion Pharmaceuticals",
    }
    for key, name in company_map.items():
        if key in fname:
            meta["company"] = name
            break

    title = meta["source_title"].lower()
    if any(w in title for w in ["software", "swe", "ml", "data", "bioinformatics"]):
        meta["role_type"] = "technical"
    elif any(w in title for w in ["regulatory", "cmc", "affairs"]):
        meta["role_type"] = "regulatory"

    return meta


def clean_text(text: str) -> str:
    """Normalize whitespace and remove excessive blank lines."""
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


def chunk_text(text: str) -> List[tuple]:
    """
    Sliding window chunker with sentence-boundary snapping.
    Returns list of (chunk_text, start, end).
    """
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        # Snap to sentence boundary within ±50 chars if possible
        if end < len(text):
            boundary = text.rfind('. ', start, end + 50)
            if boundary > start + CHUNK_SIZE // 2:
                end = boundary + 1
        chunk = text[start:end].strip()
        if chunk:
            chunks.append((chunk, start, end))
        start = end - CHUNK_OVERLAP
        if start >= len(text):
            break
    return chunks


def ingest_all() -> List[Chunk]:
    """Load, clean, and chunk all documents. Returns flat list of Chunks."""
    all_chunks: List[Chunk] = []
    files = sorted(f for f in os.listdir(DOCUMENTS_DIR) if f.endswith(".txt"))

    print(f"📂 Found {len(files)} documents\n")

    for filename in files:
        path = os.path.join(DOCUMENTS_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()

        meta = extract_metadata(filename, raw)
        clean = clean_text(raw)
        text_chunks = chunk_text(clean)

        for i, (text, start, end) in enumerate(text_chunks):
            all_chunks.append(Chunk(
                chunk_id=f"{filename.replace('.txt', '')}__chunk_{i:03d}",
                source_file=filename,
                source_title=meta["source_title"],
                company=meta["company"],
                role_type=meta["role_type"],
                text=text,
            ))

        print(f"  ✓ {filename}: {len(text_chunks)} chunks")

    print(f"\n✅ Total chunks: {len(all_chunks)}")
    return all_chunks


if __name__ == "__main__":
    chunks = ingest_all()
    print(f"\n--- Sample chunk ---")
    print(chunks[0].text[:300])
