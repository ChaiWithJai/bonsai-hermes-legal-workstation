# Client commitments review

Ask "What commitments still need an owner?", check the agreement, and assign the next action from Slack. The bot saves the owner in Google Sheets and replies with the previous value, saved value and row link.

## How it works

Hermes connects the conversation to commitment tools, with Bonsai running locally. The tools read the agreement, check the revision and verify the saved assignment. See the [architecture](docs/architecture.md) for data flow, persistence and failure handling.

[A recorded assignment](docs/google-verification.md) changed APL-002 from unassigned to Khizar and passed independent Sheet readback.

![Assignment confirmation in Slack](evidence/slack-short-receipt.png)

## Get started

The example uses sample agreements and requests. Python 3.10 or newer runs the sample register. The commands print its unassigned commitments; [setup](docs/setup.md) adds Bonsai, Hermes, Google and Slack.

```sh
git clone https://github.com/ChaiWithJai/bonsai-hermes-legal-workstation.git
cd bonsai-hermes-legal-workstation
python3 scripts/build_seed.py
python3 -c 'import json, commitments; print(json.dumps(commitments.execute("review_commitments", {"unassigned_only": True}), indent=2))'
```

## Resources

| Resource | Use it to |
| --- | --- |
| [Setup](docs/setup.md) | Run the agent and connect its inputs. |
| [Model parameters](docs/parameter-guide.md) | Understand the settings, evidence and tuning tradeoffs. |
| [Configuration capture](docs/recorded-configuration.md) | Inspect the recorded model and Hermes settings. |
| [Cost worksheet](docs/cost-analysis.md) | Compare cost per accepted assignment. |
| [Development](docs/development.md) | Find the implementation and run its tests. |
