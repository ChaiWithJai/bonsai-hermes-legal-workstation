"""MCP tools for fictional A+ agreements and a local commitments register."""
import fcntl
import json
import os
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(os.environ.get("LEGAL_DATA_DIR", Path(__file__).resolve().parent)).expanduser().resolve()
STATE = Path(os.environ.get("LEGAL_WORKSTATION_STATE", ROOT / "state.json"))
INDEX_PATH = ROOT / "source-index.json"
INDEX = json.loads((INDEX_PATH if INDEX_PATH.exists() else ROOT / "source-index.example.json").read_text())
OWNERS = ("Anthony", "Khizar", "Jai")


def google_configured():
    return bool(os.environ.get("LEGAL_GOOGLE_TOKEN") or os.environ.get("LEGAL_GOOGLE_TOKEN_FILE"))


def google_token():
    token = os.environ.get("LEGAL_GOOGLE_TOKEN")
    if token:
        return token
    filename = os.environ.get("LEGAL_GOOGLE_TOKEN_FILE")
    if not filename:
        return None
    try:
        token = Path(filename).expanduser().read_text().strip()
        if token.startswith("{"):
            token = json.loads(token).get("access_token", "")
        if not isinstance(token, str) or not token or any(c.isspace() for c in token):
            raise ValueError()
        return token
    except (OSError, ValueError):
        raise RuntimeError("Google token file must contain an access token or JSON with access_token") from None


def google(url, method="GET", payload=None):
    token = google_token()
    if not token:
        raise RuntimeError("Google OAuth token unavailable")
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Authorization", "Bearer " + token)
    if data is not None:
        request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.read()
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"Google API returned HTTP {error.code}") from error


def sheet_base():
    sheet_id = os.environ.get("LEGAL_SPREADSHEET_ID", INDEX["spreadsheet_id"])
    return f"https://sheets.googleapis.com/v4/spreadsheets/{urllib.parse.quote(sheet_id, safe='')}"


def sheet_range(cells):
    tab = "'" + INDEX["spreadsheet_tab"].replace("'", "''") + "'"
    return tab + "!" + cells


def sheet_values():
    cell_range = urllib.parse.quote(sheet_range("A2:J"), safe="")
    return json.loads(google(sheet_base() + "/values/" + cell_range)).get("values", [])


def rows():
    if google_configured():
        result, seen = [], set()
        fields = ("id", "customer", "obligation", "due_date", "owner", "status",
                  "source_file", "source_section", "revision", "evidence_needed")
        for number, cells in enumerate(sheet_values(), start=2):
            if not cells or not cells[0]:
                continue
            if len(cells) < 9 or cells[0] in seen:
                raise RuntimeError("Incomplete or duplicate commitment in Google Sheet")
            item = dict(zip(fields, cells + [""] * max(0, 10 - len(cells))))
            item["revision"] = int(item["revision"])
            sheet_id = os.environ.get("LEGAL_SPREADSHEET_ID", INDEX["spreadsheet_id"])
            item["sheet_url"] = "https://docs.google.com/spreadsheets/d/" + urllib.parse.quote(sheet_id, safe="") + "/edit#range=" + urllib.parse.quote(sheet_range(f"A{number}:J{number}"), safe="")
            if item["revision"] < 0:
                raise RuntimeError("Invalid Google Sheet revision")
            seen.add(item["id"])
            result.append(item)
        return result
    path = STATE if STATE.exists() else ROOT / "seed.json"
    return json.loads(path.read_text())["commitments"]


def save(all_rows):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=STATE.parent, prefix=".state-", delete=False) as handle:
        json.dump({"notice": "FICTIONAL DEMO DATA", "commitments": all_rows}, handle, indent=2)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(STATE)


def clause(row):
    filename = row["source_file"]
    file_id = INDEX["files"][filename]
    source_kind = "local_copy_of_drive_document"
    if google_configured():
        url = f"https://www.googleapis.com/drive/v3/files/{urllib.parse.quote(file_id)}?alt=media"
        content = google(url).decode("utf-8")
        source_kind = "google_drive_api"
    else:
        content = (ROOT / "agreements" / filename).read_text()
    sections = content.split("\n## ")
    matches = [section for section in sections[1:] if section.splitlines()[0].startswith(row["source_section"])]
    if len(matches) != 1:
        raise RuntimeError(f"Source section missing or ambiguous: {filename} {row['source_section']}")
    return {"source_file": filename, "source_section": row["source_section"],
            "drive_file_id": file_id, "source_kind": source_kind,
            "clause": matches[0].split("\n", 1)[1].strip()}


def update_sheet(commitment_id, owner, previous_revision):
    if not google_configured():
        return "mocked_local_only"
    base = sheet_base()
    values = sheet_values()
    matches = [(number + 2, cells) for number, cells in enumerate(values) if cells and cells[0] == commitment_id]
    if len(matches) != 1:
        raise RuntimeError("Expected exactly one matching Google Sheet row")
    number, cells = matches[0]
    sheet_revision = int(cells[8]) if len(cells) > 8 and cells[8] else 0
    if sheet_revision != previous_revision:
        raise RuntimeError("Google Sheet revision changed; reread before assigning")
    body = {"valueInputOption": "RAW", "data": [
        {"range": sheet_range(f"E{number}"), "values": [[owner]]},
        {"range": sheet_range(f"I{number}"), "values": [[previous_revision + 1]]},
    ]}
    google(base + "/values:batchUpdate", "POST", body)
    verified = [item for item in rows() if item["id"] == commitment_id]
    if (len(verified) != 1 or verified[0]["owner"] != owner
            or verified[0]["revision"] != previous_revision + 1):
        raise RuntimeError("Google Sheet write could not be verified; reread before retrying")
    return "google_sheets_api_verified"


