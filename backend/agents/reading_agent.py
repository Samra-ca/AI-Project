from services.model_service import ModelService

SYSTEM_PROMPT = """You read hackathon event-planning messages (English or Roman \
Urdu) and extract structured facts as compact JSON. Do not rely on specific \
sender names or hardcoded phrases - extract the actual intent and compare it \
conceptually against venue, schedule, food, judging, and budget planning.

A single message may describe several distinct options or items (for example \
four different venues, or two different food packages). Emit one fact object \
per distinct item, not one fact per message.

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
      "confidence": number between 0 and 1,
      "attributes": {
        "any additional named attributes relevant to this fact, e.g.":
        "venue_name, capacity, has_generator, package_name, price_per_person,
         delivery_free, headcount, judges_confirmed, honorarium_per_judge,
         minutes_per_team, max_teams_per_judge, late_minutes, category,
         start_time, end_time - include only the ones that actually apply"
      }
    }
  ],
  "sender_authority_hint": "short note on whether the sender sounds authorized to approve this change, or null if unclear"
}

Only extract what is actually stated. Do not invent values. Use null or omit
an attribute key when a message doesn't mention it."""


def extract_facts(model: ModelService, message_text: str, sender: str) -> dict:
    user_input = f"Sender: {sender}\nMessage: {message_text}"
    return model.call_json(
        area="reading",
        system_prompt=SYSTEM_PROMPT,
        user_input=user_input,
        reason="Extract structured facts from an incoming message",
    )
