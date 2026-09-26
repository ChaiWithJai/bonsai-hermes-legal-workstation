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
    stale_slack = json.loads((EVIDENCE / "live-slack-before-restart.json").read_text())
    reloaded_slack = json.loads((EVIDENCE / "live-slack-after-restart.json").read_text())
    stale_review = stale_slack["tool_calls"][0]
    reloaded_review, reloaded_record = reloaded_slack["tool_calls"]
    expected_unassigned = {"APL-001", "APL-002", "APL-003", "APL-004", "APL-008", "APL-009"}
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
        "stale_process_detected": {"APL-006", "APL-007"}.issubset(set(stale_review["ids"])) and "APL-008" not in stale_review["ids"],
        "slack_new_tools_used": [call["name"] for call in reloaded_slack["tool_calls"]] == ["mcp__commitments__review_commitments", "mcp__commitments__get_commitment"],
        "slack_new_register_read": set(reloaded_review["ids"]) == expected_unassigned and reloaded_review["count"] == 6,
        "slack_owner_readback": reloaded_record["id"] == "APL-007" and reloaded_record["owner"] == "Khizar",
        "slack_answer_matches_register": all(item in reloaded_slack["answer"] for item in expected_unassigned) and "APL-006" not in reloaded_slack["answer"],
        "slack_local_source_disclosed": reloaded_record["source_kind"] == "local_copy_of_drive_document" and "local copy" in reloaded_slack["answer"].lower(),
        "slack_sheet_limit_disclosed": reloaded_record["sheet_sync"] == "mocked_local_only" and "not a live Google Sheets read" in reloaded_slack["answer"],
    }
    return {"checks": checks, "passed": sum(checks.values()), "total": len(checks),
            "scope": "Offline deterministic checks of three direct and two Slack captured sessions. The first Slack run is an expected stale-MCP failure; the second is a live read-only Slack path. No Google API call or Slack-triggered write was evaluated."}


result = evaluate()
trace_id = mlflow.get_last_active_trace_id()
trace = mlflow.get_trace(trace_id, flush=True)
record = {**result, "trace_id": trace_id, "experiment_id": trace.info.experiment_id,
          "trace_status": trace.info.status.value}
(EVIDENCE / "evaluation.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record))
if result["passed"] != result["total"]:
    raise SystemExit(1)
