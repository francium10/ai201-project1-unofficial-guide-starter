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

## Sample Chunks

Five representative chunks from the corpus, showing how the chunking strategy divides the source documents in practice.

**Chunk 1 — Source: `benchling_intern_reddit.txt`**
```
The Interview:
4 rounds total. First: 30-min recruiter screen (background, why Benchling, why life sciences software). Second: 1-hour technical screen with 2 LeetCode mediums, emphasis on arrays/strings. Third: System design round — I got asked to design a "molecular sequence versioning system" (very on-brand). Fourth: Behavioral with an engineering manager (STAR format, prepare your stories).
```

**Chunk 2 — Source: `genentech_intern_reddit.txt`**
```
Compensation:
Around $35-38/hr for bioprocess roles. Housing stipend of $2,000 for the summer. No relocation. They do provide a shuttle from Caltrain which is helpful.

Downsides:
South San Francisco is expensive. The shuttle schedule is rigid. Some senior scientists can be dismissive of intern ideas — thick skin helps.
```

**Chunk 3 — Source: `recursion_ml_intern.txt`**
```
Interview Process (5 rounds — yes, really):
1. Recruiter screen
2. ML fundamentals: bias-variance, overfitting, regularization, basic probability
3. Coding: Python ML code (no LeetCode grind — they want you to actually write ML code)
4. Research presentation: present a paper you've read in the last 6 months
5. Team fit: informal chat with 3 team members
They are rigorous.
```

**Chunk 4 — Source: `biotech_internship_survival_guide.txt`**
```
RETURN OFFER RATES (community estimates, vary by year):
- Genentech: ~40-50% for strong performers
- Merck: ~30-40%
- BMS: ~35-45%
- Pfizer: ~20-30% (post-2023 layoffs reduced this)
- Veeva: ~50-60%
- Benchling: ~40-50%
- Recursion: ~30-40%
```

**Chunk 5 — Source: `merck_regulatory_intern.txt`**
```
Day-to-Day:
Lots of document review. Reading FDA guidance documents. Attending cross-functional team meetings (clinical, CMC, regulatory). Using Veeva Vault for document management. Learning about ICH guidelines (Q1, Q8, Q9, Q10 are the big ones for CMC). If you're not comfortable reading dense regulatory text, this role will be an adjustment.
```

---

## Retrieval Test Results

Three queries run against the vector store, showing the top returned chunks and relevance analysis.

---

**Query 1: "What is the interview process like at Benchling?"**

| Rank | Source Document | Similarity Score | Chunk Preview |
|------|----------------|-----------------|---------------|
| 1 | benchling_intern_reddit.txt | 0.81 | "4 rounds total. First: 30-min recruiter screen... Second: 1-hour technical screen with 2 LeetCode mediums... Third: System design round — molecular sequence versioning system..." |
| 2 | benchling_intern_reddit.txt | 0.74 | "Pro tip: they will ask 'what do you know about the life sciences industry?' in at least one round. If you can't answer this, you will struggle..." |
| 3 | veeva_intern_glassdoor.txt | 0.61 | "The interview process is technical and moves fast — two LeetCode-style problems (medium difficulty) plus system design for senior interns..." |
| 4 | biotech_internship_survival_guide.txt | 0.54 | "Be able to explain your research clearly to a non-expert — this separates candidates at every level..." |

*Why the top chunks are relevant:* Chunks 1 and 2 are both from the Benchling document and directly describe the interview structure. Chunk 1 covers the four rounds with specifics; Chunk 2 adds the domain knowledge requirement that is unique to Benchling. Chunk 3 from Veeva is partially relevant — it describes a similar pharma-tech SaaS interview format and provides useful comparison context. Chunk 4 from the survival guide gives general interview advice that supplements the specific Benchling information.

---

**Query 2: "How much do biotech interns get paid?"**

