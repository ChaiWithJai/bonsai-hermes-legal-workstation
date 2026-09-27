# Client commitments review

Ask "What commitments still need an owner?", check the agreement, and assign the next action from Slack. The bot saves the owner in Google Sheets and replies with the previous value, saved value and row link.

## How it works

Hermes uses local Bonsai to read agreements and call the assignment tools. The tools check the record revision before saving an owner and verify the result in Google Sheets.

[A recorded assignment](docs/google-verification.md) changed APL-002 from unassigned to Khizar and passed independent Sheet readback.

![Assignment confirmation in Slack](evidence/slack-short-receipt.png)

## Get started

With Python 3.10 or newer, print the unassigned commitments in the sample agreements:

```sh
git clone https://github.com/ChaiWithJai/bonsai-hermes-legal-workstation.git
cd bonsai-hermes-legal-workstation
python3 scripts/build_seed.py
python3 -c 'import json, commitments; print(json.dumps(commitments.execute("review_commitments", {"unassigned_only": True}), indent=2))'
```

## Resources

| Resource | Use it to |
| --- | --- |
| [Setup](docs/setup.md) | Configure Bonsai and Hermes. |
| [Architecture](docs/architecture.md) | Follow the tools, records and failure handling. |
| [Model parameters](docs/parameter-guide.md) | Choose settings and inspect the supporting measurements. |
| [Configuration capture](docs/recorded-configuration.md) | See the model and Hermes settings used in the recorded run. |
| [Cost worksheet](docs/cost-analysis.md) | Compare cost per accepted assignment. |
| [Development](docs/development.md) | Find the implementation and run its tests. |
| [Weekly review scenario](fixtures/weekly-review-v3/README.md) | Review the connected Sheet and Drive read for the updated agreements. |
