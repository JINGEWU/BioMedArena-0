"""Core orchestrator: route → execute → synthesise."""

from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any

import yaml

from harness.adapter_base import AdapterBase
from harness.llm_client import LLMClient

logger = logging.getLogger(__name__)


class BioMedArena:
    """Main entry point. Loads config, instantiates adapters, and handles queries."""

    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.llm = self._build_llm()
        self.adapters: dict[str, AdapterBase] = {}
        self._load_adapters()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    @staticmethod
    def _load_config(path: str) -> dict[str, Any]:
        raw = Path(path).read_text()
        # Resolve ${ENV_VAR} references
        for key, val in os.environ.items():
            raw = raw.replace(f"${{{key}}}", val)
        return yaml.safe_load(raw)

    def _build_llm(self) -> LLMClient:
        cfg = self.config.get("llm", {})
        return LLMClient(
            provider=cfg.get("provider", "openai"),
            model=cfg.get("model", "gpt-4o"),
            api_key=cfg.get("api_key"),
            base_url=cfg.get("base_url"),
        )

    def _load_adapters(self) -> None:
        from harness.adapters import ADAPTER_REGISTRY

        for name, acfg in self.config.get("adapters", {}).items():
            if not acfg.get("enabled", False):
                logger.info("Adapter %s disabled, skipping", name)
                continue
            cls_name = acfg.get("class")
            cls = ADAPTER_REGISTRY.get(cls_name)
            if cls is None:
                logger.warning("Adapter class %s not found in registry", cls_name)
                continue
            try:
                adapter = cls(config=acfg, llm=self.llm)
                self.adapters[name] = adapter
                logger.info("Loaded adapter %s (%s)", name, "available" if adapter.available else "unavailable")
            except Exception:
                logger.exception("Failed to instantiate adapter %s", name)

    # ------------------------------------------------------------------
    # Query pipeline
    # ------------------------------------------------------------------

    async def query(self, question: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Route → execute → synthesise."""
        available = {n: a for n, a in self.adapters.items() if a.available}
        if not available:
            return {"synthesis": "No adapters available.", "adapter_results": [], "routed_to": []}

        # 1. Route
        selected_names = await self._route(question, context, available)
        selected = {n: available[n] for n in selected_names if n in available}
        if not selected:
            selected = available  # fallback: use all

        # 2. Execute in parallel
        results = await self._execute(question, context, selected)

        # 3. Synthesise
        synthesis = await self._synthesise(question, context, results)

        return {
            "synthesis": synthesis,
            "adapter_results": results,
            "routed_to": list(selected.keys()),
        }

    # ------------------------------------------------------------------
    # Route
    # ------------------------------------------------------------------

    async def _route(
        self, question: str, context: dict[str, Any] | None, adapters: dict[str, AdapterBase],
    ) -> list[str]:
        adapter_descriptions = []
        for name, adapter in adapters.items():
            adapter_descriptions.append({
                "name": name,
                "modality": adapter.modality,
                "description": adapter.description,
                "capabilities": adapter.capabilities(),
            })

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a medical query router. Given a user question and a list of "
                    "available specialist adapters, return a JSON object with a single key "
                    '"adapters" containing a list of adapter names that should be invoked '
                    "to answer the question. Select 1-5 adapters that are most relevant. "
                    "Return ONLY valid JSON."
                ),
            },
            {
                "role": "user",
                "content": json.dumps({
                    "question": question,
                    "context": context,
                    "available_adapters": adapter_descriptions,
                }),
            },
        ]

        try:
            resp = await self.llm.chat_json(messages)
            names = resp.get("adapters", [])
            if isinstance(names, list) and names:
                return [n for n in names if isinstance(n, str)]
        except Exception:
            logger.exception("Routing LLM call failed, using all adapters")
        return list(adapters.keys())

    # ------------------------------------------------------------------
    # Execute
    # ------------------------------------------------------------------

    async def _execute(
        self, question: str, context: dict[str, Any] | None, adapters: dict[str, AdapterBase],
    ) -> list[dict[str, Any]]:
        async def _safe_run(name: str, adapter: AdapterBase) -> dict[str, Any]:
            try:
                return await asyncio.wait_for(adapter.run(question, context), timeout=120)
            except asyncio.TimeoutError:
                logger.error("Adapter %s timed out", name)
                return {"source": name, "answer": "Adapter timed out.", "evidence": [], "confidence": 0.0, "raw": None}
            except Exception as exc:
                logger.exception("Adapter %s raised an exception", name)
                return {"source": name, "answer": f"Error: {exc}", "evidence": [], "confidence": 0.0, "raw": None}

        tasks = [_safe_run(n, a) for n, a in adapters.items()]
        return list(await asyncio.gather(*tasks))

    # ------------------------------------------------------------------
    # Synthesise
    # ------------------------------------------------------------------

    async def _synthesise(
        self, question: str, context: dict[str, Any] | None, results: list[dict[str, Any]],
    ) -> str:
        results_summary = []
        for r in results:
            results_summary.append({
                "source": r.get("source"),
                "answer": r.get("answer"),
                "evidence": r.get("evidence", []),
                "confidence": r.get("confidence"),
            })

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a senior physician synthesising input from multiple medical AI "
                    "specialists. Produce a unified, evidence-based response to the patient "
                    "query below. Cite which specialist (source) provided each finding. "
                    "Highlight agreements, flag disagreements, and note confidence levels. "
                    "Include appropriate caveats about AI-generated medical information."
                ),
            },
            {
                "role": "user",
                "content": json.dumps({
                    "question": question,
                    "context": context,
                    "specialist_results": results_summary,
                }),
            },
        ]

        try:
            return await self.llm.chat(messages, temperature=0.3, max_tokens=4096)
        except Exception:
            logger.exception("Synthesis LLM call failed")
            # Fallback: concatenate raw answers
            parts = [f"[{r['source']}] {r['answer']}" for r in results if r.get("answer")]
            return "\n\n".join(parts) if parts else "Synthesis failed and no adapter results available."
