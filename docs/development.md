# Development

| Location | What to change |
| --- | --- |
| `commitments.py` | Register reads, source retrieval, owner writes and verification. |
| `agreements/`, `seed.json`, `commitments.csv` | Sample agreements and register inputs. |
| `SOUL.md`, `hermes-config.json`, `config/` | Agent instructions, tool access and sampling. |
| `scripts/` | Google checks, request capture and the cost worksheet server. |
| `tests/` | Assignment, source and configuration regression checks. |
| `docs/`, `evidence/` | Setup and architecture guides, followed by recorded results. |

Run `python3 -m unittest discover -s tests -v` after changing a tool. Use the [cost worksheet](../docs/cost-analysis.md) to compare cost per accepted assignment at your workload, and the [connected verification](../docs/google-verification.md) to inspect the Slack and Google evidence.
