# Collateral Profile Researcher Prompt

Use this prompt with another agent when you want a first-pass collateral profile for a token.

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
1. Identify the token and the protocol/project behind it.
2. Prefer official sources over third-party summaries.
3. Find the best DefiLlama page for the protocol when possible.
4. Determine a simple token type such as:
   - `bond`
   - `delta neutral strategy`
   - `vault`
   - `lp token`
   - `staking receipt`
   - `stablecoin`
   - `wrapped asset`
   - `rwa`
   - `other`
5. Summarize redemption / exit characteristics in plain language.
   - Do not force a rigid structure.
   - Mention KYC, business-day delays, issuer redemption, offchain processes, lockups, or instant onchain exit only if supported by sources.
6. Assign a `rank` from 1 to 5 as a quick reviewer score.
   - `1` = very weak / avoid
   - `2` = concerning / many caveats
   - `3` = mixed / acceptable with caveats
   - `4` = solid / understandable structure
   - `5` = very strong / simple and transparent
7. Add short notes that would help a human reviewing the collateral.
8. Never invent facts.
9. If something is unknown, use `null`.

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
