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
      "attributes": { ... }
    }
  ],
  "sender_authority_hint": "short note on whether the sender sounds authorized to approve this change, or null if unclear"
}

"is_confirmed_decision" means: does the sender state this as a settled fact
or number, including a correction to an earlier figure ("the bill came in
at Rs X", "it's now Rs Y", "confirmed: X")? Then true. Is it instead a
request, suggestion, question, or something explicitly awaiting someone
else's approval ("can we get X", "I'd like to request Y")? Then false. A
correction or update to a previous number is still a confirmed decision,
not a request, as long as the sender states it rather than asking for it.

The "attributes" object holds extra named values when they apply to this
fact's area. You MUST use these exact key names verbatim - never rename,
abbreviate, or invent a synonym for them:
- venue: venue_name, capacity, has_generator, has_ramp_access (true/false,
  only when step-free/ramp/ground-floor access is explicitly mentioned for
  that venue), is_unavailable (set true ONLY when a message says a
  previously offered venue can no longer be booked, is withdrawn, under
  maintenance, double-booked, etc. - omit entirely otherwise),
  requires_accessibility (set true on its own fact, not tied to a specific
  venue, when a message states that step-free/wheelchair access is a
  requirement for the event). Always include venue_name whenever a
  specific venue is named, even in a price update, correction, or
  withdrawal that doesn't re-describe the whole venue.
- food: package_name, price_per_person, delivery_free, headcount,
  service_charge_percent (always include package_name whenever a specific
  food package is named, even in a price update that doesn't re-describe
  the whole package)
- judging: judges_confirmed, honorarium_per_judge, minutes_per_team,
  max_teams_per_judge, late_minutes
- budget: category, budget_all_in (boolean true/false only - set it to
  true ONLY on the single fact that states the event's overall approved
  budget ceiling, e.g. "the budget is Rs X, all in" - never on an
  individual expense line item, even one that is itself "all inclusive"),
  staff_on_duty
- schedule: prayer_break_minutes, duration_minutes, start_time, end_time,
  headcount, team_size

Omit a key entirely (do not include it with null) when the message doesn't
mention it. Only extract what is actually stated - do not invent values.

If a message has no relevant planning content at all (pure noise, totally
unrelated to venue/schedule/food/judging/budget - for example an unrelated
building's hours), return an empty "facts" array rather than forcing it
into one of the five areas."""


def extract_facts(model: ModelService, message_text: str, sender: str) -> dict:
    user_input = f"Sender: {sender}\nMessage: {message_text}"
    return model.call_json(
        area="reading",
        system_prompt=SYSTEM_PROMPT,
        user_input=user_input,
        reason="Extract structured facts from an incoming message",
    )
