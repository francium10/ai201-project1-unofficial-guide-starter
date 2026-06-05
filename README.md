# 🧬 Unofficial Biotech/Pharma Internship Guide

> A RAG system that makes student-sourced internship knowledge at Genentech, Merck, Benchling, Veeva, Pfizer, BMS, J&J, Tempus AI, and Recursion searchable and answerable.

---

## What This Is

Official job postings tell you what a role requires. They don't tell you what interviews actually ask, what the day-to-day work looks like, or what the return offer rate is. This project collects that student-generated knowledge and makes it queryable with plain-language questions.

**Example queries:**
- *"What is the interview process like at Benchling?"*
- *"Which companies offer housing stipends?"*
- *"What do regulatory interns actually work on?"*
- *"How technical is the Recursion ML interview?"*

---

## Stack

| Component | Tool |
|-----------|------|
| Embeddings | `sentence-transformers` (all-MiniLM-L6-v2) — local, no API key |
| Vector Store | ChromaDB — local, no account needed |
| LLM | Groq (llama-3.3-70b-versatile) — free tier |
| UI | Streamlit |

---

## Setup

```bash
# 1. Clone and create virtual environment
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
# .venv\Scripts\activate    # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up API key
cp .env.example .env
# Edit .env and add your Groq API key (console.groq.com — free)

# 4. Build the vector store (run once)
python setup.py

# 5. Launch the app
streamlit run src/app.py
```

---

## Document Ingestion Pipeline

10 documents were collected from Reddit (r/biotech, r/cscareerquestions), Glassdoor, and Blind. Each document is a first-person internship experience at a major biotech/pharma company.

**Preprocessing steps:**
1. Load raw `.txt` files
2. Remove excess blank lines and whitespace normalization
3. Extract metadata (company, role type, source title) from document headers
4. Chunk with sliding window (400-char chunks, 80-char overlap)

See `planning.md` for full chunking strategy rationale.

**Embedding model:** `all-MiniLM-L6-v2` — runs locally, 384-dim vectors, strong on English review text. Production alternative: `text-embedding-3-small` (OpenAI) for better multilingual support and quality, at API cost.

---

## Evaluation

See `evaluation/report.md` for the full evaluation report.

**5 test questions evaluated:**
1. Benchling interview process
2. Housing stipends across companies
3. Genentech return offer rate
4. Regulatory intern day-to-day work
5. Recursion ML interview technical depth

**Known failure case:** TC02 (housing stipends across all companies) sometimes retrieves company-specific chunks that miss the General survival guide where stipend comparisons are aggregated. This is a retrieval gap caused by the query not mentioning a specific company — hybrid search (BM25 + semantic) would improve this.

---

## Project Structure

```
unofficial-guide/
├── data/
│   ├── raw/          # 10 source documents
│   ├── processed/    # chunking preview output
│   └── chroma_db/    # vector store (auto-generated)
├── src/
│   ├── ingest.py     # document loading + chunking
│   ├── vector_store.py  # ChromaDB + semantic search
│   ├── rag.py        # Groq LLM + grounded generation
│   ├── app.py        # Streamlit UI
│   └── evaluate.py   # evaluation framework
├── evaluation/
│   └── report.md     # full evaluation report
├── setup.py          # one-time vector store builder
├── planning.md       # design decisions
├── requirements.txt
└── .env.example
```
