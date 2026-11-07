"""Validate canonical review artifacts without inferring approval from their presence."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

PATH = re.compile(r"v1/chain/([1-9][0-9]*)/(oracle/)?(0x[a-f0-9]{40})\.json")


def load_json(path):
    """Reject ambiguous objects and constants unsupported by JSON consumers."""
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError(f"invalid JSON constant: {value}")

    return json.loads(path.read_text(), object_pairs_hook=unique_object,
                      parse_constant=invalid_constant)


def validate(path, data, allow_legacy=False):
    errors = []
    match = PATH.fullmatch(path)
    if not match:
        return ["noncanonical review path"]
    if not isinstance(data, dict):
        return ["review must be an object"]
    chain, oracle, address = match.groups()
    identity = "oracleAddress" if oracle else "collateralAddress"
    if (type(data.get("version")) is not (str if oracle else int)
            or data.get("version") != ("1.1" if oracle else 1)):
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
            try:
                parsed = urlparse(url) if isinstance(url, str) else None
                valid_url = (parsed is not None and parsed.scheme in ("http", "https")
                             and bool(parsed.hostname))
                if valid_url:
                    # Accessing port also validates malformed or out-of-range ports.
                    parsed.port
            except ValueError:
                valid_url = False
            if not valid_url:
                errors.append("invalid source URL")
    # Legacy descriptive artifacts remain readable, but confer no binary decision.
    # Never manufacture decisions by assigning a threshold to rank.
    if not oracle and "decision" not in data and not allow_legacy:
        errors.append("completed collateral review requires an explicit decision")
    if "decision" in data or "reason" in data:
        if oracle or data.get("decision") not in ("whitelist", "blacklist"):
            errors.append("invalid collateral decision")
        if not isinstance(data.get("reason"), str) or not data["reason"].strip():
            errors.append("decision requires a reason")
    return errors


def load_legacy(root):
    """Load exact, existing collateral paths; never accept substring membership."""
    legacy_file = root / "legacy-unclassified.v1.json"
    if not legacy_file.exists():
        return set()
    legacy = load_json(legacy_file)
    if not isinstance(legacy, list):
        raise ValueError("legacy-unclassified.v1.json must be an array of paths")
    paths = set()
    for path in legacy:
        match = PATH.fullmatch(path) if isinstance(path, str) else None
        if not match or match.group(2) or not (root / path).is_file():
            raise ValueError(f"invalid legacy collateral path: {path!r}")
        if path in paths:
            raise ValueError(f"duplicate legacy collateral path: {path}")
        paths.add(path)
    return paths


def build_manifest(root):
    entries = []
    legacy = load_legacy(root)
    for path in sorted((root / "v1").rglob("*.json")):
        relative = path.relative_to(root).as_posix()
        data = load_json(path)
        errors = validate(relative, data, allow_legacy=relative in legacy)
        if errors:
            raise ValueError(f"{relative}: {errors}")
        if "oracleAddress" not in data and "decision" in data:
            entries.append({key: data[key] for key in
                            ("chainId", "collateralAddress", "decision", "reason")}
                           | {"reviewPath": relative})
    return {"version": 1, "decisions": entries}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--write-index", action="store_true", help="regenerate explicit decisions only")
    args = parser.parse_args()
    failures = 0
    try:
        legacy = load_legacy(args.root)
    except (ValueError, OSError) as error:
        print(f"Invalid legacy migration list: {error}")
        return True
    paths = sorted((args.root / "v1").rglob("*.json"))
    if not paths:
        parser.error("no review artifacts found")
    for path in paths:
        try:
            errors = validate(path.relative_to(args.root).as_posix(), load_json(path),
                              allow_legacy=path.relative_to(args.root).as_posix() in legacy)
        except (ValueError, OSError) as error:
            errors = [str(error)]
        for error in errors:
            print(f"{path.relative_to(args.root)}: {error}")
        failures += bool(errors)
    if not failures:
        expected = json.dumps(build_manifest(args.root), indent=2) + "\n"
        target = args.root / "decisions.v1.json"
        if args.write_index:
            target.write_text(expected)
        elif not target.exists() or target.read_text() != expected:
            print("decisions.v1.json is missing/stale; run with --write-index")
            failures += 1
    print(f"Validated {len(paths)} reviews; {failures} invalid")
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
