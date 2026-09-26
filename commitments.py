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

ROOT = Path(__file__).resolve().parent
STATE = Path(os.environ.get("LEGAL_WORKSTATION_STATE", ROOT / "state.json"))
INDEX_PATH = ROOT / "source-index.json"
INDEX = json.loads((INDEX_PATH if INDEX_PATH.exists() else ROOT / "source-index.example.json").read_text())
OWNERS = ("Anthony", "Khizar", "Jai")


def google(url, method="GET", payload=None):
    token = os.environ.get("LEGAL_GOOGLE_TOKEN")
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


def rows():
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
    if os.environ.get("LEGAL_GOOGLE_TOKEN"):
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
    if not os.environ.get("LEGAL_GOOGLE_TOKEN"):
        return "mocked_local_only"
    sheet_id = os.environ.get("LEGAL_SPREADSHEET_ID", INDEX["spreadsheet_id"])
    tab = INDEX["spreadsheet_tab"]
    base = f"https://sheets.googleapis.com/v4/spreadsheets/{urllib.parse.quote(sheet_id)}"
    values = json.loads(google(base + "/values/" + urllib.parse.quote(tab + "!A2:I100", safe="!"))).get("values", [])
    matches = [(number + 2, cells) for number, cells in enumerate(values) if cells and cells[0] == commitment_id]
    if len(matches) != 1:
        raise RuntimeError("Expected exactly one matching Google Sheet row")
    number, cells = matches[0]
    sheet_revision = int(cells[8]) if len(cells) > 8 and cells[8] else 0
    if sheet_revision != previous_revision:
        raise RuntimeError("Google Sheet revision changed; reread before assigning")
    body = {"valueInputOption": "RAW", "data": [
        {"range": f"{tab}!E{number}", "values": [[owner]]},
        {"range": f"{tab}!I{number}", "values": [[previous_revision + 1]]},
    ]}
    google(base + "/values:batchUpdate", "POST", body)
    return "google_sheets_api"


def execute(name, arguments):
    if name == "review_commitments":
        items = [item for item in rows() if item["status"] != "complete"]
        if arguments.get("unassigned_only", True):
            items = [item for item in items if not item["owner"]]
        items.sort(key=lambda item: (not bool(item["due_date"]), item["due_date"], item["id"]))
        return {"fictional": True, "count": len(items), "commitments": items,
                "register_kind": "local_fixture_mirrored_to_google_sheet"}
    commitment_id = arguments.get("commitment_id", "")
    matches = [item for item in rows() if item["id"] == commitment_id]
    if len(matches) != 1:
        raise ValueError("Use an exact commitment ID from review_commitments")
    if name == "get_commitment":
        return {**matches[0], **clause(matches[0]), "fictional": True}
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
            return {"changed": False, "commitment": current, "sheet_sync": "unchanged"}
        sheet_sync = update_sheet(commitment_id, owner, expected)
        current["owner"], current["revision"] = owner, expected + 1
        current["last_sheet_sync"] = sheet_sync
        save(all_rows)
    return {"changed": True, "commitment": current, "sheet_sync": sheet_sync,
            "notification_sent": False, "fictional": True}


def tool(name, description, properties, required=(), readonly=True):
    return {"name": name, "description": description,
            "inputSchema": {"type": "object", "properties": properties,
                            "required": list(required), "additionalProperties": False},
            "annotations": {"readOnlyHint": readonly, "destructiveHint": False, "openWorldHint": False}}


TOOLS = [
    tool("review_commitments", "Read fictional commitments, nearest due first.",
         {"unassigned_only": {"type": "boolean"}}),
    tool("get_commitment", "Read a commitment and the exact source clause; source_kind says whether Google Drive or a local copy supplied it.",
         {"commitment_id": {"type": "string"}}, ("commitment_id",)),
    tool("assign_owner", "Save an owner only after an explicit request and a current readback. Report sheet_sync exactly.",
         {"commitment_id": {"type": "string"}, "owner": {"type": "string", "enum": list(OWNERS)},
          "expected_revision": {"type": "integer"}},
         ("commitment_id", "owner", "expected_revision"), False),
]


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
