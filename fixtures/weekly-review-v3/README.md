# Weekly commitments review, version 3

Use the client handoffs to understand what was sold, what delivery depends on and what still needs an owner. The account notes apply the commercial handoff principles recorded in `manifest.json`; the legal clauses remain separate scenario documents.

Set `LEGAL_DATA_DIR` to this directory's absolute path before creating a new Hermes profile. The profile installer forwards the path to its tool process. Keep the existing profile and state for historical captures. The register begins with six unassigned commitments; Aster's plan is complete because the account history records early delivery and approval. `get_commitment` includes the local account handoff beside the contract clause and labels their source types separately.

The public source index contains placeholders. The nine source and handoff files and the seven-row register were staged in a separate private Drive folder and native Sheet on September 27, 2026. The local `source-index.json` maps this checkout to those files and is ignored by Git. A local model review preserved the delivery trigger and listed all six unassigned commitments, but exceeded the response-length guidance. After renewing the Google authorization, a [connected read check](../../evidence/weekly-review-v3-google-20260927/verification.json) retrieved all six open records and their Drive clauses. Two Hermes sessions then used the Sheet review and Harbor's Drive clause. See [the review results](../../docs/review-results.md). The v3 Sheet has not received an agent assignment or a Slack request. Account-level delivery ownership, contact names and payment confirmation remain unknown; the agent must not invent them.


From the repository root, create an isolated profile:

```sh
export LEGAL_DATA_DIR="$PWD/fixtures/weekly-review-v3"
export LEGAL_WORKSTATION_STATE="$HOME/.local/state/bonsai-legal-v3-fixture/state.json"
python3 scripts/build_seed.py
python3 setup.py --profile legal-weekly-review-v3-fixture
```

The CSV is written inside the selected fixture directory and includes the completed plan alongside the six unassigned commitments. The state path keeps assignments outside the source fixture. After starting the configured Bonsai server, run:

```sh
hermes --profile legal-weekly-review-v3-fixture chat --oneshot -Q --run-budget 180 -q "What commitments still need an owner? Explain what needs attention before our weekly client review."
```

The automated MCP transport test exercises review, account-context retrieval, assignment and readback in a temporary state directory. It verifies that the original demo register is unchanged. It does not call Bonsai or Google.

Version 3 makes Harbor's missing delivery event explicit. It does not treat acceptance as the event that starts the acceptance window, and it does not attribute the missing delivery record to the customer. The source clauses are unchanged.
