"""MASEval-compatible thin adapter for BioMedArena.

Source pattern: parameterlab/MASEval (Parameter Lab + Oxford 2025)
Paper: "Framework choice impacts performance as much as model choice."

MASEval's `AgentAdapter` requires two methods:
    _run_agent(query: str) -> str
    get_messages() -> MessageHistory

This file provides a BioMedArenaAdapter so our framework can be plugged
into MASEval and benchmarked against other agent frameworks (smolagents,
LangGraph, LlamaIndex, CAMEL) on multi-agent benchmarks
(MACS, ConVerse, MultiAgentBench, GAIA, AgentBench, etc.).

Usage (in a MASEval evaluation script):
    from harness.eval.maseval_adapter import BioMedArenaAdapter
    adapter = BioMedArenaAdapter(harness_config="config_gemini.yaml", mode="heavy")
    # Then pass to MASEval's benchmark.setup_agents(...)
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Message:
    role: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MessageHistory:
    """Per-agent message history (MASEval interface)."""
    agent_name: str
    messages: list[Message] = field(default_factory=list)

    def append(self, role: str, content: str, **metadata: Any):
        self.messages.append(Message(role=role, content=content, metadata=metadata))

    def to_list(self) -> list[dict[str, Any]]:
        return [
            {"role": m.role, "content": m.content, **m.metadata}
            for m in self.messages
        ]


class BioMedArenaAdapter:
    """Plug BioMedArena into MASEval as an evaluation target.

    Implements MASEval's AgentAdapter interface (two methods: _run_agent + get_messages).
    """

    def __init__(
        self,
        harness_config: str = "config_gemini.yaml",
        mode: str = "heavy",
        agent_name: str = "BioMedArena",
    ):
        from harness.eval.benchmark_suite import BenchmarkSuite
        self.suite = BenchmarkSuite(config_path=harness_config)
        self.mode = mode
        self.agent_name = agent_name
        self.history = MessageHistory(agent_name=agent_name)

    def _run_agent(self, query: str) -> str:
        """Execute the harness on a single query (MASEval sync interface)."""
        self.history.append("user", query)

        # Build a minimal task dict matching our internal schema
        task = {
            "id": f"maseval_{len(self.history.messages)}",
            "question": query,
            "answer": "",
            "answer_type": "openText",
            "category": "MASEval",
            "context": {},
        }

        # Dispatch to selected mode
        loop = asyncio.new_event_loop()
        try:
            if self.mode == "simple_llm":
                resp, tools = loop.run_until_complete(self.suite._run_simple(task))
            elif self.mode == "deep_think":
                resp, tools = loop.run_until_complete(self.suite._run_deep(task))
            elif self.mode == "heavy":
                resp, tools = loop.run_until_complete(self.suite._run_harness(task))
            elif self.mode == "light":
                resp, tools = loop.run_until_complete(self.suite._run_function_calling(task))
            else:
                resp, tools = loop.run_until_complete(self.suite._run_simple(task))
        finally:
            loop.close()

        self.history.append("assistant", resp, tools_called=tools, mode=self.mode)
        return resp

    def get_messages(self) -> MessageHistory:
        """Return per-agent message history (MASEval interface)."""
        return self.history

    def reset(self) -> None:
        """Clear message history for a new task."""
        self.history = MessageHistory(agent_name=self.agent_name)
