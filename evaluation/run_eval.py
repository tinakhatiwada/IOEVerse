"""
Evaluation runner — run the eval set against the RAG pipeline and report.

Usage:
    python -m evaluation.run_eval

Reports per-question:
  - Retrieval success (did we get relevant chunks?)
  - Context sufficiency (does the context actually cover the answer?)
  - Generation faithfulness (does the answer match the context?)
  - Status correctness (did the grounding status match expectations?)
"""

import json
import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.rag.grounding import ask_question  # noqa: E402
from app.rag.retriever import retrieve  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

EVAL_SET_PATH = os.path.join(os.path.dirname(__file__), "eval_set.json")


def run_eval() -> None:
    """Run the evaluation set and print a results table."""
    with open(EVAL_SET_PATH) as f:
        eval_set = json.load(f)

    results = []

    for i, item in enumerate(eval_set, 1):
        q = item["question"]
        subject = item["subject"]
        chapter = item["chapter"]
        expected_status = item["expected_status"]
        corpus_sufficient = item["corpus_sufficient"]

        logger.info("--- Question %d/%d ---", i, len(eval_set))
        logger.info("Q: %s", q)

        # 1. Retrieval check
        chunks = retrieve(q, subject, chapter, k=5)
        retrieval_ok = len(chunks) > 0
        retrieval_has_chapter = any(
            c.get("chapter", "").lower() == chapter.lower() for c in chunks
        )

        # 2. Grounding call
        result = ask_question(q, subject, chapter)
        actual_status = result.get("status", "error")

        # 3. Assess
        status_correct = actual_status == expected_status

        # Context sufficiency: if corpus is sufficient but model says not_found,
        # that's a retrieval/grounding failure
        context_ok = True
        if corpus_sufficient and actual_status == "not_found":
            context_ok = False
        if not corpus_sufficient and actual_status == "grounded":
            context_ok = False  # model is probably hallucinating

        # Generation faithfulness: basic check — did model return an answer
        # when it should have, and not when it shouldn't?
        answer = result.get("answer")
        generation_ok = True
        if actual_status == "grounded" and not answer:
            generation_ok = False
        if actual_status == "not_found" and answer:
            generation_ok = False

        results.append({
            "num": i,
            "question": q[:60] + "..." if len(q) > 60 else q,
            "expected": expected_status,
            "actual": actual_status,
            "retrieval_ok": retrieval_ok,
            "retrieval_chapter_match": retrieval_has_chapter,
            "context_ok": context_ok,
            "generation_ok": generation_ok,
            "status_correct": status_correct,
        })

        logger.info(
            "   Expected: %-12s  Got: %-12s  ✅" if status_correct else
            "   Expected: %-12s  Got: %-12s  ❌",
            expected_status, actual_status,
        )

    # Print summary table
    print("\n" + "=" * 110)
    print(f"{'#':>3} | {'Question':<62} | {'Expected':<14} | {'Actual':<14} | {'Ret':>3} | {'Ctx':>3} | {'Gen':>3} | {'OK':>3}")
    print("-" * 110)

    correct = 0
    for r in results:
        ok = "✅" if r["status_correct"] else "❌"
        ret = "✅" if r["retrieval_ok"] else "❌"
        ctx = "✅" if r["context_ok"] else "❌"
        gen = "✅" if r["generation_ok"] else "❌"
        print(f"{r['num']:>3} | {r['question']:<62} | {r['expected']:<14} | {r['actual']:<14} | {ret:>3} | {ctx:>3} | {gen:>3} | {ok:>3}")
        if r["status_correct"]:
            correct += 1

    print("=" * 110)
    print(f"Status accuracy: {correct}/{len(results)} ({100*correct/len(results):.0f}%)")

    # Breakdown by failure type
    retrieval_failures = sum(1 for r in results if not r["retrieval_ok"])
    context_failures = sum(1 for r in results if not r["context_ok"])
    generation_failures = sum(1 for r in results if not r["generation_ok"])

    print(f"\nFailure breakdown:")
    print(f"  Retrieval failures:  {retrieval_failures}")
    print(f"  Context failures:    {context_failures}")
    print(f"  Generation failures: {generation_failures}")


if __name__ == "__main__":
    run_eval()
