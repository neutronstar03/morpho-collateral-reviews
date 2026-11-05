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
- `rank`: quick reviewer score from `0` to `5`.
  - `0`: broken / stale data at the dated observation
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

## Validation and binary decisions

Run `python3 scripts/validate.py` and `python3 -m unittest discover -s tests`.
The validator checks every canonical collateral/oracle resource, identity, field type,
rank and source URL. Nullable collateral facts and additive metadata are preserved.
Oracle ranks support **0-5**; 0 records a broken/stale finding at the stated
observation time. It is never a collateral classification.

Completed collateral research must include `decision` (`whitelist` or `blacklist`)
and a nonempty `reason`. A positive review must establish exact chain/token identity,
structure, credible evidence and an understandable redemption/exit route. Every
other completed review is blacklisted with the specific reason (fraud, unacceptable
risk, or insufficient credible evidence after research). Do not call insufficient
evidence proven fraud or infer a decision from rank. Pending research and transport
errors are temporary workflow states, not final decisions.

Legacy artifacts without these fields are descriptive research awaiting explicit
classification. Validation permits them to preserve the corpus; their existence is
not authorization to whitelist. Negative/unclassified research must never enter
positive approval coverage. A decision is complete only after its durable producer
and MBM consumer are integrated and verified (MBM issue #5). The Dot owns research,
evidence publication and effective classification, preserving stronger exclusions.
A negative decision must be effective before publishing evidence that an older
path-only consumer could interpret as approval. Do not close a collateral issue
until the actual MBM path reflects the decision and reason; document cache intervals.

## Research prompt

The agent prompt used to produce first-pass review files lives here:

- [docs/collateral-profile-researcher-prompt.md](./docs/collateral-profile-researcher-prompt.md)
- [docs/oracle-market-researcher-prompt.md](./docs/oracle-market-researcher-prompt.md) for oracle reviews.

CI is installed in `.github/workflows/validate.yml` and runs the validator and
fixture suite on pushes and pull requests. The Loop workflow scope was verified
on 2026-11-05 before publishing this configuration.

## Authoritative decision publication (MBM #5)

The review object stores `decision` and `reason`; `python3 scripts/validate.py
--write-index` produces committed `decisions.v1.json` from valid canonical collateral
resources only. The default validator rejects a missing/stale index. Commit evidence
and index together. Legacy/unclassified and oracle resources never enter it. MBM
fetches the manifest every five minutes and its positive-only compatibility endpoint
has a five-minute edge TTL; raw GitHub/browser caches can add propagation delay.
Do not hand-edit the index. To record a negative decision before every consumer has
upgraded, first make the durable MBM asset blacklist effective. The Dot must verify
the real consuming version before closing a research issue; a source push alone is
not evidence that an unreleased application already runs the new consumer.

`legacy-unclassified.v1.json` freezes the historical unclassified paths; this is a
migration list, never an approval list. New collateral artifacts require explicit
decisions. Do not add new paths to the legacy list to bypass classification.
