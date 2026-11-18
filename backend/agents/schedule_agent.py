"""Builds the event timetable: fixed milestones, prayer break, and a
duration-consistency flag (area tag: "schedule").

The milestones below come from the organizers' brief, not from the message
pack, so they are passed in as a fixed default rather than extracted.
"""

from dataclasses import dataclass, field

FIXED_MILESTONES: list[tuple[str, str]] = [
    ("10:00 AM", "Build starts"),
    ("1:25 PM", "Code freeze and final push"),
    ("1:30 PM", "Whole-room test run"),
    ("2:30 PM - 4:30 PM", "Judges visit tables"),
]

MILESTONE_SPAN_MINUTES = 390  # 10:00 AM to 4:30 PM


@dataclass
class SchedulePlan:
    milestones: list[tuple[str, str]]
    prayer_break_minutes: int | None
    stated_duration_minutes: int | None
    warnings: list[str] = field(default_factory=list)


def _first_attr(facts: list[dict], key: str):
    for f in facts:
        attrs = f.get("attributes") or {}
        if attrs.get(key) is not None:
            return attrs[key]
    return None


def build_schedule(
    schedule_facts: list[dict],
    fixed_milestones: list[tuple[str, str]] | None = None,
) -> SchedulePlan:
    milestones = list(fixed_milestones or FIXED_MILESTONES)
    prayer_break = _first_attr(schedule_facts, "prayer_break_minutes")
    stated_duration = _first_attr(schedule_facts, "duration_minutes")

    if prayer_break:
        milestones.append((None, f"{int(prayer_break)}-minute prayer break"))

    warnings = []
    if stated_duration and int(stated_duration) != MILESTONE_SPAN_MINUTES:
        stated_hours = int(stated_duration) // 60
        span_hours, span_minutes = divmod(MILESTONE_SPAN_MINUTES, 60)
        warnings.append(
            f"The brief calls this a {stated_hours}-hour hackathon, but the "
            f"published milestones (10:00 AM - 4:30 PM) span {span_hours} "
            f"hours {span_minutes} minutes. Preserving the explicit "
            f"milestones and flagging this inconsistency for clarification "
            f"rather than inventing a new timetable."
        )

    return SchedulePlan(
        milestones=milestones,
        prayer_break_minutes=int(prayer_break) if prayer_break else None,
        stated_duration_minutes=int(stated_duration) if stated_duration else None,
        warnings=warnings,
    )
