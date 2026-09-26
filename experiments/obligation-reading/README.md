# Compare response limits when reading an obligation

The recorded APL-008 Slack response assigned the site-plan obligation to Northstar, although Section 2.1 assigns it to A+ Active. This development case isolates reading that clause from tool selection and assignment persistence. It asks whether a 512-token or 1,024-token response limit permits a complete extraction of both parties' obligations.

Run `python3 experiments/obligation-reading/prepare.py` from the repository root to regenerate the frozen requests and protocol. The command reads the agreement, hashes it and writes both requests. It does not start inference. Both variants use the same prompt, seed and sampling settings; only `max_tokens` changes. The structured extraction prompt differs from the Slack conversation, so success here would still need an end-to-end replay through Hermes.

Section 2.1 assigns A+ Active the site schedule, accessibility plan and named escalation leads, due October 1, 2026. Northstar separately confirms room availability and participating staff. The section does not state a deadline for Northstar. A saved owner such as Khizar identifies the person assigned the next action, not a replacement for either contracting party.

Keep JSON validity separate from factual review. Check each party, deliverable and date against the section, and retain reasoning fields, truncated responses and parse failures in the raw output. A fenced JSON response is a format failure under this prompt even if a tolerant parser can recover it. Do not award a semantic pass merely because the expected company names appear somewhere in the answer.

Execution must record the model and runtime hashes, launch settings, hardware, cache usage and raw responses. Run the variants sequentially through the shared GPU queue. Alternate their order over repeated paired runs before drawing a timing conclusion. Log those observations to MLflow under a new experiment run, and preserve the protocol with the results. No results or improvement claims are available yet.
