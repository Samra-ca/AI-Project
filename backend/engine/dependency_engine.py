"""Predicts which planning areas a new message will affect, before calling
the model, using lightweight keyword matching (no model call spent on the
prediction itself). Feeds the change-prediction panel: predicted vs actual
affected areas, and whether the prediction was correct.
"""

_AREA_KEYWORDS = {
    "venue": ["hall", "room", "venue", "generator", "seat"],
    "schedule": [
        "break", "schedule", "timetable", "freeze", "am", "pm", "prayer", "hour",
    ],
    "food": [
        "lunch", "food", "caterer", "box", "boxes", "meal", "delivery",
        "catering", "headcount", "feed",
    ],
    "judging": ["judge", "judging", "team", "honorarium", "score"],
    "budget": ["budget", "rs", "rupee", "cost", "price", "bill", "quote", "fund"],
}


def predict_affected_areas(message_text: str) -> list[str]:
    text_lower = message_text.lower()
    predicted = [
        area
        for area, keywords in _AREA_KEYWORDS.items()
        if any(keyword in text_lower for keyword in keywords)
    ]
    return predicted or ["unknown"]
