"""Benchmark evaluator — modes: simple_llm, deep_think, heavy."""

from __future__ import annotations

import asyncio
import json
import logging
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from harness.eval.scoring import extract_answer_from_response, score_question
from harness.llm_client import LLMClient

logger = logging.getLogger(__name__)


@dataclass
class QuestionResult:
    question_id: str
    mode: str
    question_text: str
    expected: str
    answer_type: str
    predicted_raw: str
    predicted_extracted: str
    correct: bool
    latency_s: float
    category: str
    error: str | None = None


@dataclass
class ModeResult:
    mode: str
    accuracy: float
    total: int
    correct_count: int
    avg_latency_s: float
    per_question: list[QuestionResult]
    accuracy_by_category: dict[str, float] = field(default_factory=dict)
    accuracy_by_type: dict[str, float] = field(default_factory=dict)


class HLEEvaluator:
    """Evaluate three modes on benchmark questions."""

    SIMPLE_SYSTEM = (
        "You are a helpful assistant. Answer the following question concisely. "
        "If it is multiple choice, respond with ONLY the letter of the correct option (A, B, C, D, or E). "
        "If it requires an exact answer, respond with ONLY the answer, nothing else."
    )

    DEEP_THINK_SYSTEM = (
        "You are an expert scientist with deep expertise in biology, medicine, chemistry, "
        "genetics, neuroscience, and pharmacology. Think through this problem step by step, "
        "considering all relevant scientific principles, mechanisms, and evidence. "
        "After your thorough reasoning, state your final answer clearly on the last line. "
        "If the question is multiple choice, end with: The answer is [X] "
        "(where X is the letter A-E). "
        "If it requires an exact answer, end with: The answer is [your answer]."
    )

    def __init__(self, config_path: str = "config.yaml"):
        from harness.orchestrator import BioMedArena

        self._config_path = config_path
        self.llm: LLMClient | None = None
        self.harness: BioMedArena | None = None

    def _ensure_llm(self) -> LLMClient:
        if self.llm is None:
            import os
            import yaml
            raw = Path(self._config_path).read_text()
            for key, val in os.environ.items():
                raw = raw.replace(f"${{{key}}}", val)
            cfg = yaml.safe_load(raw).get("llm", {})
            self.llm = LLMClient(
                provider=cfg.get("provider", "openai"),
                model=cfg.get("model", "gpt-4o"),
                api_key=cfg.get("api_key"),
                base_url=cfg.get("base_url"),
            )
        return self.llm

    def _ensure_harness(self):
        if self.harness is None:
            from harness.orchestrator import BioMedArena
            self.harness = BioMedArena(self._config_path)
        return self.harness

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    @staticmethod
    def load_questions(path: str = "data/hle/hle_filtered.json") -> list[dict]:
        return json.loads(Path(path).read_text())

    @staticmethod
    def sample_questions(questions: list[dict], n: int = 50, seed: int = 42) -> list[dict]:
        rng = random.Random(seed)
        return rng.sample(questions, min(n, len(questions)))

    # ------------------------------------------------------------------
    # Mode 1: Simple LLM
    # ------------------------------------------------------------------

    async def eval_simple_llm(
        self, questions: list[dict], max_concurrent: int = 5
    ) -> ModeResult:
        """Direct LLM call with minimal prompt."""
        llm = self._ensure_llm()
        sem = asyncio.Semaphore(max_concurrent)
        results: list[QuestionResult] = []

        async def _eval_one(q: dict) -> QuestionResult:
            async with sem:
                start = time.monotonic()
                try:
                    resp = await llm.chat(
                        messages=[
                            {"role": "system", "content": self.SIMPLE_SYSTEM},
                            {"role": "user", "content": q["question"]},
                        ],
                        temperature=0.0,
                        max_tokens=1024,
                    )
                    latency = time.monotonic() - start
                    extracted = extract_answer_from_response(resp, q["answer_type"])
                    correct = score_question(resp, q["answer"], q["answer_type"])
                    return QuestionResult(
                        question_id=q["id"], mode="simple_llm",
                        question_text=q["question"][:200],
                        expected=q["answer"], answer_type=q["answer_type"],
                        predicted_raw=resp, predicted_extracted=extracted,
                        correct=correct, latency_s=round(latency, 2),
                        category=q["category"],
                    )
                except Exception as exc:
                    return QuestionResult(
                        question_id=q["id"], mode="simple_llm",
                        question_text=q["question"][:200],
                        expected=q["answer"], answer_type=q["answer_type"],
                        predicted_raw="", predicted_extracted="",
                        correct=False, latency_s=round(time.monotonic() - start, 2),
                        category=q["category"], error=str(exc),
                    )

        tasks = [_eval_one(q) for q in questions]
        total = len(tasks)
        for i, coro in enumerate(asyncio.as_completed(tasks)):
            r = await coro
            results.append(r)
            if (i + 1) % 10 == 0 or i + 1 == total:
                acc = sum(1 for x in results if x.correct) / len(results)
                print(f"  [simple_llm] {i+1}/{total} done, running accuracy: {acc:.1%}")

        return self._build_mode_result("simple_llm", results)

    # ------------------------------------------------------------------
    # Mode 2: Deep Think
    # ------------------------------------------------------------------

    async def eval_deep_think(
        self, questions: list[dict], max_concurrent: int = 5
    ) -> ModeResult:
        """LLM with chain-of-thought reasoning prompt."""
        llm = self._ensure_llm()
        sem = asyncio.Semaphore(max_concurrent)
        results: list[QuestionResult] = []

        async def _eval_one(q: dict) -> QuestionResult:
            async with sem:
                start = time.monotonic()
                try:
                    resp = await llm.chat(
                        messages=[
                            {"role": "system", "content": self.DEEP_THINK_SYSTEM},
                            {"role": "user", "content": q["question"]},
                        ],
                        temperature=0.0,
                        max_tokens=4096,
                    )
                    latency = time.monotonic() - start
                    extracted = extract_answer_from_response(resp, q["answer_type"])
                    correct = score_question(resp, q["answer"], q["answer_type"])
                    return QuestionResult(
                        question_id=q["id"], mode="deep_think",
                        question_text=q["question"][:200],
                        expected=q["answer"], answer_type=q["answer_type"],
                        predicted_raw=resp, predicted_extracted=extracted,
                        correct=correct, latency_s=round(latency, 2),
                        category=q["category"],
                    )
                except Exception as exc:
                    return QuestionResult(
                        question_id=q["id"], mode="deep_think",
                        question_text=q["question"][:200],
                        expected=q["answer"], answer_type=q["answer_type"],
                        predicted_raw="", predicted_extracted="",
                        correct=False, latency_s=round(time.monotonic() - start, 2),
                        category=q["category"], error=str(exc),
                    )

        tasks = [_eval_one(q) for q in questions]
        total = len(tasks)
        for i, coro in enumerate(asyncio.as_completed(tasks)):
            r = await coro
            results.append(r)
            if (i + 1) % 10 == 0 or i + 1 == total:
                acc = sum(1 for x in results if x.correct) / len(results)
                print(f"  [deep_think] {i+1}/{total} done, running accuracy: {acc:.1%}")

        return self._build_mode_result("deep_think", results)

    # ------------------------------------------------------------------
    # Mode 3: Heavy
    # ------------------------------------------------------------------

    async def eval_full_harness(
        self, questions: list[dict], max_concurrent: int = 2
    ) -> ModeResult:
        """Full orchestrator pipeline with tool calls."""
        harness = self._ensure_harness()
        sem = asyncio.Semaphore(max_concurrent)
        results: list[QuestionResult] = []

        async def _eval_one(q: dict) -> QuestionResult:
            async with sem:
                start = time.monotonic()
                try:
                    # Build context with hints for adapter routing
                    context = self._extract_context(q["question"])

                    # Add instruction for answer format
                    augmented_query = q["question"] + (
                        "\n\nIMPORTANT: After your analysis, state the final answer clearly. "
                        "If multiple choice, end with 'The answer is [letter]'. "
                        "If exact answer, end with 'The answer is [answer]'."
                    )

                    result = await harness.query(augmented_query, context)
                    resp = result["synthesis"]
                    latency = time.monotonic() - start
                    extracted = extract_answer_from_response(resp, q["answer_type"])
                    correct = score_question(resp, q["answer"], q["answer_type"])
                    return QuestionResult(
                        question_id=q["id"], mode="heavy",
                        question_text=q["question"][:200],
                        expected=q["answer"], answer_type=q["answer_type"],
                        predicted_raw=resp, predicted_extracted=extracted,
                        correct=correct, latency_s=round(latency, 2),
                        category=q["category"],
                    )
                except Exception as exc:
                    return QuestionResult(
                        question_id=q["id"], mode="heavy",
                        question_text=q["question"][:200],
                        expected=q["answer"], answer_type=q["answer_type"],
                        predicted_raw="", predicted_extracted="",
                        correct=False, latency_s=round(time.monotonic() - start, 2),
                        category=q["category"], error=str(exc),
                    )

        tasks = [_eval_one(q) for q in questions]
        total = len(tasks)
        for i, coro in enumerate(asyncio.as_completed(tasks)):
            r = await coro
            results.append(r)
            if (i + 1) % 5 == 0 or i + 1 == total:
                acc = sum(1 for x in results if x.correct) / len(results)
                print(f"  [heavy] {i+1}/{total} done, running accuracy: {acc:.1%}")

        return self._build_mode_result("heavy", results)

    # ------------------------------------------------------------------
    # Comparison
    # ------------------------------------------------------------------

    async def run_comparison(
        self,
        questions: list[dict],
        modes: list[str] | None = None,
    ) -> dict[str, ModeResult]:
        """Run all specified modes on the same set of questions."""
        modes = modes or ["simple_llm", "deep_think", "heavy"]
        results: dict[str, ModeResult] = {}

        mode_methods = {
            "simple_llm": self.eval_simple_llm,
            "deep_think": self.eval_deep_think,
            "heavy": self.eval_full_harness,
        }

        for mode in modes:
            method = mode_methods.get(mode)
            if not method:
                print(f"Unknown mode: {mode}, skipping")
                continue
            print(f"\n{'='*60}")
            print(f"Running mode: {mode}")
            print(f"{'='*60}")
            result = await method(questions)
            results[mode] = result
            print(f"  => {mode} accuracy: {result.accuracy:.1%} ({result.correct_count}/{result.total})")

        return results

    def generate_report(self, results: dict[str, ModeResult]) -> str:
        """Generate a comparison report."""
        lines: list[str] = []
        lines.append("=" * 70)
        lines.append("BENCHMARK COMPARISON REPORT")
        lines.append("=" * 70)

        # Summary table
        lines.append("")
        lines.append(f"{'Mode':<20} {'Accuracy':>10} {'Correct':>10} {'Total':>8} {'Avg Latency':>12}")
        lines.append("-" * 62)
        for mode, mr in results.items():
            lines.append(
                f"{mode:<20} {mr.accuracy:>9.1%} {mr.correct_count:>10} "
                f"{mr.total:>8} {mr.avg_latency_s:>10.1f}s"
            )

        # Accuracy by category
        lines.append("")
        lines.append("ACCURACY BY CATEGORY:")
        lines.append("-" * 62)
        all_cats = sorted({cat for mr in results.values() for cat in mr.accuracy_by_category})
        header = f"{'Category':<25}" + "".join(f"{m:>15}" for m in results)
        lines.append(header)
        for cat in all_cats:
            row = f"{cat:<25}"
            for mr in results.values():
                acc = mr.accuracy_by_category.get(cat)
                row += f"{acc:>14.1%}" if acc is not None else f"{'N/A':>15}"
            lines.append(row)

        # Accuracy by answer type
        lines.append("")
        lines.append("ACCURACY BY ANSWER TYPE:")
        lines.append("-" * 62)
        all_types = sorted({t for mr in results.values() for t in mr.accuracy_by_type})
        header = f"{'Type':<25}" + "".join(f"{m:>15}" for m in results)
        lines.append(header)
        for t in all_types:
            row = f"{t:<25}"
            for mr in results.values():
                acc = mr.accuracy_by_type.get(t)
                row += f"{acc:>14.1%}" if acc is not None else f"{'N/A':>15}"
            lines.append(row)

        # Per-question comparison (first N)
        lines.append("")
        lines.append("PER-QUESTION COMPARISON (showing disagreements):")
        lines.append("-" * 70)

        mode_names = list(results.keys())
        if len(mode_names) >= 2:
            # Build question-id -> results map
            q_map: dict[str, dict[str, QuestionResult]] = {}
            for mode, mr in results.items():
                for qr in mr.per_question:
                    q_map.setdefault(qr.question_id, {})[mode] = qr

            disagreements = 0
            for qid, mode_results in sorted(q_map.items()):
                corrects = {m: qr.correct for m, qr in mode_results.items()}
                if len(set(corrects.values())) > 1:
                    disagreements += 1
                    if disagreements <= 20:
                        qr0 = list(mode_results.values())[0]
                        lines.append(f"\n  Q: {qr0.question_text[:100]}...")
                        lines.append(f"  Expected: {qr0.expected}")
                        for m, qr in mode_results.items():
                            mark = "✓" if qr.correct else "✗"
                            lines.append(f"    {m}: {qr.predicted_extracted} [{mark}]")

            lines.append(f"\n  Total disagreements: {disagreements}/{len(q_map)}")

        lines.append("")
        lines.append("=" * 70)
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_context(question: str) -> dict[str, Any]:
        """Extract routing hints from question text (lightweight regex)."""
        context: dict[str, Any] = {}

        # Gene names: uppercase 2-6 letter words that look like gene symbols
        genes = re.findall(r"\b([A-Z][A-Z0-9]{1,5})\b", question)
        # Filter common non-gene words
        common = {"THE", "AND", "FOR", "NOT", "BUT", "ARE", "WAS", "HAS", "THIS", "THAT",
                   "WITH", "FROM", "WHICH", "WHAT", "HOW", "WHO", "WHY", "DOES", "CAN",
                   "DNA", "RNA", "ATP", "GTP", "NADH", "HIV", "MRI", "ICU", "FDA"}
        genes = [g for g in genes if g not in common and len(g) >= 2]
        if genes:
            context["genes"] = list(set(genes))[:5]

        # RSIDs
        rsids = re.findall(r"\b(rs\d+)\b", question, re.IGNORECASE)
        if rsids:
            context["rsid"] = rsids[0]

        # Variant notation (HGVS-like)
        variants = re.findall(r"\b([A-Z][A-Z0-9]+\s*c\.\d+[A-Z>]+)", question)
        if variants:
            context["variant"] = variants[0]

        return context

    @staticmethod
    def _build_mode_result(mode: str, results: list[QuestionResult]) -> ModeResult:
        total = len(results)
        correct = sum(1 for r in results if r.correct)
        accuracy = correct / total if total > 0 else 0.0
        avg_lat = sum(r.latency_s for r in results) / total if total > 0 else 0.0

        # Per-category accuracy
        cat_correct: dict[str, int] = {}
        cat_total: dict[str, int] = {}
        for r in results:
            cat_total[r.category] = cat_total.get(r.category, 0) + 1
            if r.correct:
                cat_correct[r.category] = cat_correct.get(r.category, 0) + 1
        acc_by_cat = {c: cat_correct.get(c, 0) / cat_total[c] for c in cat_total}

        # Per-type accuracy
        type_correct: dict[str, int] = {}
        type_total: dict[str, int] = {}
        for r in results:
            type_total[r.answer_type] = type_total.get(r.answer_type, 0) + 1
            if r.correct:
                type_correct[r.answer_type] = type_correct.get(r.answer_type, 0) + 1
        acc_by_type = {t: type_correct.get(t, 0) / type_total[t] for t in type_total}

        return ModeResult(
            mode=mode,
            accuracy=accuracy,
            total=total,
            correct_count=correct,
            avg_latency_s=round(avg_lat, 2),
            per_question=results,
            accuracy_by_category=acc_by_cat,
            accuracy_by_type=acc_by_type,
        )


# Need re import at module level for _extract_context
import re
