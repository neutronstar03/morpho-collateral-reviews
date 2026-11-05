"""Validate canonical review artifacts without inferring approval from their presence."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

PATH = re.compile(r"v1/chain/([1-9][0-9]*)/(oracle/)?(0x[a-f0-9]{40})\.json")


def validate(path, data):
    errors = []
    match = PATH.fullmatch(path)
    if not match:
        return ["noncanonical review path"]
    if not isinstance(data, dict):
        return ["review must be an object"]
    chain, oracle, address = match.groups()
    identity = "oracleAddress" if oracle else "collateralAddress"
    if data.get("version") != ("1.1" if oracle else 1):
        errors.append("unsupported resource version")
    if type(data.get("chainId")) is not int or data["chainId"] != int(chain):
        errors.append("chainId must match path")
    if data.get(identity) != address:
        errors.append(f"{identity} must match path")
    if ("collateralAddress" if oracle else "oracleAddress") in data:
        errors.append("wrong resource kind")
    fields = ("type", "provider", "pricing", "notes") if oracle else (
        "symbol", "name", "type", "protocol", "protocolUrl", "redeem", "notes")
    for key in fields:
        value = data.get(key)
        if key not in data or (not isinstance(value, str) and (oracle or value is not None)):
            errors.append(f"invalid {key}")
        elif oracle and not value.strip():
            errors.append(f"empty {key}")
    rank = data.get("rank")
    if "rank" not in data or not ((not oracle and rank is None) or (
        type(rank) is int and (0 if oracle else 1) <= rank <= 5)):
        errors.append("unsupported rank")
    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("sources must be a nonempty array")
    else:
        for source in sources:
            if not isinstance(source, dict) or not isinstance(source.get("label"), str) or not source["label"].strip():
                errors.append("invalid source label")
                continue
            url = source.get("url")
            parsed = urlparse(url) if isinstance(url, str) else None
            if not parsed or parsed.scheme not in ("http", "https") or not parsed.netloc:
                errors.append("invalid source URL")
    # Legacy descriptive artifacts remain readable, but confer no binary decision.
    # Never manufacture decisions by assigning a threshold to rank.
    if "decision" in data or "reason" in data:
        if oracle or data.get("decision") not in ("whitelist", "blacklist"):
            errors.append("invalid collateral decision")
        if not isinstance(data.get("reason"), str) or not data["reason"].strip():
            errors.append("decision requires a reason")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    failures = 0
    paths = sorted((args.root / "v1").rglob("*.json"))
    if not paths:
        parser.error("no review artifacts found")
    for path in paths:
        try:
            errors = validate(path.relative_to(args.root).as_posix(), json.loads(path.read_text()))
        except (ValueError, OSError) as error:
            errors = [str(error)]
        for error in errors:
            print(f"{path.relative_to(args.root)}: {error}")
        failures += bool(errors)
    print(f"Validated {len(paths)} reviews; {failures} invalid")
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
