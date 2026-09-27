# Legal commitments workstation

Review the commitments that still need an owner, inspect the agreement behind each obligation and assign the next action from Slack. Counsel can leave the weekly review with recorded owners for the commitments they assigned and follow up on the obligations that still need attention.

## Review and assign a commitment

Start in Slack with "What commitments still need an owner?" Ask for the agreement behind an obligation, then name the person responsible for the next action. The agent saves the assignment in the commitments Sheet and reads it back, so you can confirm the result in the same conversation.

In the [recorded Slack transaction](docs/google-verification.md), the agent retrieved APL-008 from Google Drive and saved Khizar as its owner in Google Sheets. A separate API read confirmed the owner and revision. Recording an assignment does not notify the owner or establish their acceptance.

The included agreements cover facilitation services for clinical AI companies and a clinic network. They are sample data for reproducing the workflow. Hermes connects the conversation to the tools, with Ternary Bonsai 2 27B serving inference on the workstation. The [architecture](docs/architecture.md) explains data movement, storage and assignment behavior.

## Set up the workflow

Follow the [setup guide](docs/setup.md) to run the local example, connect your Google Drive and Sheet, and enable tool traces. The guide includes the expected result for each step and explains the difference between a local register update and a saved Google Sheets assignment.

## Understand how it works

The [architecture](docs/architecture.md) explains the components, data paths and assignment behavior. The [model configuration](docs/model-configuration.md) records the Bonsai settings and Hermes profile used for clause-reading experiments.

The [connected verification](docs/google-verification.md) documents the Drive read and saved assignment, including an obligation attribution error in the recorded response. The [review results](docs/review-results.md) and [execution record](EVIDENCE.md) preserve the checks and remaining failures.

## Evaluate workstation costs

Use the [cost analysis](docs/cost-analysis.md) to compare the cost of completing the same review locally and with a hosted model. The worksheet includes model requests, hardware, power, operations and human review. Matched runs and measured review costs are still needed to establish savings.
