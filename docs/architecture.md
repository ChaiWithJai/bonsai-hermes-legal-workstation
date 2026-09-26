# How the commitments review works

The user asks which client commitments need an owner. Hermes gives the request to Bonsai on the local workstation, and the model uses a small set of tools to read obligations, inspect their source and record an explicitly requested assignment.

## Sources and responsibility

The commitments register records the obligation, deadline, owner, status, source section and revision. The agreement supplies the clause. A separate delivery handoff supplies account history and prerequisites, such as an unconfirmed material-delivery date. The handoff does not amend the agreement.

The sample register is seeded in advance. The implementation does not extract arbitrary agreements into obligations. Someone must prepare and verify the register before using it for a review.

## Tool behavior

`review_commitments` returns open commitments in due-date order, placing unknown dates last. `get_commitment` retrieves one record and its source clause. When a local handoff exists, it adds that context with its source type. `assign_owner` checks the named owner and expected revision, then saves the change. None of the tools notifies the assignee or records their acceptance.

A weekly list can use the register without retrieving every clause. Clause interpretation and assignment require a current source read. The model explains what it found; the tools control reads and writes.

## Local and Google storage

Without a Google credential, the tools read the selected fixture and save assignments in a local state file. `LEGAL_DATA_DIR` selects the source version, and `LEGAL_WORKSTATION_STATE` selects the mutable register. Historical source versions and captures can therefore be retained while a separate demo is exercised.

With a Google credential, the tools read the commitments Sheet and retrieve agreement files through the Drive API. Assignment checks the Sheet revision, writes the owner and incremented revision, then reads them back before reporting success. The credential file is read on each request; refreshing it does not require storing a token in the profile. Automatic OAuth refresh is not implemented.

The local lock serializes assignments on one host. Sheets reads and writes are separate API calls, so other hosts or manual editors can still race with the tool. A failed or timed-out write must be reread before retrying because its remote outcome may be unknown.

Delivery handoffs are currently local files even in Google mode. The returned source label preserves that distinction. Uploading the versioned fixture and authenticating the connected transaction remain separate deployment steps.

## Network and inference

The configured model endpoint is on loopback port 62737. The sample uses local Bonsai inference; Google API calls and Slack transport require internet access. A local model does not make messages sent through Slack or documents stored in Google local data.

The isolated profile defines the model endpoint, turn budget and permitted tools. It disables memory and tool search. Restart the gateway after changing its MCP configuration, since a running tool process can retain earlier code and settings.

## Evidence

The exported Hermes sessions identify model usage, tool calls and final answers. Offline MLflow checks examine those saved results. A local assignment, a Slack read and a manual Sheet update are separate actions; together they do not prove one connected transaction. The execution record identifies the path actually observed for each capture.
