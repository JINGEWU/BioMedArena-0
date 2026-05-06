"""Failure mode taxonomy — LLM-judge classifies wrong answers into error types.

Useful for error analysis and targeted improvements. Taxonomy:

    KNOWLEDGE_GAP        — Agent simply doesn't know the fact and didn't look it up.
    RETRIEVAL_FAILED     — Agent tried to retrieve but got nothing relevant.
    RETRIEVAL_WRONG      — Retrieved info was on-topic but factually incorrect
                            or outdated, leading agent astray.
    REASONING_ERROR      — Retrieved correct info but reasoned incorrectly.
    EXTRACTION_ERROR     — Final answer extraction (letter/number) failed even
                            though reasoning was correct.
    AMBIGUOUS_QUESTION   — The question itself is ambiguous; answer is defensible.
    OTHER                — None of the above.
"""

from __future__ import annotations

import logging
from collections import Counter
from typing import Any

from harness.llm_client import LLMClient

logger = logging.getLogger(__name__)


TAXONOMY_CATEGORIES = [
    "KNOWLEDGE_GAP",
    "RETRIEVAL_FAILED",
    "RETRIEVAL_WRONG",
    "REASONING_ERROR",
    "EXTRACTION_ERROR",
    "AMBIGUOUS_QUESTION",
    "OTHER",
]


TAXONOMY_SYSTEM = (
    "You are an error analyst for a medical/scientific AI agent. Given a "
    "failed task — the question, the expected answer, the agent's predicted "
    "answer, the tools it called, and its raw response — classify the error "
    "into exactly ONE of these categories:\n\n"
    "  KNOWLEDGE_GAP       — Agent didn't know the fact and did not retrieve it.\n"
    "  RETRIEVAL_FAILED    — Agent tried to retrieve but got nothing relevant.\n"
    "  RETRIEVAL_WRONG     — Retrieved content was misleading or incorrect.\n"
    "  REASONING_ERROR     — Correct info was retrieved but reasoning went wrong.\n"
    "  EXTRACTION_ERROR    — Correct reasoning but wrong final answer format/extraction.\n"
    "  AMBIGUOUS_QUESTION  — Question is ambiguous; prediction is defensible.\n"
    "  OTHER               — None of the above.\n\n"
    'Return ONLY a JSON object: {"category": "ONE_OF_THE_LABELS", '
    '"reasoning": "one-sentence explanation"}'
)


TAXONOMY_PROMPT = """Question:
{question}

Expected answer:
{expected}

Predicted answer (final extracted):
{predicted}

Agent's full response:
{raw}

Tools called by the agent:
{tools}

Classify the error category."""


class FailureTaxonomist:
    """Classify errors in benchmark results via LLM."""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def classify_one(
        self,
        question: str,
        expected: str,
        predicted: str,
        raw_response: str,
        tools: list[str],
    ) -> dict[str, Any]:
        prompt = TAXONOMY_PROMPT.format(
            question=(question or "")[:1500],
            expected=(expected or "")[:500],
            predicted=(predicted or "")[:500],
            raw=(raw_response or "")[:1500],
            tools=", ".join(tools) if tools else "(none)",
        )
        try:
            result = await self.llm.chat_json(
                messages=[
                    {"role": "system", "content": TAXONOMY_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
            )
            category = str(result.get("category", "OTHER")).upper()
            if category not in TAXONOMY_CATEGORIES:
                category = "OTHER"
            return {
                "category": category,
                "reasoning": str(result.get("reasoning", ""))[:200],
            }
        except Exception as exc:
            logger.warning("failure taxonomy failed: %s", exc)
            return {"category": "OTHER", "reasoning": f"taxonomy_error: {exc}"}

    async def classify_failures(
        self,
        results: dict[str, dict[str, Any]],
        max_concurrent: int = 5,
    ) -> dict[str, Any]:
        """Classify all failed tasks across results.

        Args:
            results: {benchmark: {mode: BenchmarkMetrics}} (after-judge)
            max_concurrent: parallel judge calls

        Returns:
            {mode: Counter of categories}
        """
        import asyncio

        sem = asyncio.Semaphore(max_concurrent)

        async def _one(q):
            async with sem:
                return await self.classify_one(
                    question=q.question_text,
                    expected=q.expected,
                    predicted=q.predicted,
                    raw_response=q.predicted_raw,
                    tools=q.tool_calls_made,
                )

        by_mode: dict[str, list] = {}
        for bench_name, mode_results in results.items():
            for mode, metrics in mode_results.items():
                for q in metrics.per_question:
                    if not q.task_success:
                        by_mode.setdefault(mode, []).append(q)

        # Classify in parallel
        mode_summary: dict[str, Any] = {}
        for mode, failed_questions in by_mode.items():
            if not failed_questions:
                continue
            coros = [_one(q) for q in failed_questions]
            classifications = list(await asyncio.gather(*coros))
            categories = Counter(c["category"] for c in classifications)
            mode_summary[mode] = {
                "total_failures": len(failed_questions),
                "categories": dict(categories),
                "examples": [
                    {"qid": q.question_id, "category": c["category"], "why": c["reasoning"][:150]}
                    for q, c in list(zip(failed_questions, classifications))[:5]
                ],
            }

        return mode_summary


def format_taxonomy_report(taxonomy: dict[str, Any]) -> str:
    """Pretty-print the taxonomy summary."""
    lines = ["=" * 78, "FAILURE MODE TAXONOMY (per mode)", "=" * 78]
    for mode, info in taxonomy.items():
        total = info["total_failures"]
        cats = info["categories"]
        lines.append(f"\n  {mode}  ({total} failures):")
        for cat, cnt in sorted(cats.items(), key=lambda x: -x[1]):
            pct = cnt / total * 100 if total else 0
            lines.append(f"    {cat:<22s} {cnt:>4d}  ({pct:4.1f}%)")
        lines.append(f"    Example failures:")
        for ex in info.get("examples", [])[:3]:
            lines.append(f"      [{ex['category']}] qid={ex['qid']}: {ex['why']}")
    lines.append("=" * 78)
    return "\n".join(lines)
