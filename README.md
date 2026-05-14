# morpho-collateral-reviews

Manual collateral review JSON files for Morpho Blue Markets.

## Goal

This repo stores manually curated collateral review files so MBM can fetch them directly without waiting for a release or a scheduled artifact generation job.

Intended workflow:

1. Spot a new collateral in MBM.
2. Run a research agent with the review prompt.
3. Save the resulting JSON into this repo.
4. Commit + push.
5. Refresh MBM and let it fetch the new file automatically.

## Repository layout

Files are stored by version, then by chain ID, then by collateral address:

```text
v1/
  chain/
    1/
      0x....json
      oracle/
        0x....json
    8453/
      0x....json
      oracle/
        0x....json
    42161/
      0x....json
```

Example path:

```text
v1/chain/8453/0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.json
```

Rules:

- filenames must be the lowercase collateral address
- one JSON file per collateral per chain
- oracle review filenames must be the lowercase oracle address and live under `v1/chain/<chainId>/oracle/`
- use plain ASCII quotes in JSON strings
- prefer official sources
- use `null` for unknown values
- do not invent redemption details

## Git hooks

This repo includes a pre-commit hook that automatically lowercases staged collateral review JSON filenames under `v*/chain/<chainId>/`.

Enable it once per clone:

```bash
git config core.hooksPath .githooks
```

## JSON shape (v1)

Each file should look like this:

```json
{
  "version": 1,
  "chainId": 8453,
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
    }
  ]
}
```

### Field notes

- `version`: current schema version. Start with `1`.
- `chainId`: EVM chain ID for the reviewed collateral.
- `collateralAddress`: lowercase onchain token address.
- `symbol`: common market symbol.
- `name`: token or wrapper name.
- `type`: short human-readable category such as `bond`, `vault`, `lp token`, `wrapped asset`, `stablecoin`, `rwa`, or `other`.
- `protocol`: main protocol, issuer, or product name behind the collateral.
- `protocolUrl`: preferably the best matching DefiLlama protocol page; if there is no good DefiLlama page, use the most useful official URL.
- `rank`: quick reviewer score from `1` to `5`.
  - `1`: very weak / avoid
  - `2`: concerning / many caveats
  - `3`: mixed / acceptable with caveats
  - `4`: solid / understandable structure
  - `5`: very strong / simple and transparent
- `redeem`: plain-English description of the real exit path. This can mention KYC, offchain redemption, business-day settlement, maturity constraints, or instant onchain exit when supported by sources.
- `notes`: extra reviewer context that does not fit elsewhere. Keep it short and useful.
- `sources`: links that justify the entry. Prefer official sources first.

Notes on scoring:

- `rank` is a human review signal, not a formal solvency proof.
- `rank` should summarize overall comfort with the collateral structure and redeemability.
- exact scoring guidelines can evolve later; consistency matters more than precision in v1.

## JSON shape (oracle v1.1)

Oracle reviews are an additive v1.1 resource. They do not replace collateral reviews.

Files are stored by chain ID, then oracle address:

```text
v1/chain/{chainId}/oracle/{lowercaseOracleAddress}.json
```

Each file should look like this:

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
    }
  ]
}
```

### Oracle field notes

- `version`: string literal `"1.1"` for additive oracle reviews.
- `chainId`: EVM chain ID for the reviewed oracle.
- `oracleAddress`: lowercase Morpho market oracle address.
- `type`: short human-readable category such as `chainlink`, `chainlink-compatible`, `erc4626-vault`, `pendle`, `redstone`, `pyth`, `meta-oracle`, `custom-adapter`, or `unknown`.
- `provider`: short provider/protocol label such as `Chainlink`, `API3`, `Redstone`, `Pendle`, `Pyth`, `Chronicle`, `Midas`, `ERC4626`, or `Unknown`.
- `rank`: quick reviewer score from `1` to `5`.
  - `1`: very weak / opaque / avoid
  - `2`: concerning / unclear or risky oracle assumptions
  - `3`: mixed / acceptable with caveats
  - `4`: solid / understandable structure
  - `5`: very strong / simple, transparent, battle-tested
- `pricing`: one short sentence describing how the oracle prices collateral in loan-token terms.
- `notes`: short review-oriented caveat or comfort summary.
- `sources`: links that justify the entry. Prefer contract pages, official docs, provider docs, and relevant source code.

Notes on oracle scoring:

- `rank` is a human review signal, not a formal proof of oracle safety.
- Prefer concise wording; MBM displays this in a compact frontend/mobile section.
- If an oracle path is unknown or only partially understood, say so and score conservatively.

## Research prompt

The agent prompt used to produce first-pass review files lives here:

- [docs/collateral-profile-researcher-prompt.md](./docs/collateral-profile-researcher-prompt.md)
- [docs/oracle-market-researcher-prompt.md](./docs/oracle-market-researcher-prompt.md) for oracle reviews.
