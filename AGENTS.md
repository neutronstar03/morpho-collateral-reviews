# Agent Instructions

## Project Mode

This is an automated collateral-review artifact repo. When a user asks to
research a collateral and write it down, save the JSON file in the appropriate
`v1/chain/<chainId>/<lowercase-collateral-address>.json` path.

After adding or updating a review artifact, automatically validate the JSON,
commit the scoped change, and push it to the configured remote. Do not wait for
an additional "commit and push" prompt unless the user explicitly asks not to
commit or push.

Keep commits focused on the review artifact or instruction change being made.
Do not stage unrelated work.
