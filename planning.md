# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

**Biotech and pharma internship experiences** — the honest, student-sourced knowledge that official job postings never include: what interviews actually ask, what the day-to-day work looks like, how much you'll get paid, whether you'll get a return offer, and what nobody warns you about before you show up.

This knowledge is hard to find because it is fragmented across Reddit threads, Glassdoor reviews, Blind posts, and personal blogs. None of those platforms let you ask a plain-language question and get a grounded, cross-company answer. A student asking "which companies offer housing stipends?" has to manually search five different sites and reconcile conflicting information. This RAG system makes all of that searchable in one place.

---

## Documents

| #  | Source | Description | URL or location |
|----|--------|-------------|-----------------|
| 1  | Reddit r/biotech | First-person intern experience at Genentech — bioprocess role, interview rounds, pay, culture | documents/genentech_intern_reddit.txt |
| 2  | Glassdoor | Software Engineer intern review at Veeva Systems — SaaS stack, Generation Veeva program, interview tips | documents/veeva_intern_glassdoor.txt |
| 3  | Reddit r/cscareerquestions | Benchling SWE intern writeup — 4 interview rounds, FastAPI/React stack, SF cost of living | documents/benchling_intern_reddit.txt |
| 4  | Glassdoor | Merck Regulatory Affairs intern — IND/NDA work, ICH guidelines, Veeva Vault, Rahway NJ | documents/merck_regulatory_intern.txt |
| 5  | Blind + Reddit | Pfizer Data Science intern — clinical ML model, compliance onboarding, NYC hybrid | documents/pfizer_datascience_intern.txt |
| 6  | Reddit r/cscareerquestions | Tempus AI bioinformatics intern — VCF pipeline, precision medicine mission, Chicago | documents/tempus_ai_intern.txt |
| 7  | Glassdoor | Bristol Myers Squibb CMC Regulatory intern — BLA filing, Summer Scholars program, NJ | documents/bms_regulatory_intern.txt |
| 8  | Reddit + LinkedIn | J&J MedTech Regulatory intern — 510(k) submission, predicate device analysis, Santa Clara | documents/jnj_medtech_intern.txt |
| 9  | Reddit + personal blog | Recursion Pharmaceuticals ML intern — cell morphology models, PyTorch, 5-round interview | documents/recursion_ml_intern.txt |
| 10 | r/biotech community wiki | Compiled survival guide — pay benchmarks, return offer rates, timeline tips, common mistakes | documents/biotech_internship_survival_guide.txt |

---

## Chunking Strategy

**Chunk size:** 400 characters

**Overlap:** 80 characters

**Reasoning:**
Our documents are review-style first-person narratives (Reddit posts, Glassdoor reviews). Key facts — interview round counts, salary figures, return offer rates, specific tools used — appear in short, concentrated bursts of 1–3 sentences. A 400-character window captures roughly one "topic unit" without mixing multiple unrelated ideas into the same chunk. For example, a chunk about compensation should not also contain text about culture fit — they answer different questions and mixing them hurts retrieval precision.

The 80-character overlap ensures that sentences split at a chunk boundary are fully captured by at least one chunk. Without overlap, a sentence like "The return offer rate is approximately 40-50% for strong performers" could be split so that neither chunk contains the full fact.

We also apply sentence-boundary snapping: when the sliding window lands mid-sentence, we scan forward up to 50 characters for the nearest period and extend the boundary there. This keeps chunks semantically clean without requiring a full semantic chunker.

**Final chunk count:** ~110–130 chunks across 10 documents (varies by document length)

---

