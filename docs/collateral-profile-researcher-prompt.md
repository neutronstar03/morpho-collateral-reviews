# Collateral Profile Researcher Prompt

Use this prompt with another agent when you want a first-pass collateral profile for a token.

This prompt is only for collateral review files under `v1/chain/{chainId}/{collateralAddress}.json`.
For oracle review files under `v1/chain/{chainId}/oracle/{oracleAddress}.json`, use [`docs/oracle-market-researcher-prompt.md`](./oracle-market-researcher-prompt.md).

Add at the bottom available tools, suggested ones:
```text
Additional tools at your disposal:
- Bun
- gh, github cli
- cast, foundry cli
```

---

## Prompt

You are researching a collateral token used in a lending market.

Input:
- chain: `<CHAIN_NAME_OR_ID>`
- tokenAddress: `<TOKEN_ADDRESS>`

Goal:
Research the token and return a simple JSON object that can be used by a UI component showing a manually curated collateral profile.

Research instructions:
1. Identify the token on the requested chain first (address, name, symbol, decimals).
2. If the user asks for the original, underlying, or accounting collateral, resolve wrappers before selecting the review target:
   - Pendle PT: call `SY()`, then the SY's `yieldToken()` or `assetInfo()`.
   - ERC-4626 share: call `asset()`.
   - Bridged/wrapped token: use official docs to identify the canonical token, but keep the target-chain representation separate.
   - If the user did not explicitly request the underlying asset, review the supplied collateral address and note its wrapper relationship instead of silently substituting it.
   - If mainnet coverage is requested too, create a distinct chain-1 profile using the mainnet address; never copy a cross-chain address into the mainnet path.
3. Identify the protocol/project behind the selected token.
4. Prefer official sources over third-party summaries.
5. Find the best DefiLlama page for the protocol when possible.
6. Determine a simple token type such as:
   - `bond`
   - `delta neutral strategy`
   - `vault`
   - `lp token`
   - `staking receipt`
   - `stablecoin`
   - `wrapped asset`
   - `rwa`
   - `other`
7. Summarize redemption / exit characteristics in plain language.
   - Do not force a rigid structure.
   - Mention KYC, business-day delays, issuer redemption, offchain processes, lockups, or instant onchain exit only if supported by sources.
   - For bridged representations, say whether a local issuer-redemption route is documented; do not assume that it is.
8. Assign a `rank` from 1 to 5 as a quick reviewer score.
   - `1` = very weak / avoid
   - `2` = concerning / many caveats
   - `3` = mixed / acceptable with caveats
   - `4` = solid / understandable structure
   - `5` = very strong / simple and transparent
9. Add short notes that would help a human reviewing the collateral.
10. Never invent facts.
11. If something is unknown, use `null`.

Return JSON only.

Use this schema:

```json
{
  "version": 1,
  "chainId": 1,
  "collateralAddress": "0x...",
  "symbol": "TOKEN",
  "name": "Token Name",
  "type": "other",
  "protocol": "Protocol Name",
  "protocolUrl": "https://defillama.com/protocol/...",
  "rank": 3,
  "redeem": "Plain-English redemption / exit summary.",
  "notes": "Short extra notes for reviewers.",
  "sources": [
    {
      "label": "Official site",
      "url": "https://..."
    },
    {
      "label": "Docs",
      "url": "https://..."
    }
  ]
}
```

Rules:
- Output valid JSON only
- Use lowercase hex address
- Use `null` for unknown values
- Include at least 2 sources when possible
- `rank` must be an integer from `1` to `5`
- Keep `redeem` concise but informative
- Keep `notes` short and review-oriented

Validation checklist before replying:
- Is the protocol correctly identified?
- Does the protocol URL point to DefiLlama when available?
- Is the `type` a simple human-usable label?
- Does `rank` roughly match the collateral's transparency and exit clarity?
- Does `redeem` describe the real exit path without over-claiming?
- Are uncertain facts represented as `null` or clearly softened?

## Required binary completion and publication

Include `decision`: `whitelist` or `blacklist`, and a nonempty evidence-based
`reason` in each completed review. Whitelist requires positive verification of
exact token identity, structure, credible evidence and redemption/exit. All other
completed research is blacklisted; distinguish proven fraud, unacceptable risk,
and insufficient credible evidence. Do not infer classification from rank or a
single transport failure. Use null for unknown facts, never a third final decision.
The maintenance Dot publishes the evidence AND durable effective classification
through the MBM #5 contract, checks stronger exclusions, and verifies consumption
before closing the issue. Do not publish negative/unclassified evidence as approval.