def execute(name, arguments):
    if name == "review_commitments":
        items = [item for item in rows() if item["status"] != "complete"]
        if arguments.get("unassigned_only", False):
            items = [item for item in items if not item["owner"]]
        items.sort(key=lambda item: (not bool(item["due_date"]), item["due_date"], item["id"]))
        return {"fictional": True, "unassigned_only": arguments.get("unassigned_only", False), "count": len(items), "customer_count": len({item["customer"] for item in items}), "commitments": items,
                "register_kind": "google_sheets_api" if google_configured() else "local_fixture_mirrored_to_google_sheet"}
    commitment_id = arguments.get("commitment_id", "")
    matches = [item for item in rows() if item["id"] == commitment_id]
    if len(matches) != 1:
        raise ValueError("Use an exact commitment ID from review_commitments")
    if name == "get_commitment":
        result = {**matches[0], **clause(matches[0]), "fictional": True}
        handoff = ROOT / "agreements" / (matches[0]["source_file"].split("-", 1)[0] + "-handoff.md")
        if handoff.exists():
            result["delivery_context"] = {"source_kind": "local_sample_account_history",
                                          "source_file": handoff.name, "text": handoff.read_text()}
        return result
    if name != "assign_owner":
        raise ValueError("Unknown tool")
    owner, expected = arguments.get("owner"), arguments.get("expected_revision")
    if owner not in OWNERS or type(expected) is not int:
        raise ValueError("Use a listed owner and the current integer revision")
    STATE.parent.mkdir(parents=True, exist_ok=True)
    with (STATE.parent / ".commitments.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        all_rows = rows()
        current = next(item for item in all_rows if item["id"] == commitment_id)
        if current["revision"] != expected:
            raise ValueError("Record changed. Read it again before assigning")
        if current["owner"] == owner:
            label = f"<{current['sheet_url']}|{commitment_id}>" if current.get('sheet_url') else commitment_id
            destination = "Google Sheets" if google_configured() else "the local register"
            return {"changed": False, "commitment": current, "sheet_sync": "unchanged",
                    "previous_owner": owner, "new_owner": owner,
                    "slack_reply": f"{label} is already assigned to {owner}; no update was needed. Verified in {destination} at revision {current['revision']}."}
        previous_owner = current["owner"]
        sheet_sync = update_sheet(commitment_id, owner, expected)
        current["owner"], current["revision"] = owner, expected + 1
        current["last_sheet_sync"] = sheet_sync
        save(all_rows)
    label = f"<{current['sheet_url']}|{commitment_id}>" if sheet_sync == "google_sheets_api_verified" else commitment_id
    before = previous_owner or "unassigned"
    destination = "Google Sheets" if sheet_sync == "google_sheets_api_verified" else "the local register only"
    receipt = f"Updated {label}: owner changed from {before} to {owner}. Verified in {destination} at revision {current['revision']}; no notification was sent."
    return {"changed": True, "commitment": current, "sheet_sync": sheet_sync,
            "previous_owner": previous_owner, "new_owner": owner, "slack_reply": receipt,
            "notification_sent": False, "fictional": True}


def tool(name, description, properties, required=(), readonly=True):
    return {"name": name, "description": description,
            "inputSchema": {"type": "object", "properties": properties,
                            "required": list(required), "additionalProperties": False},
            "annotations": {"readOnlyHint": readonly, "destructiveHint": False, "openWorldHint": False}}


TOOLS = [
    tool("review_commitments", "Read open commitments, nearest due first. Includes assigned work by default. Set unassigned_only=true only to find commitments needing an owner.",
         {"unassigned_only": {"type": "boolean", "default": False, "description": "Use false for client or owner questions; true for the unassigned weekly review."}}),
    tool("get_commitment", "Read a commitment and the exact source clause; source_kind says whether Google Drive or a local copy supplied it.",
         {"commitment_id": {"type": "string"}}, ("commitment_id",)),
    tool("assign_owner", "Save an owner only after an explicit request and a current readback. Report sheet_sync exactly.",
         {"commitment_id": {"type": "string"}, "owner": {"type": "string", "enum": list(OWNERS)},
          "expected_revision": {"type": "integer"}},
         ("commitment_id", "owner", "expected_revision"), False),
]


if os.environ.get("LEGAL_TRACE") == "1":
    import mlflow

    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://127.0.0.1:5210"))
    mlflow.set_experiment("legal-workstation-demo")
    execute = mlflow.trace(name="legal_workstation_tool", span_type="TOOL")(execute)


def main():
    for line in sys.stdin:
        try:
            request = json.loads(line)
            if "id" not in request:
                continue
            method = request["method"]
            if method == "initialize":
                result = {"protocolVersion": request.get("params", {}).get("protocolVersion", "2024-11-05"),
                          "capabilities": {"tools": {}},
                          "serverInfo": {"name": "aplus-legal-workstation", "version": "1.0.0"}}
            elif method == "ping":
                result = {}
            elif method == "tools/list":
                result = {"tools": TOOLS}
            elif method == "tools/call":
                params = request["params"]
                try:
                    result = {"content": [{"type": "text", "text": json.dumps(execute(params["name"], params.get("arguments", {})))}]}
                except Exception as error:
                    result = {"isError": True, "content": [{"type": "text", "text": str(error)}]}
            else:
                result = {}
            print(json.dumps({"jsonrpc": "2.0", "id": request["id"], "result": result}), flush=True)
        except Exception as error:
            print(str(error), file=sys.stderr)


if __name__ == "__main__":
    main()
