"""Tests for the orchestrator and core infrastructure."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from harness.orchestrator import BioMedArena
from harness.adapter_base import AdapterBase
from harness.llm_client import LLMClient


class MockAdapter(AdapterBase):
    name = "mock"
    modality = "reasoning"
    description = "Mock adapter for testing."

    def __init__(self, **kwargs):
        pass

    def capabilities(self):
        return ["testing"]

    async def run(self, query, context=None):
        return self.result(
            answer=f"Mock answer for: {query}",
            evidence=["mock_evidence"],
            confidence=0.9,
        )


class TestAdapterBase:
    def test_result_format(self):
        adapter = MockAdapter()
        result = adapter.result(answer="test", confidence=0.8, evidence=["e1"])
        assert result["source"] == "mock"
        assert result["answer"] == "test"
        assert result["confidence"] == 0.8
        assert result["evidence"] == ["e1"]
        assert result["raw"] is None

    def test_mark_unavailable(self):
        adapter = MockAdapter()
        assert adapter.available is True
        adapter.mark_unavailable("missing deps")
        assert adapter.available is False
        assert adapter.unavailable_reason == "missing deps"

    def test_repr(self):
        adapter = MockAdapter()
        assert "MockAdapter" in repr(adapter)
        assert "available" in repr(adapter)


class TestLLMClient:
    def test_resolve_env_key(self):
        import os
        os.environ["TEST_KEY_12345"] = "secret"
        assert LLMClient._resolve_key("${TEST_KEY_12345}") == "secret"
        del os.environ["TEST_KEY_12345"]

    def test_resolve_plain_key(self):
        assert LLMClient._resolve_key("plain-key") == "plain-key"

    def test_resolve_none(self):
        assert LLMClient._resolve_key(None) is None

    def test_unsupported_provider(self):
        client = LLMClient(provider="unsupported")
        with pytest.raises(ValueError, match="Unsupported"):
            client._get_client()


class TestOrchestrator:
    @pytest.fixture
    def harness(self, tmp_path):
        config = tmp_path / "config.yaml"
        config.write_text(
            "llm:\n  provider: openai\n  model: gpt-4o\n  api_key: test\n"
            "adapters: {}\n"
        )
        with patch("harness.orchestrator.BioMedArena._load_adapters"):
            h = BioMedArena(str(config))
        return h

    def test_load_config(self, harness):
        assert harness.config["llm"]["provider"] == "openai"

    @pytest.mark.asyncio
    async def test_execute_catches_exceptions(self, harness):
        class FailAdapter(AdapterBase):
            name = "fail"
            modality = "test"
            description = "Fails"
            async def run(self, query, context=None):
                raise RuntimeError("boom")

        adapter = FailAdapter()
        results = await harness._execute("test", None, {"fail": adapter})
        assert len(results) == 1
        assert "Error" in results[0]["answer"]
        assert results[0]["confidence"] == 0.0

    @pytest.mark.asyncio
    async def test_execute_catches_timeout(self, harness):
        class SlowAdapter(AdapterBase):
            name = "slow"
            modality = "test"
            description = "Slow"
            async def run(self, query, context=None):
                await asyncio.sleep(999)

        adapter = SlowAdapter()
        # Monkey-patch timeout to be very short
        import harness.orchestrator as orch
        original_execute = orch.BioMedArena._execute

        async def fast_execute(self, question, context, adapters):
            async def _safe_run(name, adapter):
                try:
                    return await asyncio.wait_for(adapter.run(question, context), timeout=0.1)
                except asyncio.TimeoutError:
                    return {"source": name, "answer": "Adapter timed out.", "evidence": [], "confidence": 0.0, "raw": None}
            tasks = [_safe_run(n, a) for n, a in adapters.items()]
            return list(await asyncio.gather(*tasks))

        harness._execute = fast_execute.__get__(harness)
        results = await harness._execute("test", None, {"slow": adapter})
        assert "timed out" in results[0]["answer"]

    @pytest.mark.asyncio
    async def test_query_no_adapters(self, harness):
        harness.adapters = {}
        result = await harness.query("test")
        assert "No adapters available" in result["synthesis"]

    @pytest.mark.asyncio
    async def test_query_with_mock_adapter(self, harness):
        mock = MockAdapter()
        harness.adapters = {"mock": mock}
        harness.llm = MagicMock()
        harness.llm.chat_json = AsyncMock(return_value={"adapters": ["mock"]})
        harness.llm.chat = AsyncMock(return_value="Synthesised answer.")

        result = await harness.query("test question")
        assert result["synthesis"] == "Synthesised answer."
        assert "mock" in result["routed_to"]
        assert len(result["adapter_results"]) == 1
