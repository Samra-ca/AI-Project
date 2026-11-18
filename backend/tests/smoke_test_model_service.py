"""Manual smoke test: python backend/tests/smoke_test_model_service.py

Verifies Groq API access, response speed, and real token-usage reporting
by running one reading-agent extraction on a sample message.
"""

import os
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

load_dotenv()

from agents.reading_agent import extract_facts  # noqa: E402
from services.model_service import ModelService  # noqa: E402

SAMPLE_MESSAGE = (
    "Updated standard lunch price is now Rs. 1,200 per person, delivery is free."
)


def main() -> None:
    model = ModelService(
        api_key=os.environ["GROQ_API_KEY"],
        model_name=os.environ.get("MODEL_NAME", "llama-3.1-8b-instant"),
    )
    result = extract_facts(model, SAMPLE_MESSAGE, sender="Catering Vendor")
    print("Extracted facts:", result)
    print("Trace entry:", model.trace[0])
    print("Summary:", model.summary())


if __name__ == "__main__":
    main()
