# Oracle Market Researcher Prompt

Use this prompt with another agent when you want a first-pass oracle review for a specific Morpho market.

Add at the bottom available tools, suggested ones:
```text
Additional tools at your disposal:
- Bun
- gh, github cli
- cast, foundry cli
- jq
```

---

## Prompt

You are researching the oracle used by a specific Morpho lending market.

Input:
- chain: `<CHAIN_NAME_OR_ID>`
- marketId: `<MORPHO_MARKET_ID>`

Goal:
Research the market oracle and return a compact JSON object that can be used by a UI component showing a manually curated oracle review.

Research instructions:
1. Resolve the Morpho market params for the input market:
   - loan token
   - collateral token
   - oracle address
   - LLTV, for context only
2. Identify the oracle contract and how it computes the price returned to Morpho.
   - Morpho oracle `price()` returns collateral value quoted in loan-token terms, scaled by `1e36`.
   - Explain the pricing route in one concise sentence.
3. Identify the main oracle provider or protocol responsible for the price data.
   - Examples: `Chainlink`, `API3`, `Redstone`, `Pendle`, `Pyth`, `Chronicle`, `Midas`, `ERC4626`, `Unknown`.
   - If multiple providers are involved, choose the most relevant concise label, such as `Pendle + Chainlink`, `ERC4626 + Chainlink`, or `Mixed`.
4. Determine a simple oracle type such as:
   - `chainlink`
   - `chainlink-compatible`
   - `erc4626-vault`
   - `pendle`
   - `redstone`
   - `pyth`
   - `meta-oracle`
   - `custom-adapter`
   - `unknown`
5. Check for important trust or risk signals:
   - unknown or opaque feed legs
   - proxy/upgradability
   - custom adapters
   - vault conversion assumptions
   - hardcoded peg assumptions
   - stale/low-quality feeds when discoverable
   - non-standard Chainlink-compatible sources such as API3 ReaderProxy or Redstone adapters
   - **data freshness**: always inspect `latestRoundData()` timestamps on every underlying feed; stale data signals infrastructure failure or an oracle that has stopped paying to post updates — both are catastrophic for bad debt
6. Assign a `rank` from 0 to 5 as a quick reviewer score.
   - `0` = broken / stale data / do not use in current state
   - `1` = very weak / opaque / avoid
   - `2` = concerning / unclear or risky oracle assumptions
   - `3` = mixed / acceptable with caveats
   - `4` = solid / understandable structure
   - `5` = very strong / simple, transparent, battle-tested
7. Add short notes that would help a human reviewing the oracle.
8. Prefer official sources, contract pages, verified source code, and provider docs.
9. Never invent facts.
10. If something is unknown, use `null` or say it is unknown in `notes` and score conservatively.

Return JSON only.

Use this schema:

```json
{
  "version": "1.1",
  "chainId": 1,
  "oracleAddress": "0x...",
  "type": "chainlink-compatible",
  "provider": "API3",
  "rank": 3,
  "pricing": "COMP/USD divided by USDC/USD using API3 ReaderProxy feeds.",
  "notes": "Direct pair route, but depends on API3 dAPI configuration rather than native Chainlink feeds.",
  "sources": [
    {
      "label": "Oracle contract",
      "url": "https://etherscan.io/address/0x..."
    },
    {
      "label": "Provider docs",
      "url": "https://..."
    }
  ]
}
```

Rules:
- Output valid JSON only.
- Use lowercase hex addresses.
- `version` must be the string `"1.1"`.
- `rank` must be an integer from `0` to `5`.
- Keep `pricing` to one concise sentence.
- Keep `notes` short and review-oriented.
- Include at least 2 sources when possible.
- Do not include a full dependency graph; compress the finding into `pricing` and `notes`.
- Do not output market-specific fields such as `marketId`, `loanToken`, or `collateralToken` unless explicitly asked. The review file is keyed by oracle address.

Validation checklist before replying:
- Did you resolve the exact oracle address used by the market?
- Does `oracleAddress` match the file path target?
- Is the provider label short enough for a UI row?
- Is the oracle type simple and human-readable?
- Does `pricing` explain the collateral-to-loan-token route without over-explaining?
- Does `rank` reflect complexity, transparency, upgradability, and data-source quality?
- Are uncertain facts represented as `null` or clearly softened?
- Did you check `latestRoundData()` timestamps on every underlying feed for staleness?
