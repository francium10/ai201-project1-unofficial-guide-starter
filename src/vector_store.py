"""
vector_store.py — Embed chunks and store in ChromaDB for semantic search.

Embedding model: all-MiniLM-L6-v2 (sentence-transformers)
  - Runs fully locally — no API key, no cost, no rate limits
  - 384-dimensional vectors, strong on English review text
  - Production alternative: text-embedding-3-small (OpenAI) for better
    multilingual support and quality, at API cost (~$0.02/1M tokens)
"""

from typing import List
from ingest import Chunk, ingest_all
import os
import sys

# Ensure the src directory is on sys.path so local imports work when
# running the script from the project root.
sys.path.insert(0, os.path.dirname(__file__))


# Optional heavy dependencies — provide a clearer message if they're missing.
try:
    import chromadb
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
except ModuleNotFoundError as e:
    print(
        "Missing dependency: {}. Install required packages with: pip install -r requirements.txt".format(
            e.name)
    )
    sys.exit(1)

CHROMA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "chroma_db")
)

# Ensure the persistent DB directory exists
os.makedirs(CHROMA_PATH, exist_ok=True)
COLLECTION_NAME = "biotech_internships"


def get_collection(reset: bool = False):
    """Return the ChromaDB collection, creating it if needed."""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    embed_fn = SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2")

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            print("🗑  Cleared existing collection.")
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


def build_vector_store(chunks: List[Chunk], reset: bool = True):
    """Embed and index all chunks into ChromaDB."""
    collection = get_collection(reset=reset)

    if collection.count() > 0 and not reset:
        print(f"Collection already has {collection.count()} docs. Skipping.")
        return collection

    print(f"⚙️  Embedding {len(chunks)} chunks (this takes ~30s first run)...")

    BATCH = 50
    for i in range(0, len(chunks), BATCH):
        batch = chunks[i:i + BATCH]
        collection.add(
            ids=[c.chunk_id for c in batch],
            documents=[c.text for c in batch],
            metadatas=[{
                "source_file": c.source_file,
                "source_title": c.source_title,
                "company": c.company,
                "role_type": c.role_type,
            } for c in batch],
        )
    print(f"✅ Indexed {collection.count()} chunks.")
    return collection


def semantic_search(query: str, n_results: int = 4, company_filter: str = None):
    """
    Retrieve top-n chunks by cosine similarity.
    Returns list of dicts: text, source, company, role_type, score.
    """
    collection = get_collection(reset=False)

    where = None
    if company_filter and company_filter != "All":
        where = {"company": company_filter}

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({
            "text": doc,
            "source": meta.get("source_title") or meta.get("source_file", "Unknown"),
            "company": meta.get("company", "Unknown"),
            "role_type": meta.get("role_type", ""),
            "score": round(1 - dist, 4),
        })

    return hits


if __name__ == "__main__":
    chunks = ingest_all()
    build_vector_store(chunks, reset=True)

    print("\n--- Smoke test ---")
    hits = semantic_search(
        "What is the interview process at Benchling?", n_results=3)
    for h in hits:
        print(f"\n[{h['company']}] score={h['score']}")
        print(h["text"][:200])