## Retrieval Approach

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers`

**Top-k:** 4 chunks per query (configurable in the UI, range 2–6)

**Production tradeoff reflection:**

| Model | Pros | Cons |
|-------|------|------|
| `all-MiniLM-L6-v2` | Free, runs fully locally, no API key, fast (~30ms/query), 384-dim | English-only, smaller model capacity |
| `text-embedding-3-small` (OpenAI) | Higher quality, multilingual support | API cost (~$0.02/1M tokens), rate limits, requires key |
| `embed-v3` (Cohere) | Best multilingual, long context window | API cost, external dependency |

For this project, `all-MiniLM-L6-v2` is the right choice — our corpus is English-only, fits entirely in memory, and local execution means zero latency variance. For a production system serving international applicants (e.g., students from India, Africa, or Latin America asking about US internships), Cohere `embed-v3` would be worth the cost for multilingual support.

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What is the interview process like at Benchling? | 4 rounds: recruiter screen → 2 LeetCode mediums → system design (life-sciences prompt) → behavioral with EM. Domain knowledge tested in at least one round. |
| 2 | Which companies offer housing stipends and how much? | Genentech $2,000 · Merck $3,000 · BMS $2,500 · J&J $2,000 · Veeva no stipend (relocation $2,500) · Benchling no stipend · ~60% of Big Pharma offer stipends per survival guide. |
| 3 | What is the return offer rate at Genentech? | Approximately 40–50% for strong performers, per the community survival guide. |
| 4 | What does a regulatory affairs intern actually work on day to day? | Document review, FDA guidance documents, cross-functional meetings (clinical/CMC/regulatory), Veeva Vault document management, learning ICH guidelines, contributing to IND/NDA/BLA/510k submission sections. |
| 5 | How technical is the Recursion Pharmaceuticals ML interview? | 5 rounds including ML fundamentals (bias-variance, regularization, probability), Python ML coding (not LeetCode — write actual model code), a research paper presentation round, and team fit. Described as rigorous. |

---

## Anticipated Challenges

1. **Multi-company queries will compete for retrieval slots.** A question like "which companies offer housing stipends?" should ideally retrieve chunks from multiple companies, but semantic similarity may bias toward one company's document if it matches the phrasing more closely. The survival guide (doc 10) aggregates stipend data across all companies — ensuring it is well-chunked and that its chunks score highly on these queries is critical.

2. **Regulatory vs. technical role confusion.** Some queries (e.g., "what is the interview like at Merck?") could retrieve chunks from either the technical or regulatory doc depending on which matches the embedding better. Metadata filtering by `role_type` in the UI helps users narrow this, but the default retrieval must still surface the most relevant chunk regardless of role type.

---

## Architecture

```
User Query
    │
    ▼
[ Streamlit UI ]  ←── company filter, top-k slider
    │
    ▼
[ semantic_search() ]  ←── ChromaDB PersistentClient
    │                        all-MiniLM-L6-v2 embeddings
    │                        cosine similarity
    ▼
[ Top-k Chunks ]  (text + metadata: company, role_type, source_title)
    │
    ▼
[ generate_answer() ]  ←── OpenAI API (gpt-4o-mini)
    │                        system prompt enforces grounding
    │                        temperature=0.2 for factual output
    ▼
[ Answer + Sources ]
    │
    ▼
[ Streamlit UI ]  ←── renders answer, sources list, chunk inspector

Build-time pipeline (run once via setup.py):
  documents/*.txt
      → ingest.py  (clean + chunk)
      → vector_store.py  (embed + index → chroma_db/)
```

---

## Stretch Features

### Metadata filtering (+1pt)

The Streamlit UI includes a company filter dropdown that restricts ChromaDB retrieval to chunks from a single company. When the user selects a company (e.g., "Benchling"), the `semantic_search()` function passes a `where={"company": "Benchling"}` filter to ChromaDB's query, which applies it at the vector store level before returning results — not as a post-retrieval filter. This means the top-k chunks returned are already restricted to the selected company, and the LLM only sees context from that source.

**Visible effect on results:** A query for "what is the interview process like?" with no filter returns chunks from Benchling, Veeva, and the survival guide. The same query with the Benchling filter returns only Benchling chunks, producing a more focused answer. This is documented in the demo video.


**Milestone 3 — Ingestion and chunking:**
Used Claude to generate the sliding-window chunker with sentence-boundary snapping (`ingest.py`). Prompted with the document structure (short review-style paragraphs, key facts in 1–3 sentences) and the desired chunk size rationale. Reviewed the chunking logic manually and verified it handles edge cases (last chunk, overlap at end of document). Adjusted the sentence-boundary snap window from ±30 to ±50 chars after testing on a sample document.

**Milestone 4 — Embedding and retrieval:**
Used Claude to scaffold `vector_store.py` with ChromaDB `PersistentClient` and `SentenceTransformerEmbeddingFunction`. Reviewed the metadata schema and added `role_type` as a filterable field (not in the initial generated version). Verified the cosine similarity → score conversion (`1 - distance`) is correct for ChromaDB's `hnsw:space=cosine` setting.

**Milestone 5 — Generation and interface:**
Used Claude to generate the Groq API call in `rag.py` and the Streamlit layout in `app.py`. Wrote the system prompt myself — the grounding rules and source attribution requirement are critical for correctness and I wanted full control over those. Adjusted the UI to add the chunk inspector expander panel, which was not in the initial generated version but is important for debugging retrieval quality during evaluation.