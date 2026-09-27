# Connected assignment verification

On September 26, a DM to the Client Commitments bot requested that APL-008 be read from Drive and assigned to Khizar. Hermes called the legal tools through the local Bonsai service. The tools retrieved the agreement through the Drive API, wrote the owner and revision through the Sheets API, and verified the write with a fresh read.

A separate process then read Khizar at revision 1 from Google Sheets. Slack API readback confirmed the bot delivered its response. The response stated that no notification was sent and that recording an owner does not establish that person's acceptance.

The captured session is `20260926_164920_a982cebd`. The [session export](../evidence/slack-google-assignment-session.json), [independent readback](../evidence/slack-google-readback.json) and [delivered reply](../evidence/slack-google-delivery.json) describe one observed transaction. The earlier direct Google assignment of APL-003 to Anthony is a separate run.

The Google access token was supplied through a private local token file. Tokens expire, and automatic OAuth refresh is not implemented. The Sheet revision check is not an atomic concurrency guarantee. These runs establish the sample workflow, not production availability, legal judgment or general reliability.

The saved owner and revision were verified, but the response's description of the obligation needs correction. It called the deliverable Northstar's obligation, while the quoted clause requires A+ Active to provide the schedule, accessibility plan and escalation leads. Northstar separately confirms rooms and participating staff. Successful persistence does not establish correct legal interpretation.

## Register correction

The initial register summary also omitted the accessibility plan and introduced backup contacts that Section 2.1 does not require. On September 26, the local seed and connected Sheet were corrected to identify A+ Active and the three required deliverables. The supporting-evidence field now distinguishes Northstar's separate room and staffing confirmation. Khizar remains the recorded owner, and the Sheet revision advanced from 1 to 2.

The correction was made through the Google Sheets browser interface, then verified after reloading the page. The [cell readback](../evidence/northstar-register-correction.json) records that maintenance operation separately from the earlier agent assignment. The API credential returned HTTP 401 during this check; a fresh Slack transaction still requires restored API access and verification of the model's answer.
