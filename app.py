"""
app.py — Streamlit query interface
Run from project root: streamlit run src/app.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from rag import generate_answer

st.set_page_config(
    page_title="Unofficial Biotech Internship Guide",
    page_icon="🧬",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
h1, h2, h3 { font-family: 'IBM Plex Mono', monospace; }
.answer-box {
    background: #161b22; border: 1px solid #30363d;
    border-left: 4px solid #58a6ff; border-radius: 6px;
    padding: 1.2rem 1.5rem; margin-top: 1rem;
    font-size: 0.95rem; line-height: 1.7; white-space: pre-wrap;
    color: #e6edf3;
}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🧬 Unofficial Biotech/Pharma Internship Guide")
st.markdown("*Student-sourced intelligence on what internships are actually like.*")
st.divider()

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    company_filter = st.selectbox("Filter by company", [
        "All", "Genentech", "Veeva Systems", "Benchling", "Merck",
        "Pfizer", "Tempus AI", "Bristol Myers Squibb",
        "Johnson & Johnson", "Recursion Pharmaceuticals", "General"
    ])
    n_chunks = st.slider("Chunks to retrieve", 2, 6, 4)
    show_chunks = st.checkbox("Show retrieved chunks", value=True)

    st.divider()
    st.markdown("### 💡 Try asking:")
    samples = [
        "What is the interview process like at Benchling?",
        "Which companies offer housing stipends?",
        "What do regulatory interns actually work on?",
        "What is the return offer rate at Genentech?",
        "How technical is the Recursion ML interview?",
    ]
    for q in samples:
        if st.button(q, key=q, use_container_width=True):
            st.session_state["query"] = q

query = st.text_input(
    "Ask anything about biotech/pharma internships:",
    placeholder="e.g. What's it actually like to intern at Pfizer?",
    key="query",
)

if st.button("🔍 Search", type="primary") and query.strip():
    with st.spinner("Searching and generating answer..."):
        result = generate_answer(
            query,
            n_chunks=n_chunks,
            company_filter=None if company_filter == "All" else company_filter,
        )

    st.markdown("### 📋 Answer")
    st.markdown(f'<div class="answer-box">{result["answer"]}</div>', unsafe_allow_html=True)

    if result["sources"]:
        st.markdown("### 📚 Sources")
        for s in result["sources"]:
            st.markdown(f"- `{s}`")

    if show_chunks and result["chunks"]:
        st.markdown("### 🔎 Retrieved Chunks")
        for i, c in enumerate(result["chunks"], 1):
            with st.expander(f"Chunk {i} — {c['company']} (score: {c['score']})"):
                st.text(c["text"])

st.divider()
st.caption("Built with ChromaDB · sentence-transformers · Groq llama-3.3-70b · Streamlit")