| Rank | Source Document | Similarity Score | Chunk Preview |
|------|----------------|-----------------|---------------|
| 1 | biotech_internship_survival_guide.txt | 0.79 | "COMPENSATION BENCHMARKS (2024): Big Pharma regulatory: $25-32/hr · Big Pharma data science: $38-48/hr · Pharma-tech SaaS: $45-55/hr · TechBio/AI drug discovery: $48-58/hr..." |
| 2 | benchling_intern_reddit.txt | 0.68 | "Compensation: ~$50-55/hr in San Francisco. No housing stipend (SF is brutal — budget carefully). Commuter benefits." |
| 3 | recursion_ml_intern.txt | 0.65 | "Pay: $50-55/hr. No housing stipend. SLC cost of living is low — you'll actually save money." |
| 4 | genentech_intern_reddit.txt | 0.62 | "Compensation: Around $35-38/hr for bioprocess roles. Housing stipend of $2,000 for the summer. No relocation." |

*Why the top chunks are relevant:* Chunk 1 is the ideal retrieval — the survival guide's compensation table aggregates pay ranges across all role types, giving a direct answer to a broad pay question. Chunks 2–4 provide company-specific figures that ground the general ranges in real data points. Together these four chunks let the LLM give a well-supported, cross-company answer with specific numbers.

---

**Query 3: "What skills do I need for a regulatory affairs internship?"**

| Rank | Source Document | Similarity Score | Chunk Preview |
|------|----------------|-----------------|---------------|
| 1 | merck_regulatory_intern.txt | 0.76 | "Skills You'll Develop: FDA regulatory pathway knowledge (IND, NDA, BLA, 510k) · ICH guideline familiarity · Veeva Vault document management · Analytical method validation concepts..." |
| 2 | biotech_internship_survival_guide.txt | 0.71 | "WHAT ACTUALLY MATTERS IN INTERVIEWS: Know the FDA regulatory pathway relevant to the role: Drug roles: IND → Phase 1/2/3 → NDA/BLA · Device roles: 510(k) for Class II, PMA for Class III..." |
| 3 | bms_regulatory_intern.txt | 0.67 | "What You Learn: ICH Q6A/Q6B: specifications for drug substances · CTD format — how regulatory filings are structured globally · Analytical method validation concepts · How CMC data connects to clinical data..." |
| 4 | jnj_medtech_intern.txt | 0.59 | "What I Learned: 510(k) vs PMA pathway decision criteria · FDA's predicate device database · Design controls under 21 CFR Part 820 · Risk management under ISO 14971..." |

*Why the top chunks are relevant:* All four chunks directly address regulatory skills. Chunks 1 and 3 come from regulatory intern experience documents (Merck and BMS) and list concrete skills developed on the job. Chunk 2 from the survival guide frames these skills as interview requirements, which answers the question from an application preparation angle. Chunk 4 from J&J adds the medical device regulatory track (510k, ISO 14971) which is a distinct regulatory pathway not covered in the drug-focused documents.

---

## Example Responses

**Response 1 — Query: "What is the interview process at Veeva Systems?"**

> Based on the retrieved documents, the Veeva Systems interview process for Software Engineer interns is technical and moves quickly. There are two LeetCode-style coding problems at medium difficulty, plus a system design round for senior interns. Interviewers ask life-sciences-specific system design questions — one example given is "design a clinical trial data tracking system" — so domain knowledge about the life sciences industry is explicitly tested and gives candidates an edge.
>
> The process is described as fast-moving from first contact to offer. Candidates are expected to explain their thinking out loud during technical screens; communication quality is weighted heavily alongside technical correctness.
>
> Key preparation tips from the document: know what Vault CRM and Veeva Network are before your interview, prepare a story about working with data at scale, and practice explaining your reasoning verbally, not just writing correct code.
>
> **Sources:** Veeva Systems Software Engineer Intern Review — Glassdoor (documents/veeva_intern_glassdoor.txt)

---

**Response 2 — Query: "What is the return offer rate at Recursion and what affects it?"**

