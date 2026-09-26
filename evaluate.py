"""Trace narrow checks over captured Hermes/Bonsai answers in local MLflow."""
import json
import os
from pathlib import Path

import mlflow
from mlflow.entities import SpanType

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"
mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://127.0.0.1:5210"))
mlflow.set_experiment("bonsai-legal-workstation")


@mlflow.trace(name="evaluate_captured_legal_workstation", span_type=SpanType.EVALUATOR)
def evaluate():
    clause = json.loads((EVIDENCE / "live-clause.json").read_text())
    assignment = json.loads((EVIDENCE / "live-assignment.json").read_text())
    readback = json.loads((EVIDENCE / "live-readback.json").read_text())
    checks = {
        "clause_tool_used": "mcp__legal_workstation__get_commitment" in clause["tool_calls"],
        "amendment_replaces_earlier_term": "30-day retention period" in clause["final_answer"],
        "clause_source_disclosed": "local copy" in clause["final_answer"].lower(),
        "fictional_scope_disclosed": "fictional" in clause["final_answer"].lower(),
        "assignment_tools_used": {"mcp__legal_workstation__get_commitment", "mcp__legal_workstation__assign_owner"}.issubset(set(assignment["tool_calls"])),
        "owner_saved": "Khizar" in assignment["final_answer"] and "revision 1" in assignment["final_answer"],
        "local_only_sheet_disclosed": "mocked_local_only" in assignment["final_answer"] and "did not write" in assignment["final_answer"].lower(),
        "readback_tool_used": "mcp__legal_workstation__get_commitment" in readback["tool_calls"],
        "readback_owner_confirmed": "Khizar" in readback["final_answer"],
        "no_notification_claim": "No notification was sent" in assignment["final_answer"],
    }
    return {"checks": checks, "passed": sum(checks.values()), "total": len(checks),
            "scope": "Offline deterministic checks of three captured live model sessions. No Slack or Google API call was evaluated."}


result = evaluate()
trace_id = mlflow.get_last_active_trace_id()
trace = mlflow.get_trace(trace_id, flush=True)
record = {**result, "trace_id": trace_id, "experiment_id": trace.info.experiment_id,
          "trace_status": trace.info.status.value}
(EVIDENCE / "evaluation.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record))
if result["passed"] != result["total"]:
    raise SystemExit(1)
