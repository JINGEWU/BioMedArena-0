"""Example: genomics-focused query through the harness."""

import asyncio
from harness.orchestrator import BioMedArena


async def main():
    harness = BioMedArena("config.yaml")

    # Single-gene variant query
    result = await harness.query(
        "What is the clinical significance of BRCA1 c.5266dupC? "
        "What cancers is it associated with and what screening is recommended?",
        context={
            "genes": ["BRCA1"],
            "variant": "BRCA1 c.5266dupC",
        },
    )
    print("=== Genomics Query ===")
    print(result["synthesis"])
    print(f"\nRouted to: {result['routed_to']}")

    # Gene-set analysis query
    result = await harness.query(
        "What biological pathways connect TP53, BRCA1, and ATM? "
        "How do mutations in these genes interact in cancer predisposition?",
        context={"genes": ["TP53", "BRCA1", "ATM"]},
    )
    print("\n=== Gene-Set Query ===")
    print(result["synthesis"])
    print(f"\nRouted to: {result['routed_to']}")


if __name__ == "__main__":
    asyncio.run(main())
