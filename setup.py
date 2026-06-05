"""
setup.py — Run once after pip install to build the vector store.
Usage: python setup.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from ingest import ingest_all
from vector_store import build_vector_store

if __name__ == "__main__":
    print("🔬 Building vector store...\n")
    chunks = ingest_all()
    build_vector_store(chunks, reset=True)
    print("\n✅ Done. Run: streamlit run src/app.py")
