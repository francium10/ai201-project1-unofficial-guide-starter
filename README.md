# The Unofficial Guide — Project 1

> **How to use this template:** Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

This project makes **biotech and pharma internship experiences** searchable with plain-language questions. The knowledge it captures is the kind students share with each other — not what job postings say — covering what interviews actually ask, what the day-to-day work looks like, how much interns get paid, whether return offers are realistic, and what nobody tells you before you show up.

This knowledge is hard to find because it is scattered across Reddit threads, Glassdoor reviews, Blind posts, and personal blogs. None of those platforms let you ask a cross-company question and get a grounded, cited answer. A student asking "which companies offer housing stipends?" has to manually open five tabs, read through pages of reviews, and reconcile conflicting information on their own. This system makes all of it queryable in one place, with sources cited in every response.

The system covers internship experiences at Genentech, Veeva Systems, Benchling, Merck, Pfizer, Tempus AI, Bristol Myers Squibb, Johnson & Johnson, and Recursion Pharmaceuticals, plus a compiled community survival guide with pay benchmarks, return offer rates, and application timeline tips.

---

## Document Sources

| #  | Source | Type | URL or file path |
|----|--------|------|-----------------|
| 1  | Reddit r/biotech | First-person intern post | documents/genentech_intern_reddit.txt |
| 2  | Glassdoor intern reviews | Platform review | documents/veeva_intern_glassdoor.txt |
| 3  | Reddit r/cscareerquestions | First-person intern post | documents/benchling_intern_reddit.txt |
| 4  | Glassdoor intern reviews | Platform review | documents/merck_regulatory_intern.txt |
| 5  | Blind + Reddit r/pharm | Platform review + post | documents/pfizer_datascience_intern.txt |
| 6  | Reddit r/cscareerquestions | First-person intern post | documents/tempus_ai_intern.txt |
| 7  | Glassdoor intern reviews | Platform review | documents/bms_regulatory_intern.txt |
| 8  | Reddit + LinkedIn post | First-person intern post | documents/jnj_medtech_intern.txt |
| 9  | Reddit + personal blog | First-person intern post | documents/recursion_ml_intern.txt |
| 10 | r/biotech community wiki | Compiled community guide | documents/biotech_internship_survival_guide.txt |

---

## Chunking Strategy

**Chunk size:** 400 characters

**Overlap:** 80 characters

**Why these choices fit your documents:**
Our documents are review-style first-person narratives — Reddit posts and Glassdoor reviews where key facts (interview round counts, salary figures, return offer rates, tools used) appear in dense, concentrated bursts of 1–3 sentences. A 400-character window captures roughly one "topic unit" — for example, a description of one interview round, or a compensation breakdown — without mixing multiple unrelated ideas into the same chunk. Larger chunks (800+ characters) would blend topics like compensation and culture into a single vector, hurting retrieval precision when a user asks specifically about pay.

The 80-character overlap prevents facts from being split across chunk boundaries. Without overlap, a sentence like "The return offer rate is approximately 40–50% for strong performers" could be split so that neither chunk contains the full fact. We also apply sentence-boundary snapping: when the sliding window lands mid-sentence, the chunker scans forward up to 50 characters for the nearest period and extends the boundary there. This keeps chunks semantically clean without requiring a full semantic chunker library.

**Final chunk count:** 121 chunks across 10 documents

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via the `sentence-transformers` library, run fully locally with no API key required.

**Production tradeoff reflection:**
`all-MiniLM-L6-v2` produces 384-dimensional embeddings and runs in memory with no network calls, which means zero latency variance and no cost. It performs well on English short-to-medium text — exactly what our review-style corpus is. The tradeoff is that it is English-only and a smaller model than commercial alternatives.

For a production system, the two most relevant alternatives are OpenAI's `text-embedding-3-small` (better semantic quality, multilingual support, ~$0.02 per million tokens, requires an API key and introduces network latency) and Cohere's `embed-v3` (the strongest multilingual option with a long context window, useful if expanding to non-English internship sources). For this project's scope — English corpus, local development, no budget — `all-MiniLM-L6-v2` is the right call. For a deployed product serving international students researching US internships, the quality and multilingual gains of `embed-v3` would justify its cost.

---

## Grounded Generation

**System prompt grounding instruction:**
The system prompt contains five explicit rules that enforce grounding. The core rule is: *"Answer ONLY using the context documents provided. Do not use outside knowledge."* A second rule requires: *"If the context doesn't contain enough information, say so clearly — never fabricate."* A third requires specificity: *"Be specific: include numbers, names, and details from the documents."* Together these rules prevent the LLM from drawing on its training data about well-known companies like Pfizer or Genentech — it must answer only from what was retrieved.

The model is `llama-3.3-70b-versatile` via Groq, with `temperature=0.2` to reduce creative variance and keep responses factual and consistent across repeated queries.

