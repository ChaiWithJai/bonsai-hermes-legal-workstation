# Observed response-limit comparison

Both requests returned identical JSON and correctly separated the parties in Section 2.1. A+ Active must provide the site schedule, accessibility plan and named escalation leads by October 1, 2026. Northstar confirms room availability and participating staff, with no stated deadline. Both responses stopped normally after 355 completion tokens. Increasing the response limit from 512 to 1,024 did not change the answer in this development case.

The first request had 320 prompt tokens and no cached prompt tokens. The second had the same prompt length, with 316 cached tokens. Observed request durations were 19.24 and 31.82 seconds respectively. These are observations from a shared resident server, not a controlled latency comparison. One pair cannot establish a speed or cost improvement.

MLflow experiment 47 contains run `74d45e24f9604460970876913c63c69a` with two native LLM spans and the full requests and responses. The runtime had a 512-token reasoning budget. The experiment changed the response limit only; it did not compare reasoning budgets.

This result narrows the next step. The model can read the isolated clause correctly under this structured prompt, so the observed Slack attribution error still requires investigation in the Hermes conversation and tool context. No Slack replay, assignment write or human acceptance occurred in this test.
