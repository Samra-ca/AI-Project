"""Single orchestrator coordinating the five specialist planning modules.

Reads every message, extracts facts via the reading agent, runs each fact
through the conflict detector, groups accepted facts by area, and hands
each area to its specialist agent for pure-Python calculation.
"""

from agents import budget_agent, food_agent, judging_agent, schedule_agent, venue_agent
from agents.reading_agent import extract_facts
from engine import conflict_detector, validation_engine
from services.message_service import RawMessage
from services.model_service import ModelService

PLANNING_AREAS = ("venue", "schedule", "food", "judging", "budget")


def run_plan(
    model: ModelService,
    messages: list[RawMessage],
    student_count: int,
    staff_count: int,
    team_count: int,
    approved_budget: float,
) -> dict:
    per_message_facts: list[tuple[RawMessage, list[dict]]] = []
    for msg in messages:
        extraction = extract_facts(model, msg.text, sender=msg.sender)
        per_message_facts.append((msg, extraction.get("facts", [])))

    judges_confirmed = 0
    for _, facts in per_message_facts:
        for fact in facts:
            if fact.get("area") == "judging":
                value = (fact.get("attributes") or {}).get("judges_confirmed")
                if value:
                    judges_confirmed = max(judges_confirmed, int(value))

    required_capacity = student_count + staff_count + judges_confirmed

    decisions: list[dict] = []
    accepted_facts: list[dict] = []
    committed_budget_so_far = 0.0

    for msg, facts in per_message_facts:
        for fact in facts:
            result = conflict_detector.evaluate_fact(
                fact,
                sender=msg.sender,
                approved_budget=approved_budget,
                committed_so_far=committed_budget_so_far,
                required_headcount=(
                    required_capacity if fact.get("area") == "food" else None
                ),
            )
            decisions.append(
                {
                    "sender": msg.sender,
                    "date": msg.date,
                    "message": msg.text,
                    "fact": fact,
                    "accepted": result.accepted,
                    "reason": result.reason,
                    "conflict_type": result.conflict_type,
                }
            )
            if not result.accepted:
                continue
            accepted_facts.append(fact)
            if (
                fact.get("area") == "budget"
                and fact.get("cost") is not None
                and not conflict_detector.is_budget_ceiling_statement(
                    fact, approved_budget
                )
            ):
                committed_budget_so_far += float(fact["cost"])

    facts_by_area: dict[str, list[dict]] = {area: [] for area in PLANNING_AREAS}
    for fact in accepted_facts:
        area = fact.get("area")
        if area in facts_by_area:
            facts_by_area[area].append(fact)

    budget_facts = [
        f
        for f in facts_by_area["budget"]
        if not conflict_detector.is_budget_ceiling_statement(f, approved_budget)
    ]

    venue_decision = venue_agent.select_venue(facts_by_area["venue"], required_capacity)
    food_decision = food_agent.select_food_package(facts_by_area["food"], required_capacity)
    judging_plan = judging_agent.plan_judging(facts_by_area["judging"], team_count)
    schedule_plan = schedule_agent.build_schedule(facts_by_area["schedule"])

    extra_committed: list[tuple[str, float]] = []
    if venue_decision.selected:
        extra_committed.append(
            (f"Venue: {venue_decision.selected.name}", venue_decision.selected.cost)
        )
    if food_decision.selected:
        extra_committed.append(
            (f"Food: {food_decision.selected.name}", food_decision.total_cost)
        )
    if judging_plan.honorarium_total:
        extra_committed.append(("Judge honorarium", judging_plan.honorarium_total))

    budget_summary = budget_agent.summarize_budget(
        budget_facts, approved_budget, extra_committed=extra_committed
    )

    checks = validation_engine.validate_plan(
        venue_decision,
        food_decision,
        judging_plan,
        budget_summary,
        schedule_plan,
        required_capacity,
    )

    return {
        "required_capacity": required_capacity,
        "venue": venue_decision,
        "food": food_decision,
        "judging": judging_plan,
        "budget": budget_summary,
        "schedule": schedule_plan,
        "validation": checks,
        "decisions": decisions,
        "trace": model.trace,
        "trace_summary": model.summary(),
    }
