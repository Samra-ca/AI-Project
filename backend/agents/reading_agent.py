from services.model_service import ModelService

SYSTEM_PROMPT = """You read hackathon event-planning messages (English or Roman \
Urdu) and extract structured facts as compact JSON. Do not rely on specific \
sender names or hardcoded phrases - extract the actual intent and compare it \
conceptually against venue, schedule, food, judging, and budget planning.

Return a JSON object with exactly this shape:
{
  "facts": [
    {
      "area": "venue" | "schedule" | "food" | "judging" | "budget",
      "fact": "short description of the extracted fact",
      "quantity": number or null,
      "cost": number or null,
      "date": "ISO date/time or null",
      "is_confirmed_decision": true or false,
      "confidence": number between 0 and 1
    }
  ],
  "sender_authority_hint": "short note on whether the sender sounds authorized to approve this change, or null if unclear"
}

Only extract what is actually stated. Do not invent values."""


def extract_facts(model: ModelService, message_text: str, sender: str) -> dict:
    user_input = f"Sender: {sender}\nMessage: {message_text}"
    return model.call_json(
        area="reading",
        system_prompt=SYSTEM_PROMPT,
        user_input=user_input,
        reason="Extract structured facts from an incoming message",
    )