> According to the community survival guide, Recursion Pharmaceuticals has a return offer rate of approximately 30–40% for interns, which is on the lower end compared to pharma-tech SaaS companies like Veeva (~50–60%) but comparable to large pharma companies like Merck (~30–40%).
>
> The intern experience document for Recursion adds context: return offer rates vary heavily by team. The document notes that roughly half of the interns in one cohort received return offers, suggesting the 30–40% community estimate may be conservative depending on the specific group. Factors that likely affect outcomes include project completion quality — the document describes full ownership of a ML pipeline improvement with a measurable result (3.2% F1 improvement) as the standard of work expected — and mission alignment, since Recursion's culture is described as strongly values-driven and interviewers ask directly about motivation for precision medicine work.
>
> **Sources:** Recursion Pharmaceuticals ML Intern — Reddit + personal blog (documents/recursion_ml_intern.txt) · Biotech/Pharma Internship Survival Guide (documents/biotech_internship_survival_guide.txt)

---

**Response 3 — Out-of-scope query: "What GPA do I need to get into Harvard Medical School?"**

> The documents in this system cover biotech and pharma internship experiences — interview processes, day-to-day work, compensation, and return offer rates at companies like Genentech, Benchling, Veeva, Merck, and others. They do not contain any information about medical school admissions, GPA requirements, or Harvard Medical School specifically.
>
> I can't answer this question from the available documents. For medical school admissions guidance, the AAMC (aamc.org) and individual school admissions pages would be the right sources.
>
> **Sources:** No relevant documents retrieved.

---

## Query Interface

**Interface type:** Streamlit web application, launched via `streamlit run src/app.py`, accessible at `http://localhost:8501`.

**Input fields:**
- **Query text box** — free-text plain-language question about biotech/pharma internships (main input)
- **Company filter** (sidebar dropdown) — optionally restrict retrieval to one company: All, Genentech, Veeva Systems, Benchling, Merck, Pfizer, Tempus AI, Bristol Myers Squibb, Johnson & Johnson, Recursion Pharmaceuticals, or General
- **Chunks to retrieve** (sidebar slider, range 2–6, default 4) — controls how many chunks are passed to the LLM as context
- **Show retrieved chunks** (sidebar checkbox, default on) — toggles visibility of the chunk inspector panel
- **Sample question buttons** (sidebar) — 5 pre-written queries that populate the text box on click

**Output fields:**
- **Answer panel** — the LLM-generated response, grounded in retrieved context, always ending with a Sources section
- **Sources list** — the document titles cited in the answer, displayed as a labeled list below the answer
- **Retrieved chunks panel** — expandable per-chunk view showing the exact text passage and similarity score for each retrieved chunk

**Sample interaction transcript:**

```
User input:  "Do Pfizer interns get real work or is it mostly busywork?"

System output:
Based on the retrieved documents, Pfizer Data Science interns do get real, 
substantive projects — but there is a significant onboarding delay before 
that work begins.

The intern experience document describes a project building a machine 
learning model to predict clinical trial dropout rates using a large 
anonymized patient dataset. The problem is described as genuinely hard 
with real stakes. The intern had full access to the data and used Python 
(pandas, scikit-learn, PyTorch) and Cloudera Data Platform for big data 
processing.

However, the document is explicit that the first 3 weeks were consumed by 
system access requests, mandatory compliance training (GxP, HIPAA, data 
governance — approximately 40 hours of e-learning), and orientation. The 
intern did not touch actual data until week 4 of a 12-week internship. 
This is described as industry-standard for regulated pharma environments, 
not specific to Pfizer.

The document advises: "Be patient with the access/compliance process — 
it's industry standard." The work itself is real, but the ramp-up period 
is longer than at pharma-tech companies like Benchling or Veeva.

Sources: Pfizer Data Science Intern — Blind + Reddit 
(documents/pfizer_datascience_intern.txt)

Retrieved chunks:
  Chunk 1 — Pfizer (score: 0.77)
  "The Good: Pfizer Digital is the internal tech arm of Pfizer... 
   My project was building a machine learning model to predict clinical 
   trial dropout rates..."
  
  Chunk 2 — Pfizer (score: 0.71)  
  "The Challenging: Big Pharma bureaucracy is real. I spent my first 
   3 weeks getting system access, completing mandatory training..."
```

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