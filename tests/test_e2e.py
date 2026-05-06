"""End-to-end tests — require LLM API keys and/or vendor repos."""

import os
import pytest
import asyncio

from harness.orchestrator import BioMedArena


pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set; skipping e2e tests",
)


class TestE2EGenomics:
    @pytest.fixture
    def harness(self):
        return BioMedArena("config.yaml")

    @pytest.mark.asyncio
    async def test_brca1_query(self, harness):
        result = await harness.query(
            "What is BRCA1 and what cancers is it associated with?",
            context={"genes": ["BRCA1"]},
        )
        assert result["synthesis"]
        assert len(result["adapter_results"]) > 0

    @pytest.mark.asyncio
    async def test_multimodal_query(self, harness):
        result = await harness.query(
            "Patient has diabetes and declining activity. Assess risk.",
            context={
                "wearable_data": {"avg_steps_30d": 3000, "trend": "declining"},
                "labs": {"HbA1c": 8.2, "glucose": 185},
            },
        )
        assert result["synthesis"]
        assert len(result["routed_to"]) > 0
