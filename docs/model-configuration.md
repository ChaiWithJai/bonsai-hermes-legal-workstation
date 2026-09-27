# Reproduce the explicit sampling configuration

One local Hermes clause-reading replay returned reasoning text without a final answer. The same prompt and tools produced a complete answer through a proxy that applied the settings below. This was a combined configuration change on one development case, so it does not isolate a causal setting or establish a speed improvement.

Start the model with `sh start_model.sh`, then start the repository's proxy in another terminal:

```sh
python3 scripts/settings_proxy.py
```

The proxy listens on `127.0.0.1:5266` and forwards to the model on port 62737. Create a fresh profile that uses it:

```sh
python3 setup.py --profile legal-sampling-demo --sampling-proxy
hermes --profile legal-sampling-demo chat --oneshot -Q --run-budget 180 -q "Read APL-008 and its source clause. What does A+ Active owe, what does Northstar owe, and which deadline applies to each party? Cite the section. Do not assign anyone or change the register."
```

The proxy applies `config/sampling.json`: temperature 1.0, top-p 0.95, top-k 20, min-p 0.05, presence penalty zero and repetition penalty 1.0. It enables thinking through the chat template with medium reasoning effort, removes the top-level `reasoning_effort` parameter and limits the response to at most 1,536 tokens. It preserves a caller's smaller token limit. The server's 512-token reasoning budget remains a separate launch setting.

Full requests and responses are saved under the ignored `exchanges/` directory. They can contain agreement text and internal prompts. Choose inputs and retention accordingly. The proxy requires no dependency on another demo repository. The direct endpoint remains the setup default so existing profiles retain their configuration.

The recorded successful replay used the identical proxy implementation and sampling file from ambient finance on port 5264. The legal copy changes its repository root and default port. Its request transformation has regression coverage. A later [Slack assignment and independent Google readback](../evidence/slack-short-receipt.json) verified APL-002 changing from unassigned to Khizar through the installed commitments profile. The [captured profile](recorded-configuration.md) points to the legal proxy on port 5266; that later capture does not by itself establish every request setting during the earlier transaction. See `evidence/hermes-obligation-proxy-20260926/review.json` for the recorded final answer and the failed direct replay in `evidence/hermes-obligation-read-20260926/review.json`.

Check the persisted final answer as well as the process exit code. The installed Hermes version can promote reasoning text to its CLI response while leaving the final assistant content empty. A successful process exit alone does not establish a usable answer, correct assignment or completed customer workflow.
