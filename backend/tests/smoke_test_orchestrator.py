"""Manual smoke test: python backend/tests/smoke_test_orchestrator.py

Runs the full orchestrator against the real 8-message sample pack and
prints the resulting plan, checking it against the plan document's
expected sample-pack figures (Hall B, basic lunch, Rs. 524,000 total, etc).
"""

import os
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

load_dotenv()

from engine.orchestrator import run_plan  # noqa: E402
from services.message_service import read_message_file  # noqa: E402
from services.model_service import ModelService  # noqa: E402

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def main() -> None:
    model = ModelService(
        api_key=os.environ["GROQ_API_KEY"],
        model_name=os.environ.get("MODEL_NAME", "openai/gpt-oss-20b"),
    )
    messages = read_message_file(os.path.join(DATA_DIR, "messages.txt"))

    plan = run_plan(
        model,
        messages,
        student_count=150,
        staff_count=10,
        team_count=50,
        approved_budget=650000,
    )

    print("Required capacity:", plan["required_capacity"])
    print()
    print("Venue:", plan["venue"].selected, "|", plan["venue"].reason)
    for option, reason in plan["venue"].rejected:
        print("  rejected:", option, "-", reason)
    print()
    print("Food:", plan["food"].selected, "| total:", plan["food"].total_cost, "|", plan["food"].reason)
    print()
    print("Judging:", plan["judging"])
    print()
    print("Budget committed items:")
    for item in plan["budget"].committed_items:
        print("  -", item)
    print("Budget pending items:")
    for item in plan["budget"].pending_items:
        print("  -", item)
    print(
        "Total committed:", plan["budget"].total_committed,
        "| remaining:", plan["budget"].remaining,
        "| within budget:", plan["budget"].within_budget,
    )
    print()
    print("Schedule milestones:", plan["schedule"].milestones)
    print("Schedule warnings:", plan["schedule"].warnings)
    print()
    print("Validation checks:")
    for check in plan["validation"]:
        print(f"  [{'PASS' if check.passed else 'FAIL'}] {check.name}: {check.details}")
    print()
    print("Rejected/pending decisions:")
    for d in plan["decisions"]:
        if not d["accepted"]:
            print(f"  - ({d['conflict_type']}) {d['sender']}: {d['fact'].get('fact')} -> {d['reason']}")
    print()
    print("Trace summary:", plan["trace_summary"])


if __name__ == "__main__":
    main()
