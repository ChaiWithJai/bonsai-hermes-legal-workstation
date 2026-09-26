# Weekly commitments review, version 3

Use the client handoffs to understand what was sold, what delivery depends on and what still needs an owner. The account notes apply the commercial handoff principles recorded in `manifest.json`; the legal clauses remain separate scenario documents.

Set `LEGAL_DATA_DIR` to this directory's absolute path before creating a new Hermes profile. The profile installer forwards the path to its tool process. Keep the existing profile and state for historical captures. The register begins with six unassigned commitments; Aster's plan is complete because the account history records early delivery and approval. `get_commitment` includes the local account handoff beside the contract clause and labels their source types separately.

The source index contains placeholders. These versioned files have not been uploaded to Drive or tested in a model run. The earlier runs used version 2, as described in [the review results](../../docs/review-results.md). Supply the actual Drive IDs and Sheet mapping before using Google mode. Account-level delivery ownership, contact names and payment confirmation remain unknown; the agent must not invent them.


From the repository root, create an isolated profile:

```sh
export LEGAL_DATA_DIR="$PWD/fixtures/weekly-review-v3"
export LEGAL_WORKSTATION_STATE="$HOME/.local/state/bonsai-legal-v3-fixture/state.json"
python3 build_seed.py
python3 setup.py --profile legal-weekly-review-v3-fixture
```

The CSV is written inside the selected fixture directory and includes the completed plan alongside the six unassigned commitments. The state path keeps assignments outside the source fixture. After starting the configured Bonsai server, run:

```sh
hermes --profile legal-weekly-review-v3-fixture chat --oneshot -Q --run-budget 180 -q "What commitments still need an owner? Explain what needs attention before our weekly client review."
```

The automated MCP transport test exercises review, account-context retrieval, assignment and readback in a temporary state directory. It verifies that the original demo register is unchanged. It does not call Bonsai or Google.

Version 3 makes Harbor's missing delivery event explicit. It does not treat acceptance as the event that starts the acceptance window, and it does not attribute the missing delivery record to the customer. The source clauses are unchanged.
