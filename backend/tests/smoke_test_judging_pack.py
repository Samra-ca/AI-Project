"""Manual smoke test: python backend/tests/smoke_test_judging_pack.py

Runs the full orchestrator against a genuinely unseen message pack
(different format, different numbers, new constraint types: venue
accessibility, venue withdrawal, an irrelevant message) to check
robustness beyond the known sample pack.
"""

import json
import os
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

load_dotenv()

from engine.orchestrator import run_plan  # noqa: E402
from services.message_service import read_message_file  # noqa: E402
from services.model_service import create_model_service  # noqa: E402

PACK_PATH = "C:/Users/COMPUTER ARENA/Desktop/judging_pack.txt"


def main() -> None:
    model = create_model_service()
    print("Provider:", model._provider, "| Model:", model._model_name)

    messages = read_message_file(PACK_PATH)
    print("Parsed messages:", len(messages))

    plan = run_plan(
        model,
        messages,
        student_count=150,
        staff_count=10,
        team_count=50,
        approved_budget=650000,
    )

    print()
    print("Required capacity:", plan["required_capacity"])
    print("Venue:", plan["venue"].selected, "|", plan["venue"].reason)
    for option, reason in plan["venue"].rejected:
        print("  rejected:", option, "-", reason)
    print()
    print("Food:", plan["food"].selected, "| total:", plan["food"].total_cost)
    print()
    print("Judging:", plan["judging"])
    print()
    print("Budget committed:")
    for item in plan["budget"].committed_items:
        print("  -", item)
    print("Pending:")
    for item in plan["budget"].pending_items:
        print("  -", item)
    print(
        "Total committed:", plan["budget"].total_committed,
        "| approved:", plan["budget"].approved_budget,
        "| remaining:", plan["budget"].remaining,
    )
    print()
    print("Validation:")
    for check in plan["validation"]:
        print(f"  [{'PASS' if check.passed else 'FAIL'}] {check.name}: {check.details}")
    print()
    print("All decisions:")
    for d in plan["decisions"]:
        fact_desc = d.get("fact", {}).get("fact") if d.get("fact") else None
        print(f"  [{d['accepted']}] {d['sender']}: {fact_desc} -> {d['reason']}")
    print()
    print("Trace summary:", plan["trace_summary"])

    with open("judging_pack_result.json", "w", encoding="utf-8") as f:
        json.dump({"note": "see console output"}, f)


if __name__ == "__main__":
    main()
