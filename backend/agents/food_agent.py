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
    service_charge_percent: float = 0.0


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
        service_charge_percent=float(attrs.get("service_charge_percent") or 0.0),
    )


def _latest_per_package(food_facts: list[dict]) -> list[FoodPackage]:
    """Facts are appended in chronological message order, so a later quote
    for the same package name (e.g. a price update) replaces an earlier one
    instead of both being treated as separate options - a stale quote must
    not win just because it happens to be cheaper. A service charge stated
    in the same message as the prices (not tied to one specific package
    name) is carried forward onto every package from that point on, since
    it's a caterer-wide surcharge rather than a per-package attribute.
    """
    by_name: dict[str, FoodPackage] = {}
    pending_service_charge = 0.0
    for fact in food_facts:
        attrs = fact.get("attributes") or {}
        if attrs.get("service_charge_percent"):
            pending_service_charge = float(attrs["service_charge_percent"])

        package = _to_package(fact)
        if package is None:
            continue
        if not package.service_charge_percent:
            package.service_charge_percent = pending_service_charge
        by_name[package.name.lower().strip()] = package
    return list(by_name.values())


def select_food_package(food_facts: list[dict], headcount: int) -> FoodDecision:
    packages = _latest_per_package(food_facts)

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
    subtotal = selected.price_per_person * headcount + selected.delivery_charge
    total_cost = subtotal * (1 + selected.service_charge_percent / 100)

    rejected = [
        (p, "More expensive per head; cheapest sufficient package preferred.")
        for p in packages
        if p is not selected
    ]

    reason = (
        f"{selected.name} at Rs. {selected.price_per_person:,.0f}/head is the "
        f"cheapest available package for {headcount} people, preserving budget "
        f"(total Rs. {total_cost:,.0f}"
    )
    if selected.service_charge_percent:
        reason += f", including a {selected.service_charge_percent:g}% service charge"
    reason += ")."

    return FoodDecision(
        selected=selected,
        headcount=headcount,
        total_cost=total_cost,
        reason=reason,
        rejected=rejected,
    )
