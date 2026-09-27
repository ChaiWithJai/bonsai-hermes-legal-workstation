# Set up the legal commitments workstation

Run the commands below from the repository root.

## Reproduce the local workflow

The [reproduction guide](https://gist.github.com/ChaiWithJai/8d4f27ee997b8ef07a46488a45ea02ae) provides clone and checkout commands for the tested revision. Run the following commands from that checkout.

1. Install the matching Prism runtime and Ternary Bonsai 2 27B checkpoint using the [Prism Bonsai demo](https://github.com/PrismML-Eng/Bonsai-demo) and [model card](https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf). Set `LLAMA_SERVER` and `BONSAI_MODEL` to their local paths, then run `sh start_model.sh`. The script binds loopback port 62737 with model alias `bonsai-ui-public-ternary-bonsai2`, 65,536 context tokens, `--jinja`, one slot, and a 512 token reasoning budget. If that port is already in use, check its model ID and launch flags before reusing it.
2. Set `LEGAL_DATA_DIR="$PWD/fixtures/weekly-review-v3"` and `LEGAL_WORKSTATION_STATE="$(mktemp -d)/state.json"` in the same shell. Run `python3 scripts/build_seed.py` and `python3 -m unittest discover -s tests -v -p 'test_*.py'`. The first command validates the source clauses and rebuilds the CSV. The isolated state path starts with six unassigned commitments; the tests do not change it.
3. Run `python3 setup.py --profile legal-weekly-review-demo`. The script creates an isolated Hermes profile and refuses to replace an existing one. Then run `hermes --profile legal-weekly-review-demo chat --oneshot -Q --run-budget 180 -q "What commitments still need an owner for our weekly client review? Give the count and the next decision."`.
4. Ask about `APL-003` and its source clause. Then ask, "Assign APL-003 to Anthony and verify the saved owner. Do not notify anyone." Ask who owns `APL-003` in a separate turn. This local run saves the owner in the isolated state file and reports `sheet_sync: mocked_local_only`; the [connected Slack transaction](../evidence/weekly-review-v3-google-20260927/slack-assignment.json) records the separate Google Sheets write and readback.

The installed profile has three explicit tools, an eight turn limit, medium reasoning, disabled memory and disabled tool search. The tools cannot send a client message or notify an owner. The files `SOUL.md` and `hermes-config.json` show the harness configuration. To DM the agent, supply Slack credentials to a Hermes profile with the same tool configuration; no credentials are included here. The [execution record](../EVIDENCE.md) preserves the earlier runs, including a stale tool process, and the [connected verification](google-verification.md) records the subsequent Drive read and Sheets assignment.

For the recorded sampling configuration and its failed and successful clause-reading replays, see [model configuration](model-configuration.md). The guide provides an isolated profile using this repository's local settings proxy.

## Use your own Google Drive and Sheet

The six Markdown agreements can be uploaded to a Drive folder. Copy `source-index.example.json` to `source-index.json`, replace each file ID, and set your Sheet ID. Import `commitments.csv` into a tab named `Sheet1`, preserving the column order. The owner column is E, and the revision column is I. Set `spreadsheet_gid` in the source index to the tab ID shown in the Sheet URL so Slack links select the correct row; the default is 0 for the initial tab. The sample Sheet must contain exactly one row per ID.

Set `LEGAL_GOOGLE_TOKEN_FILE` to an absolute path outside the repository before running `setup.py`. The file accepts a plain access token or JSON containing `access_token`; the profile stores only its path, and the tool rereads it on each request. Refresh expired tokens in that file. Automatic OAuth refresh is not implemented. An existing profile needs the same path in the legal MCP server environment and a gateway restart. You can alternatively supply `LEGAL_GOOGLE_TOKEN` in the tool process environment. The token needs read access to the Drive files and read and write access to the Sheet. With a token, the review reads the Sheet, `get_commitment` reads the Drive file through the Drive API, and `assign_owner` checks the Sheet revision before using the Sheets API to update columns E and I. It then reads the Sheet again and verifies the owner and new revision before reporting success. The agent must report `source_kind` and `sheet_sync` from the tool results. Without a token, it uses the local agreement copies and updates only the local register. Google Sheets does not offer an atomic compare and swap for these two cells, so this example should not be used as a concurrent production assignment system.

Run `python3 scripts/check_google.py` to verify the Sheet and each open commitment's Drive clause without making a write. The output records source hashes and revisions without printing credentials. A successful read check does not prove write access; the assignment workflow verifies that separately.

The public source index contains placeholders for your own Drive files and Sheet. Credentials and private file IDs are excluded. The [connected verification](google-verification.md) links the captured API transaction and independent readback; the execution record identifies older screenshots that used a manually updated Sheet.


## Observe live tool calls

Install `requirements-eval.txt` into the interpreter used by the MCP server. Before creating a profile, set `LEGAL_PYTHON` to that interpreter, `LEGAL_TRACE=1` and `MLFLOW_TRACKING_URI` to your local server, such as `http://127.0.0.1:5210`. The profile preserves the tracing settings. Existing profiles need the same environment values and a tool-process restart.

Each tool invocation creates a `TOOL` span in the `legal-workstation-demo` experiment with its arguments, output and execution status. Tool results can include agreement text and assignments, so choose the tracking destination accordingly. These spans cover tool execution only. They do not measure model generation, represent a complete Slack transaction or provide a human acceptance decision. The offline evaluation runs remain separate from live tool traces.
