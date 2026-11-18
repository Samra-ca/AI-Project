"""Single entry point: python run.py

Reads data/messages.txt, runs the planning engine (initial run or
incremental update), validates the plan, saves it to PostgreSQL, and
exports outputs/final_plan.json + outputs/execution_trace.json.
"""


def main() -> None:
    raise NotImplementedError


if __name__ == "__main__":
    main()
