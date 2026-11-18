"""Calculates total expenses and remaining budget against the approved cap
using pure Python arithmetic (area tag: "budget").
"""

from dataclasses import dataclass


@dataclass
class BudgetLineItem:
    category: str
    amount: float
    approved: bool


@dataclass
class BudgetSummary:
    approved_budget: float
    committed_items: list[BudgetLineItem]
    pending_items: list[BudgetLineItem]
    total_committed: float
    remaining: float
    within_budget: bool


def _to_line_item(fact: dict) -> BudgetLineItem | None:
    attrs = fact.get("attributes") or {}
    amount = fact.get("cost")
    if amount is None:
        return None
    category = attrs.get("category") or fact.get("fact", "Unnamed expense")
    approved = bool(fact.get("is_confirmed_decision", False))
    return BudgetLineItem(category=category, amount=float(amount), approved=approved)


def summarize_budget(
    budget_facts: list[dict],
    approved_budget: float,
    extra_committed: list[tuple[str, float]] | None = None,
) -> BudgetSummary:
    items = [i for i in (_to_line_item(f) for f in budget_facts) if i is not None]

    committed = [i for i in items if i.approved]
    pending = [i for i in items if not i.approved]

    for label, amount in extra_committed or []:
        committed.append(BudgetLineItem(category=label, amount=amount, approved=True))

    total_committed = sum(i.amount for i in committed)
    remaining = approved_budget - total_committed

    return BudgetSummary(
        approved_budget=approved_budget,
        committed_items=committed,
        pending_items=pending,
        total_committed=total_committed,
        remaining=remaining,
        within_budget=remaining >= 0,
    )
