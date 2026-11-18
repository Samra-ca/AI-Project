"""Calculates judge requirements, capacity, honorarium, and late-arrival
reassignment notes from extracted judging facts (area tag: "judging").
"""

import math
from dataclasses import dataclass, field


@dataclass
class JudgingPlan:
    teams: int
    confirmed_judges: int
    minutes_per_team: int
    max_teams_per_judge: int
    min_required_judges: int
    capacity_teams: int
    is_sufficient: bool
    honorarium_total: float
    reassignment_notes: list[str] = field(default_factory=list)


def _first_attr(facts: list[dict], key: str):
    for f in facts:
        attrs = f.get("attributes") or {}
        if attrs.get(key) is not None:
            return attrs[key]
    return None


def plan_judging(
    judging_facts: list[dict],
    team_count: int,
    default_minutes_per_team: int = 15,
    default_max_teams_per_judge: int = 3,
) -> JudgingPlan:
    confirmed_judges = int(_first_attr(judging_facts, "judges_confirmed") or 0)
    minutes_per_team = int(
        _first_attr(judging_facts, "minutes_per_team") or default_minutes_per_team
    )
    max_teams_per_judge = int(
        _first_attr(judging_facts, "max_teams_per_judge")
        or default_max_teams_per_judge
    )
    honorarium_per_judge = float(_first_attr(judging_facts, "honorarium_per_judge") or 0)

    min_required_judges = (
        math.ceil(team_count / max_teams_per_judge) if max_teams_per_judge else team_count
    )
    capacity_teams = confirmed_judges * max_teams_per_judge
    is_sufficient = capacity_teams >= team_count

    notes = []
    for fact in judging_facts:
        late = (fact.get("attributes") or {}).get("late_minutes")
        if late:
            notes.append(
                f"A judge may be {int(late)} minutes late; reassign their "
                f"earliest teams to another judge within the "
                f"{max_teams_per_judge}-team cap rather than rejecting their "
                f"participation."
            )

    return JudgingPlan(
        teams=team_count,
        confirmed_judges=confirmed_judges,
        minutes_per_team=minutes_per_team,
        max_teams_per_judge=max_teams_per_judge,
        min_required_judges=min_required_judges,
        capacity_teams=capacity_teams,
        is_sufficient=is_sufficient,
        honorarium_total=confirmed_judges * honorarium_per_judge,
        reassignment_notes=notes,
    )
