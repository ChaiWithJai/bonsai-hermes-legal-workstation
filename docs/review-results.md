# Weekly review results

The weekly review must identify unassigned work and explain the controlling obligation without inventing a deadline. An assignment must persist the intended owner and report which system was updated.

## Recorded model runs

Both September 26 reviews below used the version 2 agreements and register. The v3 label on the second session identifies the instruction revision, not version 3 of the sample data.

| Session | Observation | Required correction |
| --- | --- | --- |
| `20260926_160126_b10a74` | The answer included all six unassigned commitments and excluded the completed plan. It used 264 words against 200-word guidance. | Reduce repetition while preserving source context. |
| `20260926_160447_d1bdf0` | The answer included all six IDs, but said acceptance confirmation starts Harbor's deadline. The agreement starts the five-business-day period at delivery of materials. It used 291 words. | Correct the missing-event description and repeat the source-interpretation test. |

Version 3 of the sample data identifies the missing delivery record explicitly and avoids assigning responsibility for the gap to the customer. It has not yet been tested with the model. A deterministic fixture check confirms the fields, but cannot establish that the next model answer interprets them correctly.

The second review made seven model requests with 37,069 input tokens and 4,287 output tokens in total. Its session-summary input count was 7,307. The cost calculator uses individual request counts, including repeated context, and requires explicit cost assumptions. The erroneous answer is not evidence of cost per accepted review.

## Reproduction checks

Run `python3 -m unittest discover -v -p 'test_*.py'` from the repository root. The tests exercise isolated profile creation, MCP requests from another working directory, source context, assignment and readback, revision conflicts, Google adapter response handling and request-level cost accounting. They use temporary state and mocked Google responses.

The Google adapter reads the Sheet when configured and verifies assignment writes with a fresh read. Those code paths still require a live authenticated transaction from Slack through Drive and Sheets. Tests do not prove OAuth permissions, a deployed gateway configuration or a successful remote write. No human acceptance decision has been recorded for these weekly reviews.
