"""Single entry point: python run.py

Reads data/messages.txt, runs the planning engine, applies any messages in
data/practice_updates.txt as an incremental update (if present), validates
the plan, saves it to PostgreSQL, and exports outputs/final_plan.json,
outputs/execution_trace.json, and outputs/report.json.
"""

import os
import sys

from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
DATA_DIR = os.path.join(ROOT_DIR, "data")
OUTPUTS_DIR = os.path.join(ROOT_DIR, "outputs")

sys.path.insert(0, BACKEND_DIR)
load_dotenv(os.path.join(ROOT_DIR, ".env"))

from database import models  # noqa: E402,F401
from database.connection import Base, SessionLocal, engine  # noqa: E402
from engine.orchestrator import run_plan  # noqa: E402
from engine.update_engine import run_update  # noqa: E402
from services.export_service import export_plan  # noqa: E402
from services.message_service import read_message_file  # noqa: E402
from services.model_service import ModelService  # noqa: E402
from services.persistence_service import persist_plan  # noqa: E402

EVENT = {
    "student_count": 150,
    "staff_count": 10,
    "team_count": 50,
    "approved_budget": 650000,
}


def main() -> None:
    Base.metadata.create_all(engine)
    db = SessionLocal()

    model = ModelService(
        api_key=os.environ["GROQ_API_KEY"],
        model_name=os.environ.get("MODEL_NAME", "openai/gpt-oss-20b"),
    )

    initial_messages = read_message_file(os.path.join(DATA_DIR, "messages.txt"))
    processed_messages = list(initial_messages)

    plan = run_plan(
        model,
        initial_messages,
        student_count=EVENT["student_count"],
        staff_count=EVENT["staff_count"],
        team_count=EVENT["team_count"],
        approved_budget=EVENT["approved_budget"],
    )

    updates_path = os.path.join(DATA_DIR, "practice_updates.txt")
    if os.path.exists(updates_path):
        update_messages = read_message_file(updates_path)
        known_fingerprints = {m.fingerprint for m in initial_messages}
        plan = run_update(
            plan,
            update_messages,
            known_fingerprints,
            model,
            required_capacity=plan["required_capacity"],
            approved_budget=EVENT["approved_budget"],
        )
        processed_messages += update_messages

    persist_plan(db, plan, processed_messages)
    export_plan(plan, OUTPUTS_DIR)

    print("Run complete.")
    print(f"Venue: {plan['venue'].selected}")
    print(f"Food: {plan['food'].selected} (total Rs. {plan['food'].total_cost:,.0f})")
    print(
        f"Budget: committed Rs. {plan['budget'].total_committed:,.0f}, "
        f"remaining Rs. {plan['budget'].remaining:,.0f}"
    )
    print("Validation:")
    for check in plan["validation"]:
        print(f"  [{'PASS' if check.passed else 'FAIL'}] {check.name}")
    print("Trace summary:", plan["trace_summary"])
    print(f"Outputs written to {OUTPUTS_DIR}")


if __name__ == "__main__":
    main()
