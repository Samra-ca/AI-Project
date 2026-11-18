"""Checks authority, explicit approval, feasibility, and budget before a
newly extracted fact is accepted into the plan. Deliberately does not key
off specific sender names or hardcoded phrases - unseen messages must be
judged on role keywords and the fact's own content.
"""

from dataclasses import dataclass

_AUTHORIZED_ROLE_KEYWORDS = ["dean", "finance", "coordinator", "organizer"]
_AREA_VENDOR_KEYWORDS = {
    "venue": ["hall", "event"],
    "food": ["caterer"],
    "judging": ["judge"],
}


@dataclass
class ConflictResult:
    accepted: bool
    reason: str
    conflict_type: str | None = None


def _sender_is_likely_authorized(sender: str, area: str) -> bool:
    sender_lower = sender.lower()
    if any(keyword in sender_lower for keyword in _AUTHORIZED_ROLE_KEYWORDS):
        return True
    return any(keyword in sender_lower for keyword in _AREA_VENDOR_KEYWORDS.get(area, []))


def is_budget_ceiling_statement(fact: dict, approved_budget: float) -> bool:
    """A "budget" fact is the approved ceiling itself, not a committed
    expense, if the model flagged it as such or if its cost is large enough
    that it can only be the overall cap (no single genuine line item should
    equal or exceed the entire approved budget). The magnitude check is a
    deliberate fallback since the model's own flag isn't 100% consistent
    across runs.
    """
    if fact.get("area") != "budget":
        return False
    attrs = fact.get("attributes") or {}
    # Strict `is True` on purpose: the model has been observed to set this
    # key to a cost figure instead of a boolean on ordinary line items,
    # which would wrongly exclude a real expense if checked for truthiness.
    if attrs.get("budget_all_in") is True:
        return True
    cost = fact.get("cost")
    return cost is not None and float(cost) >= approved_budget


def evaluate_fact(
    fact: dict,
    sender: str,
    approved_budget: float,
    committed_so_far: float,
    required_headcount: int | None = None,
) -> ConflictResult:
    """Price quotes and options (venue quotes, food package lists, judge
    confirmations) are not "decisions" by themselves - deciding among them is
    the specialist planning agents' job, so they pass straight through.
    Only new discretionary *spending requests* are gated on explicit
    confirmation and sender authority; everything else is gated on
    feasibility (e.g. insufficient food quantity) and budget overrun.
    """
    area = fact.get("area")
    attrs = fact.get("attributes") or {}
    cost = fact.get("cost")
    is_confirmed = bool(fact.get("is_confirmed_decision", False))

    if is_budget_ceiling_statement(fact, approved_budget):
        return ConflictResult(accepted=True, reason="Approved budget ceiling noted.")

    if area == "budget" and cost is not None:
        if not is_confirmed:
            return ConflictResult(
                accepted=False,
                reason=(
                    "Reads as a spending request, not a confirmed decision. "
                    "Logged but not auto-approved - an ordinary request "
                    "cannot silently become an approved expense."
                ),
                conflict_type="explicit_approval",
            )
        if not _sender_is_likely_authorized(sender, area):
            return ConflictResult(
                accepted=False,
                reason=(
                    f"Sender '{sender}' does not appear authorized to "
                    f"approve new spending."
                ),
                conflict_type="authority",
            )
        projected = committed_so_far + float(cost)
        if projected > approved_budget:
            return ConflictResult(
                accepted=False,
                reason=(
                    f"Accepting Rs. {float(cost):,.0f} would push committed "
                    f"spend to Rs. {projected:,.0f}, over the "
                    f"Rs. {approved_budget:,.0f} approved budget."
                ),
                conflict_type="budget",
            )

    if area == "food" and required_headcount is not None and is_confirmed:
        boxes = fact.get("quantity") or attrs.get("boxes") or attrs.get("order_quantity")
        if boxes is not None and float(boxes) < required_headcount:
            return ConflictResult(
                accepted=False,
                reason=(
                    f"{boxes:g} boxes is insufficient for the required "
                    f"headcount of {required_headcount}."
                ),
                conflict_type="feasibility",
            )

    return ConflictResult(accepted=True, reason="Accepted.")
