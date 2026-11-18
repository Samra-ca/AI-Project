"""Rule engine: runs the six final validation checks against the five
planning agents' outputs (capacity, arithmetic, timings, budget)."""

from dataclasses import dataclass

from agents.budget_agent import BudgetSummary
from agents.food_agent import FoodDecision
from agents.judging_agent import JudgingPlan
from agents.schedule_agent import SchedulePlan
from agents.venue_agent import VenueDecision


@dataclass
class ValidationCheck:
    name: str
    passed: bool
    details: str


def validate_plan(
    venue_decision: VenueDecision,
    food_decision: FoodDecision,
    judging_plan: JudgingPlan,
    budget_summary: BudgetSummary,
    schedule_plan: SchedulePlan,
    required_capacity: int,
) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = []

    computed_total = sum(i.amount for i in budget_summary.committed_items)
    checks.append(
        ValidationCheck(
            name="correct_figures",
            passed=abs(budget_summary.total_committed - computed_total) < 0.01,
            details="Budget total matches the sum of its committed line items.",
        )
    )

    checks.append(
        ValidationCheck(
            name="within_budget",
            passed=budget_summary.within_budget,
            details=(
                f"Committed Rs. {budget_summary.total_committed:,.0f} of "
                f"Rs. {budget_summary.approved_budget:,.0f} approved "
                f"(remaining Rs. {budget_summary.remaining:,.0f})."
            ),
        )
    )

    venue_ok = (
        venue_decision.selected is not None
        and venue_decision.selected.capacity >= required_capacity
    )
    checks.append(
        ValidationCheck(
            name="venue_fits",
            passed=venue_ok,
            details=(
                f"Selected venue capacity "
                f"{venue_decision.selected.capacity if venue_decision.selected else 'n/a'} "
                f"vs required {required_capacity}."
            ),
        )
    )

    checks.append(
        ValidationCheck(
            name="schedule_valid",
            passed=bool(schedule_plan.milestones),
            details=(
                f"{len(schedule_plan.warnings)} warning(s) flagged for review."
                if schedule_plan.warnings
                else "No scheduling conflicts."
            ),
        )
    )

    checks.append(
        ValidationCheck(
            name="enough_judges",
            passed=judging_plan.is_sufficient,
            details=(
                f"Capacity for {judging_plan.capacity_teams} teams vs "
                f"{judging_plan.teams} teams needed; minimum required judges "
                f"{judging_plan.min_required_judges}, confirmed "
                f"{judging_plan.confirmed_judges}."
            ),
        )
    )

    all_covered = all(
        [
            venue_decision.selected is not None,
            food_decision.selected is not None,
            judging_plan.confirmed_judges > 0,
            bool(budget_summary.committed_items) or bool(budget_summary.pending_items),
            bool(schedule_plan.milestones),
        ]
    )
    checks.append(
        ValidationCheck(
            name="all_five_areas_covered",
            passed=all_covered,
            details="venue, food, judging, budget, and schedule all produced output.",
        )
    )

    return checks
