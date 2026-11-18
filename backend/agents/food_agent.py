"""Calculates food quantities and costs from extracted food facts using pure
Python arithmetic (area tag: "food"). Each fact is expected to carry
attributes: package_name, price_per_person, delivery_free (optional),
delivery_charge (optional).
"""

from dataclasses import dataclass


@dataclass
class FoodPackage:
    name: str
    price_per_person: float
    delivery_charge: float


@dataclass
class FoodDecision:
    selected: FoodPackage | None
    headcount: int
    total_cost: float
    reason: str
    rejected: list[tuple[FoodPackage, str]]


def _to_package(fact: dict) -> FoodPackage | None:
    attrs = fact.get("attributes") or {}
    price = attrs.get("price_per_person", fact.get("cost"))
    if price is None:
        return None
    delivery_charge = 0.0 if attrs.get("delivery_free", True) else float(
        attrs.get("delivery_charge", 0.0)
    )
    return FoodPackage(
        name=attrs.get("package_name") or fact.get("fact", "Unnamed package"),
        price_per_person=float(price),
        delivery_charge=delivery_charge,
    )


def select_food_package(food_facts: list[dict], headcount: int) -> FoodDecision:
    packages = [p for p in (_to_package(f) for f in food_facts) if p is not None]

    if not packages:
        return FoodDecision(
            selected=None,
            headcount=headcount,
            total_cost=0.0,
            reason="No food package information available.",
            rejected=[],
        )

    packages.sort(key=lambda p: p.price_per_person)
    selected = packages[0]
    total_cost = selected.price_per_person * headcount + selected.delivery_charge

    rejected = [
        (p, "More expensive per head; cheapest sufficient package preferred.")
        for p in packages
        if p is not selected
    ]

    reason = (
        f"{selected.name} at Rs. {selected.price_per_person:,.0f}/head is the "
        f"cheapest available package for {headcount} people, preserving budget "
        f"(total Rs. {total_cost:,.0f})."
    )

    return FoodDecision(
        selected=selected,
        headcount=headcount,
        total_cost=total_cost,
        reason=reason,
        rejected=rejected,
    )
