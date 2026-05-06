"""Unified benchmark runner across clinical, genomic, and diagnostic benchmarks."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from harness.eval.scoring import score_question
from harness.orchestrator import BioMedArena

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    task_id: str
    query: str
    expected: str | None
    actual: str
    routed_to: list[str]
    latency_s: float
    correct: bool | None = None  # None if no ground truth
    adapter_results: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class BenchmarkSummary:
    benchmark_name: str
    total: int
    correct: int
    incorrect: int
    unscored: int
    avg_latency_s: float
    results: list[BenchmarkResult]


class BenchmarkRunner:
    """Run evaluation benchmarks through the harness."""

    def __init__(self, config_path: str = "config.yaml"):
        self.harness = BioMedArena(config_path)

    async def run_benchmark(
        self,
        benchmark_name: str,
        tasks: list[dict[str, Any]],
        max_concurrent: int = 5,
    ) -> BenchmarkSummary:
        """Run a list of benchmark tasks.

        Each task dict should have:
            query: str
            context: dict (optional)
            expected: str (optional ground truth)
            task_id: str (optional)
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        results: list[BenchmarkResult] = []

        async def _run_task(idx: int, task: dict) -> BenchmarkResult:
            async with semaphore:
                task_id = task.get("task_id", f"task_{idx}")
                query = task["query"]
                context = task.get("context")
                expected = task.get("expected")

                logger.info("Running task %s: %s", task_id, query[:80])
                start = time.monotonic()

                try:
                    result = await self.harness.query(query, context)
                    latency = time.monotonic() - start
                    actual = result["synthesis"]
                    routed = result["routed_to"]
                    adapter_results = result["adapter_results"]
                except Exception as exc:
                    latency = time.monotonic() - start
                    actual = f"Error: {exc}"
                    routed = []
                    adapter_results = []

                correct = None
                if expected:
                    correct = self._check_correctness(
                        expected,
                        actual,
                        task.get("answer_type", "exactMatch"),
                        task.get("context") or {},
                    )

                return BenchmarkResult(
                    task_id=task_id,
                    query=query,
                    expected=expected,
                    actual=actual,
                    routed_to=routed,
                    latency_s=round(latency, 2),
                    correct=correct,
                    adapter_results=adapter_results,
                )

        coros = [_run_task(i, t) for i, t in enumerate(tasks)]
        results = list(await asyncio.gather(*coros))

        correct = sum(1 for r in results if r.correct is True)
        incorrect = sum(1 for r in results if r.correct is False)
        unscored = sum(1 for r in results if r.correct is None)
        avg_latency = sum(r.latency_s for r in results) / max(len(results), 1)

        return BenchmarkSummary(
            benchmark_name=benchmark_name,
            total=len(results),
            correct=correct,
            incorrect=incorrect,
            unscored=unscored,
            avg_latency_s=round(avg_latency, 2),
            results=results,
        )

    @staticmethod
    def _check_correctness(
        expected: str,
        actual: str,
        answer_type: str = "exactMatch",
        context: dict[str, Any] | None = None,
    ) -> bool:
        """Score via the shared deterministic scorer stack."""
        return bool(score_question(actual, expected, answer_type, context or {}))

    def save_results(self, summary: BenchmarkSummary, output_path: str) -> None:
        """Save benchmark results to JSON."""
        data = {
            "benchmark": summary.benchmark_name,
            "total": summary.total,
            "correct": summary.correct,
            "incorrect": summary.incorrect,
            "unscored": summary.unscored,
            "avg_latency_s": summary.avg_latency_s,
            "results": [
                {
                    "task_id": r.task_id,
                    "query": r.query,
                    "expected": r.expected,
                    "actual": r.actual[:500],
                    "routed_to": r.routed_to,
                    "latency_s": r.latency_s,
                    "correct": r.correct,
                }
                for r in summary.results
            ],
        }
        Path(output_path).write_text(json.dumps(data, indent=2))
        logger.info("Results saved to %s", output_path)

    # ------------------------------------------------------------------
    # Pre-built benchmark loaders
    # ------------------------------------------------------------------

    @staticmethod
    def load_genotex_tasks(genotex_path: str = "vendors/GenoTEX") -> list[dict[str, Any]]:
        """Load genomic benchmark tasks."""
        tasks_dir = Path(genotex_path) / "benchmark"
        if not tasks_dir.exists():
            logger.warning("GenoTEX benchmark dir not found: %s", tasks_dir)
            return []

        tasks = []
        for f in sorted(tasks_dir.glob("*.json")):
            data = json.loads(f.read_text())
            tasks.append({
                "task_id": f.stem,
                "query": data.get("query", data.get("task", "")),
                "context": data.get("context", {}),
                "expected": data.get("expected", data.get("answer")),
            })
        return tasks

    @staticmethod
    def load_medagentbench_tasks(mab_path: str = "vendors/MedAgentBench") -> list[dict[str, Any]]:
        """Load clinical EHR benchmark tasks."""
        tasks_file = Path(mab_path) / "data" / "tasks.json"
        if not tasks_file.exists():
            logger.warning("MedAgentBench tasks not found: %s", tasks_file)
            return []

        all_tasks = json.loads(tasks_file.read_text())
        return [
            {
                "task_id": t.get("task_id", f"mab_{i}"),
                "query": t.get("instruction", t.get("task", "")),
                "context": t.get("context", {}),
                "expected": t.get("expected_output"),
            }
            for i, t in enumerate(all_tasks[:50])  # limit for reasonable runtime
        ]
