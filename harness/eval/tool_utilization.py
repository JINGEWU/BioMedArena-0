"""Tool utilization efficiency metric.

Given a set of tool calls made by an agent and the question/task,
computes:
    tool_precision: fraction of tools called that were relevant
    tool_recall:    fraction of tools that SHOULD have been called that were
    f1:             2PR/(P+R)
    redundancy:     fraction of calls that were duplicates (same tool+args)

Ground-truth "which tools should be called" is inferred from task category
and keywords. For a rigorous version, an LLM-judge can classify each tool
call as relevant/irrelevant.
"""

from __future__ import annotations

import re
from typing import Any


# Heuristic mapping from task signals to expected tools
CATEGORY_TO_EXPECTED_TOOLS = {
    "genomics":      {"gene_lookup", "ncbi_gene", "pubmed_search", "clinvar_lookup", "omim_lookup"},
    "biology":       {"gene_lookup", "ncbi_gene", "pubmed_search"},
    "medicine":      {"pubmed_search", "rxnav_drug", "medlineplus_topic", "compute_calculator"},
    "chemistry":     {"pubmed_search", "rxnav_drug", "openfda_adverse"},
    "ehr":           {"compute_calculator", "rxnav_drug", "clinvar_lookup"},
    "clinical":      {"compute_calculator", "rxnav_drug", "medlineplus_topic", "pubmed_search"},
    "medcalc":       {"compute_calculator", "calculator_eval"},
    "rag":           {"pubmed_search", "rxnav_drug", "openfda_adverse", "omim_lookup", "orphanet_lookup"},
    "swe-bench":     {"code_search", "python_exec"},
}


def _expected_tools_for_task(task: dict[str, Any]) -> set[str]:
    """Heuristically determine which tools *should* have been called."""
    cat = (task.get("category") or "").lower()
    expected: set[str] = set()
    for keyword, tools in CATEGORY_TO_EXPECTED_TOOLS.items():
        if keyword in cat:
            expected.update(tools)

    # Additional signals from the question text
    q = (task.get("question") or "").lower()
    if "calculate" in q or "compute" in q or "score" in q:
        expected.add("compute_calculator")
    if re.search(r"\b(patch|bug|function|class|variable|repo)\b", q):
        expected.add("code_search")
    if re.search(r"\brs\d{3,}\b", q):  # SNP / rsid
        expected.add("clinvar_lookup")
    if re.search(r"\b(drug|medication|dose|interaction)\b", q):
        expected.add("rxnav_drug")

    return expected


def _clean_tool_name(name: str) -> str:
    """Strip colon-prefixed mode tags from tool names."""
    if not name:
        return ""
    if ":" in name:
        return name.split(":")[0]
    return name


def compute_tool_utilization(
    tools_called: list[str],
    task: dict[str, Any],
) -> dict[str, float]:
    """Compute precision / recall / F1 / redundancy for a single task."""
    if not tools_called:
        return {
            "tool_precision": 0.0,
            "tool_recall": 0.0,
            "tool_f1": 0.0,
            "tool_redundancy": 0.0,
            "tools_called_count": 0,
            "unique_tools_called": 0,
        }

    # Strip meta tags (triage_skip, vision) — keep actual tool names
    meta_prefixes = ("triage_skip", "vision")
    actual_tools = [t for t in tools_called if not any(t.startswith(p) for p in meta_prefixes)]
    unique_tools = set(actual_tools)

    expected = _expected_tools_for_task(task)

    if not actual_tools:
        # Only meta-tags, no real tools
        return {
            "tool_precision": 0.0,
            "tool_recall": 0.0,
            "tool_f1": 0.0,
            "tool_redundancy": 0.0,
            "tools_called_count": 0,
            "unique_tools_called": 0,
        }

    # Precision: fraction of called tools that are in expected set
    if expected:
        tp = len(unique_tools & expected)
        precision = tp / len(unique_tools) if unique_tools else 0.0
        recall = tp / len(expected) if expected else 0.0
    else:
        # No expected tools → any call is "extra" precision=0; recall undefined, set to 1
        precision = 0.0
        recall = 1.0

    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    redundancy = 1.0 - (len(unique_tools) / len(actual_tools)) if actual_tools else 0.0

    return {
        "tool_precision": round(precision, 3),
        "tool_recall": round(recall, 3),
        "tool_f1": round(f1, 3),
        "tool_redundancy": round(redundancy, 3),
        "tools_called_count": len(actual_tools),
        "unique_tools_called": len(unique_tools),
    }


def aggregate_tool_utilization(
    per_question_tools: list[tuple[list[str], dict]],
) -> dict[str, float]:
    """Aggregate tool-utilization over many tasks."""
    if not per_question_tools:
        return {}
    per_task = [compute_tool_utilization(tools, task) for tools, task in per_question_tools]
    n = len(per_task)
    return {
        "mean_tool_precision":  round(sum(p["tool_precision"]  for p in per_task) / n, 3),
        "mean_tool_recall":     round(sum(p["tool_recall"]     for p in per_task) / n, 3),
        "mean_tool_f1":         round(sum(p["tool_f1"]         for p in per_task) / n, 3),
        "mean_tool_redundancy": round(sum(p["tool_redundancy"] for p in per_task) / n, 3),
        "mean_tools_per_task":  round(sum(p["tools_called_count"] for p in per_task) / n, 2),
    }
