"""Exports final_plan.json, execution_trace.json, and report.json to
outputs/."""

import dataclasses
import json
import os


def _to_jsonable(value):
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {k: _to_jsonable(v) for k, v in dataclasses.asdict(value).items()}
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(v) for v in value]
    return value


def plan_to_dict(plan: dict) -> dict:
    return _to_jsonable(plan)


def export_plan(plan: dict, outputs_dir: str) -> None:
    os.makedirs(outputs_dir, exist_ok=True)
    data = plan_to_dict(plan)

    final_plan = {k: v for k, v in data.items() if k not in ("trace", "trace_summary")}
    with open(os.path.join(outputs_dir, "final_plan.json"), "w", encoding="utf-8") as f:
        json.dump(final_plan, f, indent=2, default=str)

    execution_trace = {
        "trace": data.get("trace", []),
        "summary": data.get("trace_summary", {}),
    }
    with open(os.path.join(outputs_dir, "execution_trace.json"), "w", encoding="utf-8") as f:
        json.dump(execution_trace, f, indent=2, default=str)

    with open(os.path.join(outputs_dir, "report.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
