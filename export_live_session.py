"""Export a narrow, public-safe Hermes session record without hidden prompts."""
import argparse
import json
import sqlite3
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--state-db", type=Path, required=True)
parser.add_argument("--session-id", required=True)
parser.add_argument("--out", type=Path, required=True)
args = parser.parse_args()
connection = sqlite3.connect(args.state_db)
connection.row_factory = sqlite3.Row
messages = connection.execute(
    "SELECT role, content, tool_calls, tool_name FROM messages WHERE session_id=? AND active=1 ORDER BY id",
    (args.session_id,)).fetchall()
if not messages:
    raise SystemExit("Session not found")
usage = [dict(row) for row in connection.execute(
    "SELECT model, api_call_count, input_tokens, output_tokens, reasoning_tokens, cost_status "
    "FROM session_model_usage WHERE session_id=?", (args.session_id,))]
calls = []
for message in messages:
    if message["role"] != "assistant" or not message["tool_calls"]:
        continue
    try:
        data = json.loads(message["tool_calls"])
    except json.JSONDecodeError:
        continue
    for call in data:
        calls.append(call.get("function", {}).get("name", call.get("name", "unknown")))
user = [message["content"] for message in messages if message["role"] == "user"]
final = [message["content"] for message in messages if message["role"] == "assistant" and message["content"]]
output = {"session_id": args.session_id, "prompt": user[-1] if user else "",
          "tool_calls": calls, "final_answer": final[-1] if final else "", "usage": usage,
          "scope": "One live Hermes/Bonsai session with fictional local fixture. No Google or Slack tool was called."}
args.out.parent.mkdir(parents=True, exist_ok=True)
args.out.write_text(json.dumps(output, indent=2) + "\n")
print(args.out)
