"""Install an isolated Hermes profile without replacing one already present."""
import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--profile", default="legal-workstation-demo")
parser.add_argument("--sampling-proxy", action="store_true", help="Use the local recorded-settings proxy on port 5266")
args = parser.parse_args()
if not re.fullmatch(r"[a-z][a-z0-9-]{1,40}", args.profile):
    raise SystemExit("Use a simple profile name")
out = Path.home() / ".hermes" / "profiles" / args.profile
if out.exists():
    raise SystemExit(f"Refusing to overwrite {out}")
config = json.loads((root / "hermes-config.json").read_text())
if args.sampling_proxy:
    config["model"]["base_url"] = "http://127.0.0.1:5266/v1"
python = Path(os.environ.get("LEGAL_PYTHON", sys.executable)).expanduser().absolute()
if not python.exists():
    raise SystemExit("Python interpreter does not exist")
config["mcp_servers"]["legal_workstation"]["command"] = str(python)
config["mcp_servers"]["legal_workstation"]["args"] = [str(root / "commitments.py")]
for name in ("LEGAL_SPREADSHEET_ID", "LEGAL_WORKSTATION_STATE", "LEGAL_GOOGLE_TOKEN_FILE", "LEGAL_DATA_DIR", "LEGAL_TRACE", "MLFLOW_TRACKING_URI"):
    if os.environ.get(name):
        config["mcp_servers"]["legal_workstation"]["env"][name] = (str(Path(os.environ[name]).expanduser().resolve()) if name in ("LEGAL_DATA_DIR", "LEGAL_WORKSTATION_STATE", "LEGAL_GOOGLE_TOKEN_FILE") else os.environ[name])
out.mkdir(parents=True)
(out / "config.yaml").write_text(json.dumps(config, indent=2) + "\n")
shutil.copy2(root / "SOUL.md", out / "SOUL.md")
(out / ".env.example").write_text("SLACK_BOT_TOKEN=\nSLACK_APP_TOKEN=\nSLACK_ALLOWED_USERS=\n")
print(out)
