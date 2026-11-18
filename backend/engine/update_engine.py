"""Incremental updates: skip already-seen messages, predict affected areas,
extract facts for only the new messages, apply conflict-checked changes
(including budget line-item supersession), and recompute only what changed
- enforcing the 5-model-call / 1-minute update limits.
"""

import time

from agents import budget_agent
from agents.reading_agent import extract_facts
from engine import conflict_detector, dependency_engine, validation_engine
from services.message_service import RawMessage, diff_new_messages
from services.model_service import ModelService

MAX_UPDATE_CALLS = 5
MAX_UPDATE_SECONDS = 60


def _match_existing_category(category: str, items: list) -> int | None:
    """Index of an existing committed item whose category matches
    (case-insensitively) the given category, if any - used to detect that a
    new fact corrects/supersedes an existing line item rather than adding a
    new one."""
    category_lower = category.lower().strip()
    for i, item in enumerate(items):
        existing_lower = item.category.lower().strip()
        if existing_lower in category_lower or category_lower in existing_lower:
            return i
    return None


def run_update(
    previous_plan: dict,
    new_messages: list[RawMessage],
    known_fingerprints: set[str],
    model: ModelService,
    required_capacity: int,
    approved_budget: float,
) -> dict:
    start = time.perf_counter()
    truly_new = diff_new_messages(new_messages, known_fingerprints)

    calls_before = len(model.trace)
    decisions: list[dict] = []
    predictions: list[dict] = []
    affected_areas: set[str] = set()

    committed_items = list(previous_plan["budget"].committed_items)
    pending_items = list(previous_plan["budget"].pending_items)
    committed_total = previous_plan["budget"].total_committed
    food_required_headcount = required_capacity

    for msg in truly_new:
        if len(model.trace) - calls_before >= MAX_UPDATE_CALLS:
            decisions.append(
                {
                    "sender": msg.sender,
                    "date": msg.date,
                    "message": msg.text,
                    "accepted": False,
                    "reason": "Update call limit (5) reached; message deferred to the next run.",
                    "conflict_type": "call_limit",
                }
            )
            continue

        predicted_areas = dependency_engine.predict_affected_areas(msg.text)
        calls_before_message = len(model.trace)

        extraction = extract_facts(model, msg.text, sender=msg.sender)
        facts = extraction.get("facts", [])
        actual_areas = sorted({f.get("area") for f in facts if f.get("area")})

        predictions.append(
            {
                "sender": msg.sender,
                "predicted_areas": predicted_areas,
                "actual_areas": actual_areas,
                "calls_used": len(model.trace) - calls_before_message,
                "prediction_correct": bool(set(predicted_areas) & set(actual_areas)),
            }
        )

        for fact in facts:
            area = fact.get("area")
            affected_areas.add(area)
            attrs = fact.get("attributes") or {}

            if area == "food" and attrs.get("headcount"):
                food_required_headcount = int(attrs["headcount"])

            superseded_index = None
            if area == "budget" and fact.get("cost") is not None:
                category = attrs.get("category") or fact.get("fact", "")
                superseded_index = _match_existing_category(category, committed_items)

            committed_so_far = committed_total
            if superseded_index is not None:
                committed_so_far -= committed_items[superseded_index].amount

            result = conflict_detector.evaluate_fact(
                fact,
                sender=msg.sender,
                approved_budget=approved_budget,
                committed_so_far=committed_so_far,
                required_headcount=(
                    food_required_headcount if area == "food" else None
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

            if (
                area == "budget"
                and fact.get("cost") is not None
                and not conflict_detector.is_budget_ceiling_statement(
                    fact, approved_budget
                )
            ):
                new_item = budget_agent.BudgetLineItem(
                    category=attrs.get("category") or fact.get("fact", "Unnamed expense"),
                    amount=float(fact["cost"]),
                    approved=True,
                )
                if superseded_index is not None:
                    committed_total -= committed_items[superseded_index].amount
                    committed_items[superseded_index] = new_item
                else:
                    committed_items.append(new_item)
                committed_total += new_item.amount

        if time.perf_counter() - start > MAX_UPDATE_SECONDS:
            decisions.append(
                {
                    "sender": "system",
                    "date": "",
                    "message": "",
                    "accepted": False,
                    "reason": "Update time limit (60s) reached; remaining messages deferred.",
                    "conflict_type": "time_limit",
                }
            )
            break

    remaining = approved_budget - committed_total
    budget_summary = budget_agent.BudgetSummary(
        approved_budget=approved_budget,
        committed_items=committed_items,
        pending_items=pending_items,
        total_committed=committed_total,
        remaining=remaining,
        within_budget=remaining >= 0,
    )

    updated_plan = dict(previous_plan)
    updated_plan["budget"] = budget_summary
    updated_plan["decisions"] = previous_plan["decisions"] + decisions
    updated_plan["validation"] = validation_engine.validate_plan(
        updated_plan["venue"],
        updated_plan["food"],
        updated_plan["judging"],
        budget_summary,
        updated_plan["schedule"],
        required_capacity,
    )
    updated_plan["affected_areas"] = sorted(affected_areas)
    updated_plan["predictions"] = predictions
    updated_plan["calls_used"] = len(model.trace) - calls_before
    updated_plan["duration_seconds"] = time.perf_counter() - start
    updated_plan["trace"] = model.trace
    updated_plan["trace_summary"] = model.summary()

    return updated_plan
