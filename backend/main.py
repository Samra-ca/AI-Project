import os
from collections.abc import Generator
from datetime import datetime, UTC

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from fastapi import Depends, FastAPI, HTTPException, UploadFile  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from pydantic import BaseModel  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from database import models  # noqa: E402
from database.connection import SessionLocal  # noqa: E402
from engine.orchestrator import run_plan  # noqa: E402
from engine.update_engine import run_update  # noqa: E402
from services.export_service import export_plan  # noqa: E402
from services.message_service import read_message_file  # noqa: E402
from services.model_service import create_model_service  # noqa: E402
from services.persistence_service import persist_plan  # noqa: E402

app = FastAPI(title="Mind2Machine Planning Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost:\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)

EVENT = {
    "student_count": 150,
    "staff_count": 10,
    "team_count": 50,
    "approved_budget": 650000,
}

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(ROOT_DIR, "data")
OUTPUTS_DIR = os.path.join(ROOT_DIR, "outputs")
BASE_PACK_PATH = os.path.join(DATA_DIR, "messages.txt")
PRACTICE_UPDATES_PATH = os.path.join(DATA_DIR, "practice_updates.txt")
INCOMING_PATH = os.path.join(DATA_DIR, "incoming_messages.txt")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _run_full_pipeline(db: Session) -> dict:
    """Recomputes the full plan from data/messages.txt, then applies any
    accumulated update messages (practice_updates.txt and/or
    incoming_messages.txt, whichever exist), persists, and exports.

    Each run recomputes from scratch rather than resuming from stored
    state - a known simplification (see TODO.md) that keeps this
    stateless and correct at the cost of re-spending model calls on
    already-seen messages on every trigger.
    """
    model = create_model_service()

    initial_messages = read_message_file(BASE_PACK_PATH)
    processed_messages = list(initial_messages)
    known_fingerprints = {m.fingerprint for m in initial_messages}

    plan = run_plan(
        model,
        initial_messages,
        student_count=EVENT["student_count"],
        staff_count=EVENT["staff_count"],
        team_count=EVENT["team_count"],
        approved_budget=EVENT["approved_budget"],
    )

    for update_path in (PRACTICE_UPDATES_PATH, INCOMING_PATH):
        if not os.path.exists(update_path):
            continue
        update_messages = read_message_file(update_path)
        if not update_messages:
            continue
        plan = run_update(
            plan,
            update_messages,
            known_fingerprints,
            model,
            required_capacity=plan["required_capacity"],
            approved_budget=EVENT["approved_budget"],
        )
        processed_messages += update_messages
        known_fingerprints |= {m.fingerprint for m in update_messages}

    persist_plan(db, plan, processed_messages)
    export_plan(plan, OUTPUTS_DIR)

    return {
        "processedMessages": len(processed_messages),
        "venue": plan["venue"].selected.name if plan["venue"].selected else None,
        "totalCommitted": plan["budget"].total_committed,
        "remaining": plan["budget"].remaining,
        "validationPassed": sum(1 for c in plan["validation"] if c.passed),
        "validationTotal": len(plan["validation"]),
        "callsUsed": plan["trace_summary"]["total_calls"],
    }


def _current_plan(db: Session) -> models.Plan:
    plan = (
        db.query(models.Plan)
        .filter(models.Plan.is_current.is_(True))
        .order_by(models.Plan.version_number.desc())
        .first()
    )
    if plan is None:
        raise HTTPException(status_code=404, detail="No plan has been run yet.")
    return plan


@app.get("/api/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    plan = _current_plan(db)
    data = plan.data_json

    total_messages = db.query(models.Message).count()
    accepted = db.query(models.Message).filter(models.Message.status == "accepted").count()
    rejected = db.query(models.Message).filter(models.Message.status == "rejected").count()

    budget = data.get("budget", {})
    judging = data.get("judging", {})

    return {
        "totalStudents": EVENT["student_count"],
        "totalTeams": EVENT["team_count"],
        "staffCount": EVENT["staff_count"],
        "judgeCount": judging.get("confirmed_judges", 0),
        "approvedBudget": budget.get("approved_budget", EVENT["approved_budget"]),
        "estimatedExpenditure": budget.get("total_committed", 0),
        "remainingBudget": budget.get("remaining", 0),
        "processedMessages": total_messages,
        "acceptedMessages": accepted,
        "rejectedMessages": rejected,
    }


@app.get("/api/messages")
def get_messages(db: Session = Depends(get_db)):
    messages = db.query(models.Message).order_by(models.Message.id).all()
    return [
        {
            "id": m.id,
            "sender": m.sender,
            "date": m.date_text,
            "content": m.raw_text,
            "status": m.status,
        }
        for m in messages
    ]


@app.get("/api/plan/current")
def get_current_plan(db: Session = Depends(get_db)):
    return _current_plan(db).data_json


@app.get("/api/plan/history")
def get_plan_history(db: Session = Depends(get_db)):
    plans = db.query(models.Plan).order_by(models.Plan.version_number.desc()).all()
    return [
        {
            "versionNumber": p.version_number,
            "isCurrent": p.is_current,
            "createdAt": p.created_at.isoformat(),
        }
        for p in plans
    ]


@app.get("/api/trace")
def get_trace(db: Session = Depends(get_db)):
    traces = db.query(models.ModelTraceRecord).order_by(models.ModelTraceRecord.call_number).all()
    return [
        {
            "callNumber": t.call_number,
            "modelName": t.model_name,
            "area": t.area,
            "input": t.input_text,
            "output": t.output_text,
            "inputTokens": t.input_tokens,
            "outputTokens": t.output_tokens,
            "totalTokens": t.total_tokens,
            "durationMs": t.duration_ms,
            "reason": t.reason,
        }
        for t in traces
    ]


@app.get("/api/validation")
def get_validation(db: Session = Depends(get_db)):
    plan = _current_plan(db)
    results = (
        db.query(models.ValidationResult)
        .filter(models.ValidationResult.plan_id == plan.id)
        .all()
    )
    return [
        {"checkName": r.check_name, "passed": r.passed, "details": r.details}
        for r in results
    ]


@app.get("/api/budget")
def get_budget(db: Session = Depends(get_db)):
    return _current_plan(db).data_json.get("budget", {})


class NewMessage(BaseModel):
    sender: str
    message: str
    date: str | None = None


@app.post("/api/messages/upload")
async def upload_messages(file: UploadFile, db: Session = Depends(get_db)):
    content = (await file.read()).decode("utf-8")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(BASE_PACK_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    return _run_full_pipeline(db)


@app.post("/api/messages/add")
def add_message(payload: NewMessage, db: Session = Depends(get_db)):
    date_text = payload.date or datetime.now(UTC).strftime("%d %b")
    block = f"Sender: {payload.sender}\nDate: {date_text}\nMessage: {payload.message}\n"
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(INCOMING_PATH, "a", encoding="utf-8") as f:
        if os.path.getsize(INCOMING_PATH) > 0 if os.path.exists(INCOMING_PATH) else False:
            f.write("\n")
        f.write(block)
    return _run_full_pipeline(db)


@app.post("/api/run")
def trigger_run(db: Session = Depends(get_db)):
    return _run_full_pipeline(db)


@app.post("/api/update")
def trigger_update(db: Session = Depends(get_db)):
    return _run_full_pipeline(db)


@app.get("/api/decisions")
def get_decisions(db: Session = Depends(get_db)):
    rows = (
        db.query(models.Decision, models.Message)
        .join(models.Message, models.Decision.message_id == models.Message.id)
        .order_by(models.Decision.id)
        .all()
    )
    return [
        {
            "id": d.id,
            "sender": m.sender,
            "message": m.raw_text,
            "area": d.area,
            "decisionText": d.decision_text,
            "accepted": d.accepted,
            "reason": d.reason,
        }
        for d, m in rows
    ]


def _get_decision_and_message(db: Session, decision_id: int) -> tuple[models.Decision, models.Message]:
    decision = db.query(models.Decision).filter(models.Decision.id == decision_id).one_or_none()
    if decision is None:
        raise HTTPException(status_code=404, detail="Decision not found.")
    message = db.query(models.Message).filter(models.Message.id == decision.message_id).one_or_none()
    if message is None:
        raise HTTPException(status_code=404, detail="Source message not found.")
    return decision, message


@app.post("/api/decisions/{decision_id}/approve")
def approve_decision(decision_id: int, db: Session = Depends(get_db)):
    """A human override for a rejected (usually pending-approval) item.
    Re-injects the original message as an explicit, authorized approval
    through the normal pipeline, rather than bypassing conflict detection -
    so the approval is itself traceable in the message/decision history."""
    _decision, message = _get_decision_and_message(db, decision_id)

    override_block = (
        f"Sender: Dean's office, email\n"
        f"Date: {datetime.now(UTC).strftime('%d %b')}\n"
        f"Message: Approved - {message.raw_text}\n"
    )
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(INCOMING_PATH, "a", encoding="utf-8") as f:
        if os.path.exists(INCOMING_PATH) and os.path.getsize(INCOMING_PATH) > 0:
            f.write("\n")
        f.write(override_block)

    return _run_full_pipeline(db)


@app.post("/api/decisions/{decision_id}/reject")
def reject_decision(decision_id: int, db: Session = Depends(get_db)):
    """Confirms a rejection as final - no new message to process, so this
    just marks the source message's status without spending a model call."""
    _decision, message = _get_decision_and_message(db, decision_id)
    message.status = "rejected"
    db.commit()
    return {"status": "rejected", "messageId": message.id}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)
