"""Example: multi-modal query combining genomics, wearables, and clinical reasoning."""

import asyncio
from harness.orchestrator import BioMedArena


async def main():
    harness = BioMedArena("config.yaml")

    result = await harness.query(
        "Patient has type 2 diabetes (HbA1c 8.2%), wearable shows declining "
        "activity over 30 days, and carries APOE e4/e4 genotype. "
        "Assess combined cardiometabolic and neurodegenerative risk.",
        context={
            "patient_id": "P042",
            "wearable_data": {"avg_steps_30d": 3200, "trend": "declining"},
            "genotype": {"APOE": "e4/e4"},
            "labs": {"HbA1c": 8.2, "glucose": 185, "LDL": 142},
        },
    )

    print("=== Multi-Modal Query ===")
    print(result["synthesis"])
    print(f"\nRouted to: {result['routed_to']}")
    print(f"\nAdapter results ({len(result['adapter_results'])}):")
    for r in result["adapter_results"]:
        print(f"  [{r['source']}] confidence={r['confidence']:.2f}")
        print(f"    {r['answer'][:120]}...")


if __name__ == "__main__":
    asyncio.run(main())
