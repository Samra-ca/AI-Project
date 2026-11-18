"""Selects a venue from extracted venue facts using pure Python arithmetic
(area tag: "venue"). Each fact is expected to carry attributes:
venue_name, capacity, has_generator (optional).
"""

from dataclasses import dataclass


@dataclass
class VenueOption:
    name: str
    capacity: int
    cost: float
    has_generator: bool


@dataclass
class VenueDecision:
    selected: VenueOption | None
    reason: str
    rejected: list[tuple[VenueOption, str]]


def _to_option(fact: dict) -> VenueOption | None:
    attrs = fact.get("attributes") or {}
    capacity = attrs.get("capacity")
    cost = fact.get("cost")
    if capacity is None or cost is None:
        return None
    return VenueOption(
        name=attrs.get("venue_name") or fact.get("fact", "Unnamed venue"),
        capacity=int(capacity),
        cost=float(cost),
        has_generator=bool(attrs.get("has_generator", False)),
    )


def _latest_per_venue(venue_facts: list[dict]) -> list[VenueOption]:
    """Facts are appended in chronological message order, so a later quote
    for the same venue name (e.g. a price update) replaces an earlier one
    rather than both being treated as separate options."""
    by_name: dict[str, VenueOption] = {}
    for fact in venue_facts:
        option = _to_option(fact)
        if option is None:
            continue
        by_name[option.name.lower().strip()] = option
    return list(by_name.values())


def select_venue(venue_facts: list[dict], required_capacity: int) -> VenueDecision:
    options = _latest_per_venue(venue_facts)

    feasible: list[VenueOption] = []
    rejected: list[tuple[VenueOption, str]] = []
    for option in options:
        if option.capacity < required_capacity:
            rejected.append(
                (
                    option,
                    f"Capacity {option.capacity} is below the required "
                    f"{required_capacity}.",
                )
            )
        else:
            feasible.append(option)

    if not feasible:
        return VenueDecision(
            selected=None,
            reason=f"No venue option meets the required capacity of {required_capacity}.",
            rejected=rejected,
        )

    feasible.sort(key=lambda o: o.cost)
    cheapest = feasible[0]

    generator_options = sorted(
        (o for o in feasible if o.has_generator), key=lambda o: o.cost
    )

    if generator_options and generator_options[0] is not cheapest:
        selected = generator_options[0]
        reason = (
            f"{selected.name} (Rs. {selected.cost:,.0f}) accommodates the "
            f"required {required_capacity} and has a standby generator. "
            f"{cheapest.name} is cheaper at Rs. {cheapest.cost:,.0f} but has "
            f"no generator; the generator is chosen as a risk-based "
            f"decision, not because it is the only feasible option."
        )
        for option in feasible:
            if option is not selected:
                rejected.append((option, "Feasible but not selected."))
    else:
        selected = cheapest
        reason = (
            f"{selected.name} (Rs. {selected.cost:,.0f}) is the cheapest "
            f"option that meets the required capacity of {required_capacity}."
        )
        for option in feasible:
            if option is not selected:
                rejected.append((option, "Feasible but not selected."))

    return VenueDecision(selected=selected, reason=reason, rejected=rejected)
