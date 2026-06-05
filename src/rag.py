"""
rag.py — Grounded response generation using Groq + retrieved context.
Model: llama-3.3-70b-versatile (free tier at console.groq.com)

Grounding rule: the LLM is instructed to answer ONLY from provided context.
Every response must end with a Sources section listing cited documents.
"""

import os
import sys
from groq import Groq
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))
from vector_store import semantic_search

load_dotenv()

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are the Unofficial Guide to Biotech & Pharma Internships — a direct, honest advisor for students navigating internship applications.

STRICT RULES:
1. Answer ONLY using the context documents provided. Do not use outside knowledge.
2. If the context doesn't contain enough information, say so clearly — never fabricate.
3. Be specific: include numbers, names, and details from the documents.
4. End EVERY response with a "Sources:" section listing the document titles you drew from.
5. If sources conflict, note the conflict honestly."""


def format_context(hits: list) -> str:
    parts = []
    for i, h in enumerate(hits, 1):
        parts.append(
            f"[Doc {i}] {h['source']} | Company: {h['company']}\n{h['text']}"
        )
    return "\n\n---\n\n".join(parts)


def generate_answer(query: str, n_chunks: int = 4, company_filter: str = None) -> dict:
    """
    Full RAG pipeline: retrieve → format context → generate grounded answer.
    Returns: { answer, sources, chunks }
    """
    hits = semantic_search(query, n_results=n_chunks, company_filter=company_filter)

    if not hits:
        return {"answer": "No relevant documents found.", "sources": [], "chunks": []}

    context = format_context(hits)
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": (
                f"Question: {query}\n\n"
                f"Context Documents:\n{context}\n\n"
                "Answer using ONLY the context above. Include a Sources section."
            )},
        ],
        temperature=0.2,
        max_tokens=800,
    )

    answer = response.choices[0].message.content
    sources = list({h["source"] for h in hits})

    return {"answer": answer, "sources": sources, "chunks": hits}


if __name__ == "__main__":
    q = "What is the interview process like at Benchling?"
    print(f"Q: {q}\n")
    result = generate_answer(q)
    print(result["answer"])