**How source attribution is surfaced in the response:**
Every response is required to end with a `Sources:` section that lists the document titles it drew from. This is enforced in both the system prompt ("End EVERY response with a 'Sources:' section listing the document titles you drew from") and the user message template. In the Streamlit UI, the sources are also displayed separately below the answer as a labeled list, and users can expand each retrieved chunk individually to see exactly which text passage informed the answer. This gives three levels of attribution: the answer text itself, the Sources footer, and the raw chunk inspector.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What is the interview process like at Benchling? | 4 rounds: recruiter screen, 2 LeetCode mediums, system design with life-sciences prompt, behavioral with EM. Domain knowledge tested. | Correctly described all 4 rounds with specific details — mentioned the molecular sequence versioning system design prompt and the domain knowledge requirement. Cited Benchling source. | Relevant | Accurate |
| 2 | Which companies offer housing stipends and how much? | Genentech $2,000 · Merck $3,000 · BMS $2,500 · J&J $2,000 · Veeva no stipend · Benchling no stipend · ~60% of Big Pharma offer stipends. | Retrieved the survival guide chunk with the aggregated stipend table and named all companies correctly with amounts. Minor omission: did not mention Veeva's $2,500 relocation reimbursement as a partial substitute. | Relevant | Partially accurate |
| 3 | What is the return offer rate at Genentech? | ~40–50% for strong performers per the survival guide. | Returned the correct 40–50% figure and correctly attributed it to the community survival guide. | Relevant | Accurate |
| 4 | What does a regulatory affairs intern actually work on day to day? | Document review, FDA guidance, cross-functional meetings, Veeva Vault, ICH guidelines, NDA/BLA/510k sections. | Described day-to-day accurately using the Merck and BMS documents. Named Veeva Vault, ICH guidelines, and specific examples (FDA vs EMA comparison at Merck, BLA filing at BMS). | Relevant | Accurate |
| 5 | How technical is the Recursion Pharmaceuticals ML interview? | 5 rounds including ML fundamentals, Python ML coding (not LeetCode), research paper presentation, team fit. Described as rigorous. | Correctly identified all 5 rounds and specifically called out that the coding round is ML code not LeetCode. Noted the paper presentation is unusual. | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:**
"Which companies offer housing stipends and how much?" (TC02) returned a partially accurate response — it retrieved the correct survival guide chunk and named most companies correctly, but omitted Veeva's $2,500 relocation reimbursement, which is a partial substitute for a stipend and matters to applicants comparing offers.

**What the system returned:**
The system correctly identified that Genentech ($2,000), Merck ($3,000), BMS ($2,500), and J&J ($2,000) offer housing stipends, and that Benchling offers nothing. It stated Veeva offers "no housing stipend" — technically correct — but missed the relocation reimbursement detail that appears in a different chunk of the Veeva document.

**Root cause (tied to a specific pipeline stage):**
This is a **retrieval gap** caused by chunk boundary placement. The Veeva relocation reimbursement detail ("Relocation reimbursement up to $2,500") appears in a chunk that is not semantically close to the query "housing stipend" — the word "relocation" versus "housing" creates enough embedding distance that the chunk did not rank in the top 4. The survival guide chunk with the aggregated stipend table ranked first and dominated the retrieval results, leaving no slot for the Veeva detail.

**What you would change to fix it:**
Two fixes would address this. First, **hybrid search** (BM25 + semantic) would catch the keyword "relocation" even when the semantic embedding misses it — this is precisely the kind of case where keyword matching outperforms dense retrieval. Second, increasing `n_results` from 4 to 6 for broad multi-company queries would give more room for company-specific chunks to appear alongside the aggregated survival guide chunk. A more robust fix would add a `stipend_type` metadata field and allow the retrieval layer to explicitly query for all chunks tagged with housing or relocation data.

---

## Spec Reflection

**One way the spec helped you during implementation:**
The spec's instruction to "test retrieval before you add generation" was the single most valuable piece of advice. Early in development, the smoke test in `vector_store.py` revealed that a query about Benchling interviews was retrieving a chunk from the survival guide's "biggest mistakes" section instead of the Benchling document itself. This happened because the survival guide chunk mentioned "interview" more frequently in proximity to common keywords. Catching this at the retrieval stage — before wiring in the LLM — meant the fix (adjusting chunk size to better isolate the survival guide's sections) took 10 minutes instead of hours of debugging hallucinated responses.

**One way your implementation diverged from the spec, and why:**
The spec suggests a simple query interface — "a web UI, a command-line tool, or a notebook." The implementation went beyond this by adding a chunk inspector panel in the Streamlit UI that lets users expand each retrieved chunk and see the exact text passage and similarity score. This was not in the spec but became necessary during evaluation: without seeing which chunks were retrieved, it was impossible to diagnose whether a partial or inaccurate response was a retrieval failure or a generation failure. Making retrieval transparent in the UI turned a debugging tool into a feature — it also demonstrates to anyone running the system exactly how RAG works, which is valuable for a project submission.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* The document structure (10 review-style .txt files, 400–1,200 words each, key facts in short 1–3 sentence bursts) and the chunking requirements (sliding window, sentence-boundary snapping, overlap, metadata extraction from document headers).
- *What it produced:* A complete `ingest.py` with the `Chunk` dataclass, `clean_text()`, `chunk_text()` with sentence-boundary snapping, `extract_metadata()` for inferring company and role type from filenames, and `ingest_all()` that processes all files and returns a flat list of chunks.
- *What I changed or overrode:* The initial sentence-boundary snap window was ±30 characters, which was too narrow — short sentences ending before the window were getting cut. I expanded it to ±50 characters after testing on the Genentech document and seeing two factual sentences split mid-word. I also added the `role_type` field to the metadata schema, which was not in the generated version but became important for enabling the company + role filter in the UI.

**Instance 2**

- *What I gave the AI:* The system prompt requirements — that responses must be grounded only in retrieved context, must never fabricate, must be specific with numbers and names, and must end with a Sources section — plus the Groq model name and the desired response format.
- *What it produced:* A complete `rag.py` with `format_context()`, `generate_answer()` calling the Groq API, and a basic `SYSTEM_PROMPT` string with grounding rules.
- *What I changed or overrode:* The generated system prompt had only two rules and used softer language ("try to answer only from context"). I rewrote it with five explicit rules using direct language ("Answer ONLY", "never fabricate", "End EVERY response") because soft instructions are easier for the model to drift from under paraphrasing pressure. I also set `temperature=0.2` explicitly — the generated version used the default (1.0), which produced inconsistently formatted Sources sections across repeated runs.