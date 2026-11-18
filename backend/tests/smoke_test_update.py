"""Manual smoke test: python backend/tests/smoke_test_update.py

Runs the initial plan, then feeds the two real practice-update messages
through the update engine, checking it reproduces the plan document's
worked example (printing correction -> Rs. 529,000 / Rs. 121,000) and
correctly rejects the insufficient food-box reduction.
"""

import os
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

load_dotenv()

from engine.orchestrator import run_plan  # noqa: E402
from engine.update_engine import run_update  # noqa: E402
from services.message_service import read_message_file  # noqa: E402
from services.model_service import ModelService  # noqa: E402

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def main() -> None:
    model = ModelService(
        api_key=os.environ["GROQ_API_KEY"],
        model_name=os.environ.get("MODEL_NAME", "openai/gpt-oss-20b"),
    )
    initial_messages = read_message_file(os.path.join(DATA_DIR, "messages.txt"))
    known_fingerprints = {m.fingerprint for m in initial_messages}

    plan = run_plan(
        model,
        initial_messages,
        student_count=150,
        staff_count=10,
        team_count=50,
        approved_budget=650000,
    )
    print("Initial total committed:", plan["budget"].total_committed)
    print("Initial remaining:", plan["budget"].remaining)
    print()

    practice_messages = read_message_file(os.path.join(DATA_DIR, "practice_updates.txt"))

    updated_plan = run_update(
        plan,
        practice_messages,
        known_fingerprints,
        model,
        required_capacity=plan["required_capacity"],
        approved_budget=650000,
    )

    print("Affected areas:", updated_plan["affected_areas"])
    print("Calls used this update:", updated_plan["calls_used"])
    print("Duration (s):", round(updated_plan["duration_seconds"], 2))
    print()
    print("Predictions:")
    for p in updated_plan["predictions"]:
        print(" -", p)
    print()
    print("Updated committed items:")
    for item in updated_plan["budget"].committed_items:
        print("  -", item)
    print(
        "Total committed:", updated_plan["budget"].total_committed,
        "| remaining:", updated_plan["budget"].remaining,
    )
    print()
    print("New decisions from this update:")
    for d in updated_plan["decisions"][len(plan["decisions"]):]:
        fact_desc = d.get("fact", {}).get("fact") if d.get("fact") else None
        print(f"  [{d['accepted']}] ({d.get('conflict_type')}) {d['sender']}: {fact_desc} -> {d['reason']}")
    print()
    print("Validation checks after update:")
    for check in updated_plan["validation"]:
        print(f"  [{'PASS' if check.passed else 'FAIL'}] {check.name}: {check.details}")


if __name__ == "__main__":
    main()
