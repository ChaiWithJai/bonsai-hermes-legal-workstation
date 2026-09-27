# Workstation cost analysis for the legal agent

The cost question begins with a completed legal task, not the model's token rate. A buyer would compare monthly cost per accepted review or assignment at the same source and outcome standard, while checking whether the workstation meets the required response time and volume. The existing [scenario calculator](../tco.py) accepts arbitrary token counts. [workload_tco.py](../workload_tco.py) instead reads the call count and tokens from a captured Hermes session and labels every other input as an assumption.

The session-summary input counters are not the sum of request inputs. The legal v3 review reports 7,307 input tokens in its session summary, while its seven logged requests total 37,069 input tokens and 4,287 output tokens. The [per-call record](../evidence/weekly-v3-call-usage.json) preserves that calculation. Repeated context and cached input both appear in those request totals; they are not all newly processed tokens. Earlier assignment and readback summary counters must not be used as billable request totals without inspecting their individual calls.

Run `python3 workload_tco.py --help` to see the required fields. Pass a per-call usage record with `--session evidence/weekly-v3-call-usage.json` to populate observed tokens and model calls. Enter hardware purchase and amortization, measured idle and incremental power, monthly online hours, end-to-end task time, electricity, operations, human review, hosted token rates, volume and acceptance rates as explicit arguments. The JSON output separates `observed_from_session` from `assumptions` and reports monthly cost per accepted task for each path. The capacity number is an optimistic one-slot bound, not a service-level guarantee.

The calculator rejects session summaries. It accepts a `calls` array of per-request token counts or connected proxy records containing both `main_requests` and `session_title_requests`. Connected records include the auxiliary session-title request in the cost calculation; missing auxiliary records and duplicate exchange IDs are rejected. It applies one input rate to every request token and does not model cached-input discounts. The hosted calculation temporarily applies the local session's token counts to the hosted price inputs. A hosted model may tokenize, reason, retry or answer differently. Replace that assumption with a captured hosted run before using the comparison in a sales claim. At any chosen volume, the decision rule is to compare cost per accepted task only after both paths meet the same task-quality and response-time requirements.

For a savings claim, capture a full connected transaction and repeat it after warmup at several volumes. Record p50 and p95 time from Slack request to verified Sheet readback, model-call tokens and latency, idle and active wall energy, failures and retries, and human correction minutes. Use the same agreement cases and acceptance rubric for the hosted comparator. Only then enter measured values, with purchase price, electricity tariff, hosted rates, operations and volume stated for the buyer's setting. Vary uncertain inputs; do not present a single crossover volume as a measured fact.

The current cost output is a decision worksheet for a sales conversation. It does not establish that local inference is cheaper, faster or more accurate for this legal task.

An **accepted legal task** must cite the controlling agreement section, preserve an unknown deadline where the source does, save the intended owner and revision to the designated system, verify the row with a fresh read, and make no false claim about notification or a Google write. A human reviewer must also mark whether the source interpretation and assignment are appropriate. The connected Slack assignment has a verified Sheet write and independent readback. It still lacks a recorded human decision about the source interpretation and assignment, so an acceptance rate cannot be measured from the existing traces.


Export a completed turn from its Hermes log:

```sh
python3 scripts/export_call_usage.py \
  --log /absolute/path/to/profile/logs/agent.log \
  --session-id SESSION_ID \
  --out evidence/call-usage.json
```

The exporter requires a contiguous call sequence and a matching completed-turn count. It rejects partial logs rather than silently omitting requests. Multi-turn sessions require separate accounting; this helper covers one turn. The source log hash is recorded, and credentials or conversation text are not copied into the output.

## Connected assignment request usage

The live APL-001 assignment to Anthony used three main model requests. Their combined input was 9,452 tokens and output was 921 tokens, with 8,285 input tokens reported as cached. A separate session-title request used 283 input and 515 output tokens. Include that auxiliary request when accounting for the application's total inference work.

The [request records](../evidence/slack-anthony-request-usage.json) preserve per-call counts and exchange hashes. Main proxy request durations sum to 39.09 seconds; that sum excludes other parts of the Slack interaction and is not end-to-end latency. The assignment was independently verified in Google Sheets. Human acceptance, energy, review time and matched hosted-task costs remain unmeasured.

Pass `--session evidence/slack-anthony-request-usage.json` to use the connected assignment records. Including the session-title request gives four requests, 9,735 input tokens and 1,436 output tokens. The calculator still prices every input token at the supplied rate, so cached-input discounts require a separate hosted comparison.

## Open the interactive worksheet

From the repository root, run `python3 scripts/serve_cost.py`, then open <http://127.0.0.1:5292>. The local page uses the connected Anthony assignment's request records, including the auxiliary session-title request. Start with task volume, duration and acceptance assumptions, then expand the local and hosted cost sections. Every assumption starts blank. The server calls the same `workload_tco.analyze` function as the CLI; the browser does not maintain a separate cost formula.

The page shows recorded usage separately from buyer assumptions and reports cost per accepted task and an optimistic capacity bound. It applies one input price to all tokens, including cached input. The hosted path remains hypothetical until a matched task is measured. Inputs stay in the page and local HTTP request; the server does not save them. Stop the server with Ctrl-C.
