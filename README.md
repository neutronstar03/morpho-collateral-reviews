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
    8453/
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
- use plain ASCII quotes in JSON strings
- prefer official sources
- use `null` for unknown values
- do not invent redemption details

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
  "redeem": "Plain-English redemption / exit summary.",
  "notes": "Short extra notes for reviewers.",
  "sources": [
    {
      "label": "Official site",
      "url": "https://..."
    }
  ],
  "confidence": "low"
}
```

## Research prompt

The agent prompt used to produce first-pass review files lives here:

- [docs/collateral-profile-researcher-prompt.md](./docs/collateral-profile-researcher-prompt.md)

## Notes for MBM integration

MBM can look up a review file by chain ID + collateral address and fetch the corresponding JSON directly.

Suggested lookup pattern:

```text
v1/chain/{chainId}/{lowercaseCollateralAddress}.json
```
