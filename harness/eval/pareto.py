"""Pareto frontier analysis: accuracy vs cost trade-off (HAL Harness style).

Given benchmark results across multiple modes/models, identify which configs
are on the Pareto frontier — i.e., not dominated by any other config that
is BOTH cheaper AND more accurate.
"""

from __future__ import annotations

from typing import Any


# Approximate cost per 1M tokens (USD) for common models — update as prices change
DEFAULT_PRICES = {
    "gpt-4o":           {"input": 2.5,  "output": 10.0},
    "gpt-4o-mini":      {"input": 0.15, "output": 0.6},
    "o4-mini":          {"input": 1.1,  "output": 4.4},
    "o3-mini":          {"input": 1.1,  "output": 4.4},
    "gemini-2.5-flash": {"input": 0.075,"output": 0.30},
    "gemini-2.5-pro":   {"input": 1.25, "output": 5.0},
    "claude-sonnet-4-5":{"input": 3.0,  "output": 15.0},
    "claude-opus-4-6":  {"input": 15.0, "output": 75.0},
}


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str = "gpt-4o",
) -> float:
    """USD cost estimate. Falls back to gpt-4o pricing if model unknown."""
    p = DEFAULT_PRICES.get(model, DEFAULT_PRICES["gpt-4o"])
    return (input_tokens * p["input"] + output_tokens * p["output"]) / 1_000_000


def pareto_frontier(points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return the subset of points on the Pareto frontier.

    Each point dict must have:
        accuracy:   higher is better
        cost_usd:   lower is better
        label:      identifier for the config (e.g., "gpt-4o + harness")

    A point is on the frontier iff no other point has BOTH higher accuracy
    AND lower cost.
    """
    frontier = []
    for p in points:
        dominated = False
        for q in points:
            if q is p:
                continue
            if (q["accuracy"] >= p["accuracy"] and
                q["cost_usd"] <= p["cost_usd"] and
                (q["accuracy"] > p["accuracy"] or q["cost_usd"] < p["cost_usd"])):
                dominated = True
                break
        if not dominated:
            frontier.append(p)
    # Sort frontier by cost ascending
    frontier.sort(key=lambda x: x["cost_usd"])
    return frontier


def print_pareto_table(points: list[dict[str, Any]]) -> str:
    """Render points + frontier markers as a text table."""
    frontier_labels = {p["label"] for p in pareto_frontier(points)}

    lines = []
    lines.append("=" * 78)
    lines.append("PARETO FRONTIER: Accuracy vs Cost")
    lines.append("=" * 78)
    lines.append(f"{'On Frontier':<13}{'Config':<35}{'Accuracy':>10}{'Cost (USD)':>14}{'$/correct':>12}")
    lines.append("-" * 78)

    sorted_pts = sorted(points, key=lambda p: -p["accuracy"])
    for p in sorted_pts:
        marker = "★" if p["label"] in frontier_labels else " "
        cost_per = p["cost_usd"] / max(p.get("correct", 1), 1)
        lines.append(
            f"  {marker:<11}{p['label']:<35}{p['accuracy']:>9.1%}"
            f"{p['cost_usd']:>13.4f}{cost_per:>11.4f}"
        )
    lines.append("")
    lines.append("★ = on Pareto frontier (not dominated by any cheaper-AND-more-accurate config)")
    lines.append("=" * 78)
    return "\n".join(lines)


def build_points_from_leaderboard(
    leaderboard: dict[str, Any],
    avg_input_tokens_per_q: int = 1500,
    avg_output_tokens_per_q: int = 800,
    model_name: str = "gemini-2.5-flash",
) -> list[dict[str, Any]]:
    """Convert a leaderboard JSON to Pareto points.

    Estimates cost = total_tasks × (input + output tokens) × price_per_token.
    For more accurate cost, integrate token counters into LLMClient.
    """
    points = []
    aggregate = leaderboard.get("aggregate", {})
    for mode, stats in aggregate.items():
        n = stats.get("total_tasks", 0)
        accuracy = stats.get("task_success_rate", 0)
        # Modes that make multiple LLM calls cost more
        multiplier = {
            "simple_llm":        1,
            "deep_think":        1,
            "heavy":             2,    # triage + reason
            "light":             3,    # avg 2-3 tool turns
            "self_consistency:fc":     15,
            "self_consistency:simple":  5,
            "self_consistency:deep":    5,
            "self_consistency:harness": 10,
        }.get(mode, 1)
        in_toks = n * avg_input_tokens_per_q * multiplier
        out_toks = n * avg_output_tokens_per_q * multiplier
        cost = estimate_cost(in_toks, out_toks, model_name)
        correct = int(round(accuracy * n))
        points.append({
            "label": mode,
            "accuracy": accuracy,
            "cost_usd": round(cost, 4),
            "tokens_in": in_toks,
            "tokens_out": out_toks,
            "n": n,
            "correct": correct,
        })
    return points
