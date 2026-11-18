"""Manual smoke test: python backend/tests/smoke_test_unseen_style.py

Runs the reading agent against invented messages with new senders and
phrasing never seen in the sample pack, to check extraction robustness
against the kind of unseen pack judges will actually use.
"""

import json
import os
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

load_dotenv()

from agents.reading_agent import extract_facts  # noqa: E402
from services.model_service import ModelService  # noqa: E402

UNSEEN_MESSAGES = [
    (
        "Logistics Head, email",
        "FYI the generator rental people say they can only guarantee power "
        "till 3pm, after that it's on them to swap cylinders.",
    ),
    (
        "Registrar, SMS",
        "aaj confirm ho gaya - sirf 140 students aa rahe hain, pehle 150 "
        "bataye the.",
    ),
    (
        "Volunteer Lead, WhatsApp",
        "Need 5 more water coolers for the hall, approx Rs 3000 each, "
        "waiting on Dean's approval before we order.",
    ),
    (
        "Anonymous tip",
        "heard the venue might double book us with another event that day",
    ),
]


def main() -> None:
    model = ModelService(
        api_key=os.environ["GROQ_API_KEY"],
        model_name=os.environ.get("MODEL_NAME", "openai/gpt-oss-20b"),
    )
    for sender, text in UNSEEN_MESSAGES:
        result = extract_facts(model, text, sender=sender)
        print(f"--- {sender}: {text[:60]}... ---")
        print(json.dumps(result, indent=2))
        print()


if __name__ == "__main__":
    main()
