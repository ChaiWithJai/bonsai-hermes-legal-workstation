# Legal commitments workstation

A person can ask this Hermes agent which obligations in a fictional A+ Active Services client book still need an owner. The agent retrieves the exact clause from an agreement and can record an owner after an explicit request. Ternary Bonsai 2 27B supplies the explanation; the tools perform the reads and write. The included agreements, clients, signing state, and commitments are fictional.

The [public reproduction guide](https://gist.github.com/ChaiWithJai/8d4f27ee997b8ef07a46488a45ea02ae) gives the short command sequence. Read the evidence limits below before describing the Slack or Google integrations.

The sample covers two clinical AI startups and one invented clinic network. The Aster amendment changes an earlier recording retention term. Harbor's acceptance date is unknown because material delivery has not been confirmed. Northstar's program review does not make a clinical efficacy claim. These details give the agent a useful source conflict and a genuine unknown to handle.

## Reproduce the local workflow

1. Install the matching Prism runtime and Ternary Bonsai 2 27B checkpoint using the [Prism Bonsai demo](https://github.com/PrismML-Eng/Bonsai-demo) and [model card](https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf). Set `LLAMA_SERVER` and `BONSAI_MODEL` to their local paths, then run `sh start_model.sh`. The script binds loopback port 62737 with model alias `bonsai-ui-public-ternary-bonsai2`, 65,536 context tokens, `--jinja`, one slot, and a 512 token reasoning budget. If that port is already in use, check its model ID and launch flags before reusing it.
2. Run `python3 build_seed.py` and `python3 -m unittest -v test_commitments.py`. The first command validates every cited source section and rebuilds the CSV that can be imported into a spreadsheet. The tests use a temporary state file and do not change the demo register.
3. Run `python3 setup.py --profile legal-workstation-demo`. The script creates an isolated Hermes profile and refuses to replace an existing one. Then run `hermes --profile legal-workstation-demo chat --oneshot -Q --run-budget 180 -q "Run the weekly commitments review. Which commitments have no recorded owner?"`.
4. Ask about `APL-007` and its earlier retention term. Then ask, "Assign APL-007 to Khizar, and tell me whether Google Sheets was updated." Ask who owns `APL-007` in a separate turn. The default local register saves the owner in `state.json`; its tool result says `sheet_sync: mocked_local_only`.

The installed profile has three explicit tools, an eight turn limit, medium reasoning, disabled memory and disabled tool search. The tools cannot send a client message or notify an owner. The files `SOUL.md` and `hermes-config.json` show the harness configuration. To DM the agent, supply Slack credentials to a Hermes profile with the same tool configuration; no credentials are included here. The existing A+ Client Commitments app was connected to this repository's tool code for a read-only test on September 26. The first request still used the old cached MCP process after the profile edit. A supervised gateway restart loaded the new tool code, and the second Slack thread correctly read the new register. The captured session and screenshot are in `evidence/`. No Slack-triggered owner write or Google API call was tested.

## Use your own Google Drive and Sheet

The six Markdown agreements can be uploaded to a Drive folder. Copy `source-index.example.json` to `source-index.json`, replace each file ID, and set your Sheet ID. Import `commitments.csv` into a tab named `Sheet1`, preserving the column order. The owner column is E, and the revision column is I. The sample Sheet must contain exactly one row per ID.

Set `LEGAL_GOOGLE_TOKEN` in the environment that starts the Hermes tool process. The token needs read access to the Drive files and read and write access to the Sheet. With a token, `get_commitment` reads the Drive file through the Drive API, and `assign_owner` checks the Sheet revision before using the Sheets API to update columns E and I. The agent must report `source_kind` and `sheet_sync` from the tool results. Without a token, it uses the local agreement copies and updates only the local register. Google Sheets does not offer an atomic compare and swap for these two cells, so this example should not be used as a concurrent production assignment system.

The real demo folder and native Sheet were seeded in the user's personal Google account, but the public source index uses placeholders. This repository does not include the user's OAuth token, private file IDs or personal folder link. The screenshots in `evidence/` show the six Drive documents, populated native Sheet, and live Slack readback. After the model assigned APL-007 in the local register, the owner and revision were entered manually in the Sheet for the filmed state. The Sheet screenshot does not prove an agent write.

## Evidence and limits

The deterministic tests cover ordering, amendment retrieval, owner persistence, revision rejection and an honest local-only sync result. Live Hermes and Bonsai sessions are exported in `evidence/`, with an MLflow trace of 17 narrow checks over three direct sessions and two Slack sessions, including detection of the stale-MCP failure. Install `requirements-eval.txt` in a separate Python environment, start an MLflow tracking server, set `MLFLOW_TRACKING_URI`, and run `python evaluate.py` there to repeat the offline evaluation. The trace is not a model-wide accuracy result. The finance and ambient demonstrations keep their own evidence rather than borrowing this workstation's results.

![Live read-only Slack reply using the new legal tool code](evidence/slack-live-legal-workstation.jpg)

![MLflow trace of the 17 offline regression checks](evidence/mlflow-evaluation-17-checks.jpg)

For cost comparisons, use the included `tco.py` with your own machine price, power, utilization and external inference price. Its output is a scenario, not a measured saving. A matched workload and measured throughput are required to make an actual cost claim.
