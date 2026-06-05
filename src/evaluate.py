"""
evaluate.py — Evaluation framework (Milestone 6)
Run from project root: python src/evaluate.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from rag import generate_answer

TEST_CASES = [
    {
        "id": "TC01",
        "question": "What is the interview process like at Benchling?",
        "ground_truth": "4 rounds: recruiter screen, 2 LeetCode mediums, system design (life-sciences themed), behavioral with EM. Domain knowledge tested — must know life sciences.",
        "expected_company": "Benchling",
    },
    {
        "id": "TC02",
        "question": "Which companies offer housing stipends and how much?",
        "ground_truth": "Genentech $2,000. Merck $3,000. BMS $2,500. J&J $2,000. Veeva no stipend (relocation $2,500). Benchling no stipend. ~60% of Big Pharma offer stipends.",
        "expected_company": "General",
    },
    {
        "id": "TC03",
        "question": "What is the return offer rate at Genentech?",
        "ground_truth": "Approximately 40-50% for strong performers per the survival guide.",
        "expected_company": "Genentech",
    },
    {
        "id": "TC04",
        "question": "What does a regulatory affairs intern actually work on day to day?",
        "ground_truth": "Document review, FDA guidance documents, cross-functional meetings, Veeva Vault, ICH guidelines, IND/NDA/BLA/510k submission sections. Merck: FDA vs EMA comparison. BMS: CMC sections for BLA.",
        "expected_company": "Merck",
    },
    {
        "id": "TC05",
        "question": "How technical is the Recursion Pharmaceuticals ML interview?",
        "ground_truth": "5 rounds including ML fundamentals (bias-variance, overfitting), Python ML coding (not LeetCode), research paper presentation, team fit. Described as rigorous.",
        "expected_company": "Recursion Pharmaceuticals",
    },
]


def score_retrieval(chunks, expected_company):
    companies = [c["company"] for c in chunks]
    if expected_company == "General":
        return "PASS"
    if expected_company in companies:
        return f"PASS (rank {companies.index(expected_company) + 1})"
    return "FAIL"


def score_response(answer, ground_truth):
    gt_words = set(ground_truth.lower().split())
    ans_words = set(answer.lower().split())
    ratio = len(gt_words & ans_words) / max(len(gt_words), 1)
    if ratio >= 0.35:
        return "ACCURATE"
    elif ratio >= 0.18:
        return "PARTIAL"
    return "INACCURATE"


def run_evaluation():
    print("=" * 65)
    print("EVALUATION REPORT — Unofficial Biotech/Pharma Internship Guide")
    print("=" * 65)

    summary = []
    for tc in TEST_CASES:
        print(f"\n[{tc['id']}] {tc['question']}")
        print("-" * 55)
        result = generate_answer(tc["question"], n_chunks=4)
        retrieval = score_retrieval(result["chunks"], tc["expected_company"])
        response = score_response(result["answer"], tc["ground_truth"])

        print(f"Answer (truncated): {result['answer'][:400]}...")
        print(f"Retrieved from: {[c['company'] for c in result['chunks']]}")
        print(f"Retrieval: {retrieval} | Response: {response}")
        summary.append({"id": tc["id"], "retrieval": retrieval, "response": response})

    print(f"\n{'='*65}\nSUMMARY")
    for r in summary:
        print(f"  {r['id']}: Retrieval={r['retrieval']} | Response={r['response']}")


if __name__ == "__main__":
    run_evaluation()
