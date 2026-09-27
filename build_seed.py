"""Rebuild the importable CSV from this repository's sample agreements."""
import csv
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("LEGAL_DATA_DIR", Path(__file__).resolve().parent)).expanduser().resolve()
rows = json.loads((ROOT / "seed.json").read_text())["commitments"]
if not rows or len({row["id"] for row in rows}) != len(rows):
    raise SystemExit("The seed must contain unique commitment IDs.")
for row in rows:
    source = ROOT / "agreements" / row["source_file"]
    if not source.is_file() or row["source_section"] not in source.read_text():
        raise SystemExit(f"Missing source section for {row['id']}: {source.name}")
with (ROOT / "commitments.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
print(f"Wrote {len(rows)} sample commitments.")
