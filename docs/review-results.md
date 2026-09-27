# Weekly review results

The weekly review must identify unassigned work and explain the controlling obligation without inventing a deadline. An assignment must persist the intended owner and report which system was updated.

## Recorded model runs

Both September 26 reviews below used the version 2 agreements and register. The v3 label on the second session identifies the instruction revision, not version 3 of the sample data.

| Session | Observation | Required correction |
| --- | --- | --- |
| `20260926_160126_b10a74` | The answer included all six unassigned commitments and excluded the completed plan. It used 264 words against 200-word guidance. | Reduce repetition while preserving source context. |
| `20260926_160447_d1bdf0` | The answer included all six IDs, but said acceptance confirmation starts Harbor's deadline. The agreement starts the five-business-day period at delivery of materials. It used 291 words. | Correct the missing-event description and repeat the source-interpretation test. |

Version 3 of the sample data identifies the missing delivery record explicitly and avoids assigning responsibility for the gap to the customer. Session `20260926_162807_f487c7` tested that fixture with the preceding instructions. The answer listed all six unassigned commitments, excluded the completed plan and correctly stated that acceptance is due five business days after delivery. It made two model requests and one tool call, but used 261 words and repeated the missing-delivery action. The [captured answer](../evidence/fixture-v3-session.json) preserves those limitations. One successful interpretation does not establish reliability.

The second review made seven model requests with 37,069 input tokens and 4,287 output tokens in total. Its session-summary input count was 7,307. The cost calculator uses individual request counts, including repeated context, and requires explicit cost assumptions. The erroneous answer is not evidence of cost per accepted review.

## Reproduction checks

Run `python3 -m unittest discover -s tests -v -p 'test_*.py'` from the repository root. The tests exercise isolated profile creation, MCP requests from another working directory, source context, assignment and readback, revision conflicts, Google adapter response handling and request-level cost accounting. They use temporary state and mocked Google responses.

The Google adapter reads the Sheet when configured and verifies assignment writes with a fresh read. Unit tests alone do not prove OAuth permissions, a deployed gateway configuration or a remote write. The connected Slack assignment and the separate v3 read below provide narrower live evidence. No human acceptance decision has been recorded for these weekly reviews.

## Connected version 3 review and assignment

The [September 27 verification](../evidence/weekly-review-v3-google-20260927/verification.json) read six open commitments from the v3 Google Sheet and retrieved their source clauses through the Drive API. All six clauses matched the versioned fixture files by SHA-256. An earlier traced answer correctly left Harbor's deadline undated until A+ delivery is confirmed.

The [connected Slack transaction](../evidence/weekly-review-v3-google-20260927/slack-assignment.json) asked the weekly review question, selected APL-003 as the first dated decision, retrieved its Drive context and assigned Anthony. The Sheet changed from no owner at revision 0 to Anthony at revision 1. A separate Google API read confirmed Anthony and five remaining unassigned commitments. The evidence record links the Slack receipt, Hermes session and three MLflow tool traces. It does not establish counsel approval or recurring reliability.

The [MLflow assignment capture](../evidence/weekly-review-v3-google-20260927/mlflow-assignment.jpg) shows the live `assign_owner` tool span with the requested owner and saved revision. This is a tool trace, not a model-generation trace; the independent Google readback is recorded in the transaction record above.

## Response-structure candidate

Session `20260926_163003_a43c8f` used the same version 3 fixture with instructions for complete sentences and one closing action. It removed the dash-separated fragments but incorrectly said the six commitments span four clients; the register contains three. It also exceeded the 200-word guidance. The candidate is not accepted. The captured output is in [review-v4-session.json](../evidence/review-v4-session.json).

Session `20260926_163244_34d0e6` added a tool-provided customer count and instructions to use returned totals. Its answer omitted the client total, retained all six commitments and the delivery trigger, and used 260 words with repeated closing actions. Omitting the count does not prove correct use of the new field. The [answer](../evidence/review-v5-session.json) and [candidate instructions](../evidence/review-v5-instructions.md) are retained for review. The default instructions have not been replaced by this candidate.

The 200-word target is a harness instruction, not evidence of customer value by itself. Source accuracy, useful next actions and verified assignments remain necessary regardless of answer length. None of these review-only runs proves the connected Slack, Drive and Sheet transaction.

## Traced assignment

The first tracing-enabled profile failed to load its MCP tools because setup resolved the virtual-environment Python symlink to the base interpreter, where MLflow was unavailable. Session `20260926_164046_5acdd5` correctly declined to claim an assignment. Setup now preserves the executable path.

Session `20260926_164157_d47b91` then retrieved APL-007 and saved Khizar at revision 1. The response correctly reported a local-only update and no owner notification. A separate tool process read back Khizar and revision 1, with trace `tr-09a2f237e34ce6d624c008422a80a711`. The [session](../evidence/traced-assignment-session.json), [readback](../evidence/traced-assignment-readback.json) and [request usage](../evidence/traced-assignment-call-usage.json) preserve the result. These operations did not use Slack or Google credentials.
