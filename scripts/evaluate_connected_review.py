"""Record what the connected Northstar captures prove, including the failed answer."""

import hashlib
import json
import os
from pathlib import Path

import mlflow
from mlflow.entities import SpanType


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"


def load(name):
    path = EVIDENCE / name
    return json.loads(path.read_text()), hashlib.sha256(path.read_bytes()).hexdigest()


@mlflow.trace(name="review_connected_northstar_captures", span_type=SpanType.EVALUATOR)
def review():
    first, first_hash = load("slack-google-assignment-session.json")
    readback, readback_hash = load("slack-google-readback.json")
    corrected, corrected_hash = load("slack-assigned-lookup-repaired.json")
    receipt, receipt_hash = load("slack-short-receipt.json")

    first_calls = first["tool_calls"]
    corrected_calls = [call["function"]["name"] for turn in corrected["tool_calls"] for call in turn]
    first_answer = first["final_answer"]
    corrected_answer = corrected["final_answer"]
    checks = {
        "first_run": {
            "drive_read_and_sheet_write_tools_called": first_calls == [
                "mcp__commitments__get_commitment",
                "mcp__commitments__assign_owner",
                "mcp__commitments__get_commitment",
            ],
            "independent_owner_readback": readback["commitment_id"] == "APL-008"
            and readback["owner"] == "Khizar" and readback["revision"] == 1,
            "responsible_party_and_deliverables_correct": "A+ Active will provide the site schedule, accessibility plan and named escalation leads" in first_answer
            and "Northstar will confirm room availability and participating staff separately" in first_answer,
        },
        "corrected_lookup": {
            "assigned_record_queried": corrected_calls == [
                "mcp__commitments__review_commitments",
                "mcp__commitments__get_commitment",
            ] and '"unassigned_only":false' in corrected["tool_calls"][0][0]["function"]["arguments"],
            "responsible_party_and_deliverables_correct": "A+ Active will provide the site schedule, accessibility plan and named escalation leads" in corrected_answer
            and "Northstar will confirm room availability and participating staff separately" in corrected_answer,
            "owner_and_revision_reported": "Khizar" in corrected_answer and "revision 2" in corrected_answer,
        },
        "short_receipt": {
            "owner_and_revision_match_independent_readback": receipt["readback"] == {
                "id": "APL-002", "owner": "Khizar", "revision": 1
            } and "owner changed from unassigned to Khizar" in receipt["final_answer"],
            "two_sentences_and_no_notification_claim": receipt["sentence_count"] == 2
            and "no notification was sent" in receipt["final_answer"],
        },
    }
    return {
        "checks": checks,
        "evidence_sha256": {
            "first_run": first_hash, "first_readback": readback_hash,
            "corrected_lookup": corrected_hash, "short_receipt": receipt_hash,
        },
        "session_ids": [first["session_id"], corrected["session_id"], receipt["session_id"]],
        "scope": "Deterministic review of saved connected Slack and Google captures. The first answer misattributed the obligation; the later read-only reply corrected it. This does not join the live model spans or establish general accuracy or human acceptance.",
    }


if __name__ == "__main__":
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://127.0.0.1:5210"))
    mlflow.set_experiment("bonsai-legal-workstation")
    result = review()
    trace = mlflow.get_trace(mlflow.get_last_active_trace_id(), flush=True)
    result.update(trace_id=trace.info.trace_id, experiment_id=trace.info.experiment_id,
                  trace_status=trace.info.status.value)
    (EVIDENCE / "connected-review-evaluation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
