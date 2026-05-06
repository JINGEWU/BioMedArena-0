"""Pareto curve visualization (matplotlib-based, optional dependency).

Given a leaderboard with multiple modes (and optionally multiple models),
plot accuracy vs cost. Frontier points highlighted.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harness.eval.pareto import pareto_frontier


def plot_pareto(
    points: list[dict[str, Any]],
    output_path: str,
    title: str = "Accuracy vs Cost (Pareto frontier)",
) -> str | None:
    """Render a PNG scatter plot of accuracy vs cost with frontier highlighted.

    Each point should have: label, accuracy, cost_usd. An optional "model" field
    groups points by colour.

    Returns: output_path on success, None on error (matplotlib missing, etc).
    """
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except ImportError:
        return None

    if not points:
        return None

    frontier = {p["label"] for p in pareto_frontier(points)}

    # Group by model if present
    groups: dict[str, list[dict]] = {}
    for p in points:
        model = p.get("model", "default")
        groups.setdefault(model, []).append(p)

    fig, ax = plt.subplots(figsize=(9, 6))
    colours = plt.cm.tab10.colors  # type: ignore
    for i, (model, pts) in enumerate(groups.items()):
        colour = colours[i % len(colours)]
        # Split into frontier vs non-frontier
        front = [p for p in pts if p["label"] in frontier]
        dom = [p for p in pts if p["label"] not in frontier]
        if dom:
            ax.scatter([p["cost_usd"] for p in dom],
                        [p["accuracy"] * 100 for p in dom],
                        s=60, alpha=0.4, marker="o", color=colour,
                        label=f"{model} (dominated)")
        if front:
            ax.scatter([p["cost_usd"] for p in front],
                        [p["accuracy"] * 100 for p in front],
                        s=180, marker="*", color=colour, edgecolors="black",
                        linewidths=1.5, label=f"{model} (frontier)")

        # Annotate each point with mode label
        for p in pts:
            ax.annotate(
                p["label"], (p["cost_usd"], p["accuracy"] * 100),
                xytext=(5, 5), textcoords="offset points",
                fontsize=8, alpha=0.8,
            )

    # Connect frontier points with a dashed line
    front_pts = sorted(
        [p for p in points if p["label"] in frontier],
        key=lambda x: x["cost_usd"],
    )
    if len(front_pts) > 1:
        ax.plot(
            [p["cost_usd"] for p in front_pts],
            [p["accuracy"] * 100 for p in front_pts],
            linestyle="--", linewidth=1.5, color="gray", alpha=0.7,
        )

    ax.set_xlabel("Estimated cost (USD)")
    ax.set_ylabel("Accuracy (%)")
    ax.set_title(title)
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="lower right", fontsize=9)
    fig.tight_layout()

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path
