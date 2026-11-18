from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


def _now() -> datetime:
    return datetime.now(UTC)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    location: Mapped[str]
    student_count: Mapped[int]
    team_count: Mapped[int]
    team_size: Mapped[int]
    staff_count: Mapped[int]
    approved_budget: Mapped[float]
    created_at: Mapped[datetime] = mapped_column(default=_now)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    sender: Mapped[str]
    date_text: Mapped[str]
    raw_text: Mapped[str]
    fingerprint: Mapped[str] = mapped_column(unique=True, index=True)
    status: Mapped[str] = mapped_column(default="pending")
    created_at: Mapped[datetime] = mapped_column(default=_now)

    extracted_facts: Mapped[list["ExtractedFact"]] = relationship(
        back_populates="message"
    )
    decisions: Mapped[list["Decision"]] = relationship(back_populates="message")


class ExtractedFact(Base):
    __tablename__ = "extracted_facts"

    id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"))
    area: Mapped[str]
    fact: Mapped[str]
    quantity: Mapped[Optional[float]]
    cost: Mapped[Optional[float]]
    date_text: Mapped[Optional[str]]
    is_confirmed_decision: Mapped[bool] = mapped_column(default=False)
    confidence: Mapped[float] = mapped_column(default=0.0)
    created_at: Mapped[datetime] = mapped_column(default=_now)

    message: Mapped["Message"] = relationship(back_populates="extracted_facts")


class Constraint(Base):
    __tablename__ = "constraints"

    id: Mapped[int] = mapped_column(primary_key=True)
    area: Mapped[str]
    description: Mapped[str]
    value_json: Mapped[dict] = mapped_column(JSON, default=dict)
    is_mandatory: Mapped[bool] = mapped_column(default=True)
    source_message_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("messages.id")
    )
    superseded_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("constraints.id")
    )
    created_at: Mapped[datetime] = mapped_column(default=_now)


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"))
    area: Mapped[str]
    decision_text: Mapped[str]
    accepted: Mapped[bool]
    reason: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=_now)

    message: Mapped["Message"] = relationship(back_populates="decisions")


class Venue(Base):
    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    capacity: Mapped[int]
    cost: Mapped[float]
    has_generator: Mapped[bool] = mapped_column(default=False)
    selected: Mapped[bool] = mapped_column(default=False)
    rejection_reason: Mapped[Optional[str]]
    source_message_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("messages.id")
    )


class ScheduleItem(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True)
    activity: Mapped[str]
    start_time: Mapped[Optional[str]]
    end_time: Mapped[Optional[str]]
    notes: Mapped[Optional[str]]


class FoodPlan(Base):
    __tablename__ = "food_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    package_name: Mapped[str]
    price_per_person: Mapped[float]
    headcount: Mapped[int]
    delivery_charge: Mapped[float] = mapped_column(default=0.0)
    total_cost: Mapped[float]
    selected: Mapped[bool] = mapped_column(default=False)


class Judge(Base):
    __tablename__ = "judges"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    confirmed: Mapped[bool] = mapped_column(default=True)
    late_minutes: Mapped[int] = mapped_column(default=0)
    honorarium: Mapped[float] = mapped_column(default=0.0)

    assignments: Mapped[list["JudgeAssignment"]] = relationship(
        back_populates="judge"
    )


class JudgeAssignment(Base):
    __tablename__ = "judge_assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    judge_id: Mapped[int] = mapped_column(ForeignKey("judges.id"))
    team_identifier: Mapped[str]
    minutes_per_team: Mapped[int] = mapped_column(default=15)

    judge: Mapped["Judge"] = relationship(back_populates="assignments")


class BudgetItem(Base):
    __tablename__ = "budget_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str]
    description: Mapped[str]
    amount: Mapped[float]
    is_approved: Mapped[bool] = mapped_column(default=True)
    source_message_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("messages.id")
    )


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    version_number: Mapped[int]
    is_current: Mapped[bool] = mapped_column(default=False)
    data_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=_now)

    validation_results: Mapped[list["ValidationResult"]] = relationship(
        back_populates="plan"
    )


class ModelTraceRecord(Base):
    __tablename__ = "model_traces"

    id: Mapped[int] = mapped_column(primary_key=True)
    call_number: Mapped[int]
    model_name: Mapped[str]
    area: Mapped[str]
    input_text: Mapped[str]
    output_text: Mapped[str]
    input_tokens: Mapped[int]
    output_tokens: Mapped[int]
    total_tokens: Mapped[int]
    duration_ms: Mapped[int]
    reason: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=_now)


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"))
    check_name: Mapped[str]
    passed: Mapped[bool]
    details: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(default=_now)

    plan: Mapped["Plan"] = relationship(back_populates="validation_results")
