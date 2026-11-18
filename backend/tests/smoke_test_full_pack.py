"""Manual smoke test: python backend/tests/smoke_test_full_pack.py

Runs the reading agent against all 8 real sample messages to validate
extraction quality before building the deterministic planning agents.
"""

import json
import os
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

load_dotenv()

from agents.reading_agent import extract_facts  # noqa: E402
from services.message_service import read_message_file  # noqa: E402
from services.model_service import ModelService  # noqa: E402


def main() -> None:
    model = ModelService(
        api_key=os.environ["GROQ_API_KEY"],
        model_name=os.environ.get("MODEL_NAME", "openai/gpt-oss-20b"),
    )
    messages = read_message_file(
        os.path.join(os.path.dirname(__file__), "..", "..", "data", "messages.txt")
    )
    for i, msg in enumerate(messages, start=1):
        result = extract_facts(model, msg.text, sender=msg.sender)
        print(f"--- Message {i} ({msg.sender}) ---")
        print(json.dumps(result, indent=2))
        print()

    print("Summary:", model.summary())


if __name__ == "__main__":
    main()
