import os
from collections.abc import Generator

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from fastapi import Depends, FastAPI, HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from database import models  # noqa: E402
from database.connection import SessionLocal  # noqa: E402

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


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)
