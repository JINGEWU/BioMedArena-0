"""Example: EHR-focused query with clinical calculators."""

import asyncio
from harness.orchestrator import BioMedArena


async def main():
    harness = BioMedArena("config.yaml")

    # Clinical calculator query
    result = await harness.query(
        "Calculate CHA2DS2-VASc score and bleeding risk for a 72-year-old female "
        "with atrial fibrillation, hypertension, and prior stroke.",
        context={
            "calculator": "cha2ds2_vasc",
            "calculator_params": {
                "age": 72,
                "sex": "female",
                "hypertension": True,
                "stroke_tia_history": True,
            },
        },
    )
    print("=== Clinical Calculator Query ===")
    print(result["synthesis"])

    # EHR reasoning query
    result = await harness.query(
        "Patient P042 was admitted 3 days ago with acute kidney injury. "
        "Current creatinine is 3.2 (baseline 1.1). What is the KDIGO stage "
        "and what are the recommended next steps?",
        context={
            "patient_id": "P042",
            "labs": {"creatinine": 3.2, "baseline_creatinine": 1.1, "bun": 45},
        },
    )
    print("\n=== EHR Reasoning Query ===")
    print(result["synthesis"])


if __name__ == "__main__":
    asyncio.run(main())
