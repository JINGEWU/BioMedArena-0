"""Software engineering benchmark loader.

Task: given a Python repo at a base commit + an issue, produce a patch
that resolves the issue and passes all FAIL_TO_PASS / PASS_TO_PASS tests.

For our harness, we evaluate as TEXT QA: ask the LLM to describe the patch
or the root cause. Real execution would need running tests in repo containers.
"""

from __future__ import annotations

from typing import Any


def load_swebench_tasks(
    limit: int | None = None,
    variant: str = "Verified",  # Verified | Lite | Mini
) -> list[dict[str, Any]]:
    """Load software engineering tasks. Returns text-QA-style tasks."""
    try:
        from datasets import load_dataset
    except ImportError:
        return []

    try:
        if variant == "Verified":
            ds = load_dataset("SWE-bench/SWE-bench_Verified", split="test")
        elif variant == "Lite":
            ds = load_dataset("SWE-bench/SWE-bench_Lite", split="test")
        else:
            ds = load_dataset("SWE-bench/SWE-bench", split="test")
    except Exception:
        return []

    tasks = []
    for row in ds:
        instance_id = row.get("instance_id", f"swe_{len(tasks):04d}")
        repo = row.get("repo", "")
        problem = row.get("problem_statement", "")
        hints = row.get("hints_text", "")
        gold_patch = row.get("patch", "")
        difficulty = row.get("difficulty", "unknown")

        # Format as text QA: ask for the root cause / fix description
        question = (
            f"# Software Engineering Task ({repo})\n\n"
            f"## Issue\n{problem[:2000]}\n\n"
            f"## Hints\n{hints[:500] if hints else 'None'}\n\n"
            f"## Question\n"
            f"What is the root cause of this issue and what code change "
            f"would resolve it? Provide a concise answer."
        )

        # Use the gold patch as the "expected" — judge with LLM-as-judge
        # (since the task is open-ended, exact match won't work)
        tasks.append({
            "id": instance_id,
            "question": question,
            "answer": gold_patch[:1500],  # truncate for storage
            "answer_type": "openText",  # signal to scorer: use semantic match
            "category": f"SWE-bench/{difficulty}",
            "raw_subject": repo,
            "context": {
                "repo": repo,
                "instance_id": instance_id,
                "difficulty": difficulty,
            },
        })
        if limit and len(tasks) >= limit:
            break

    return tasks
