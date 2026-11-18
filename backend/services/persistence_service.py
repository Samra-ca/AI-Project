"""Persists a computed plan - messages, extracted facts, decisions, model
trace, and the versioned plan itself - into PostgreSQL. Never overwrites an
original message; only its status is updated, and every plan version is
kept (only the latest is marked current).
"""

from sqlalchemy.orm import Session

from database import models
from services.export_service import plan_to_dict
from services.message_service import RawMessage


def _get_or_create_message(db: Session, msg: RawMessage) -> models.Message:
    existing = (
        db.query(models.Message)
        .filter(models.Message.fingerprint == msg.fingerprint)
        .one_or_none()
    )
    if existing:
        return existing
    record = models.Message(
        sender=msg.sender,
        date_text=msg.date,
        raw_text=msg.text,
        fingerprint=msg.fingerprint,
        status="pending",
    )
    db.add(record)
    db.flush()
    return record


def persist_plan(
    db: Session,
    plan: dict,
    processed_messages: list[RawMessage],
) -> models.Plan:
    message_by_fingerprint = {
        msg.fingerprint: _get_or_create_message(db, msg) for msg in processed_messages
    }

    for decision in plan["decisions"]:
        fact = decision.get("fact")
        status = "accepted" if decision["accepted"] else "rejected"

        message_record = None
        for msg in processed_messages:
            if msg.sender == decision.get("sender") and msg.text == decision.get("message"):
                message_record = message_by_fingerprint.get(msg.fingerprint)
                break

        if message_record is None:
            continue

        message_record.status = status
        db.add(
            models.Decision(
                message_id=message_record.id,
                area=(fact or {}).get("area", "unknown"),
                decision_text=(fact or {}).get("fact", decision.get("reason", "")),
                accepted=decision["accepted"],
                reason=decision["reason"],
            )
        )
        if fact:
            db.add(
                models.ExtractedFact(
                    message_id=message_record.id,
                    area=fact.get("area", "unknown"),
                    fact=fact.get("fact", ""),
                    quantity=fact.get("quantity"),
                    cost=fact.get("cost"),
                    date_text=fact.get("date"),
                    is_confirmed_decision=bool(fact.get("is_confirmed_decision", False)),
                    confidence=float(fact.get("confidence") or 0.0),
                )
            )

    for entry in plan["trace"]:
        db.add(
            models.ModelTraceRecord(
                call_number=entry.call_number,
                model_name=entry.model_name,
                area=entry.area,
                input_text=entry.input,
                output_text=entry.output,
                input_tokens=entry.input_tokens,
                output_tokens=entry.output_tokens,
                total_tokens=entry.total_tokens,
                duration_ms=entry.duration_ms,
                reason=entry.reason,
            )
        )

    db.query(models.Plan).update({models.Plan.is_current: False})

    previous_version = (
        db.query(models.Plan.version_number)
        .order_by(models.Plan.version_number.desc())
        .first()
    )
    next_version = (previous_version[0] + 1) if previous_version else 1

    plan_record = models.Plan(
        version_number=next_version,
        is_current=True,
        data_json=plan_to_dict(plan),
    )
    db.add(plan_record)
    db.flush()

    for check in plan["validation"]:
        db.add(
            models.ValidationResult(
                plan_id=plan_record.id,
                check_name=check.name,
                passed=check.passed,
                details=check.details,
            )
        )

    db.commit()
    return plan_record
