"""Manual test: python backend/tests/test_agents_synthetic.py

Pure unit tests against hand-built fact dicts (no model calls) covering
scenarios the real sample pack doesn't happen to exercise: a stale price
quote being superseded by a newer one, a venue set where nothing fits,
and a budget-exceeding request being rejected.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.food_agent import select_food_package  # noqa: E402
from agents.venue_agent import select_venue  # noqa: E402
from engine.conflict_detector import evaluate_fact  # noqa: E402

failures = 0


def check(label: str, condition: bool) -> None:
    global failures
    status = "PASS" if condition else "FAIL"
    if not condition:
        failures += 1
    print(f"[{status}] {label}")


# --- Stale food quote must be superseded by a newer, more expensive one ---
stale_food_facts = [
    {
        "area": "food",
        "cost": 1000,
        "is_confirmed_decision": True,
        "attributes": {"package_name": "Standard lunch", "price_per_person": 1000},
    },
    {
        "area": "food",
        "cost": 1200,
        "is_confirmed_decision": True,
        "attributes": {"package_name": "Standard lunch", "price_per_person": 1200},
    },
]
food_decision = select_food_package(stale_food_facts, headcount=100)
check(
    "Stale food quote (Rs.1000) is superseded by newer Rs.1200, not picked for being cheaper",
    food_decision.selected is not None and food_decision.selected.price_per_person == 1200,
)

# --- Stale venue quote must be superseded the same way ---
stale_venue_facts = [
    {
        "area": "venue",
        "cost": 100000,
        "attributes": {"venue_name": "Hall Z", "capacity": 200, "has_generator": False},
    },
    {
        "area": "venue",
        "cost": 130000,
        "attributes": {"venue_name": "Hall Z", "capacity": 200, "has_generator": False},
    },
]
venue_decision = select_venue(stale_venue_facts, required_capacity=180)
check(
    "Stale venue quote (Rs.100,000) is superseded by newer Rs.130,000",
    venue_decision.selected is not None and venue_decision.selected.cost == 130000,
)

# --- No venue meets required capacity ---
too_small_facts = [
    {"area": "venue", "cost": 40000, "attributes": {"venue_name": "Room D", "capacity": 80}},
    {"area": "venue", "cost": 90000, "attributes": {"venue_name": "Room E", "capacity": 100}},
]
too_small_decision = select_venue(too_small_facts, required_capacity=180)
check(
    "No venue meets required capacity -> selected is None, all rejected",
    too_small_decision.selected is None and len(too_small_decision.rejected) == 2,
)

# --- Budget-exceeding confirmed request is rejected ---
over_budget_fact = {
    "area": "budget",
    "cost": 200000,
    "is_confirmed_decision": True,
    "attributes": {"category": "stage decor"},
}
result = evaluate_fact(
    over_budget_fact,
    sender="Finance, email",
    approved_budget=650000,
    committed_so_far=500000,
)
check(
    "Confirmed budget request that would exceed the approved cap is rejected",
    not result.accepted and result.conflict_type == "budget",
)

# --- Unauthorized sender cannot approve new spending ---
unauthorized_fact = {
    "area": "budget",
    "cost": 50000,
    "is_confirmed_decision": True,
    "attributes": {"category": "DJ"},
}
result2 = evaluate_fact(
    unauthorized_fact,
    sender="Random student, WhatsApp",
    approved_budget=650000,
    committed_so_far=0,
)
check(
    "Unauthorized sender confirming new spending is rejected on authority",
    not result2.accepted and result2.conflict_type == "authority",
)

print()
if failures:
    print(f"{failures} check(s) FAILED")
    sys.exit(1)
print("All checks passed.")
