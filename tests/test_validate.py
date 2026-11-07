import copy
import unittest
from scripts.validate import build_manifest, load_legacy, validate
import json
import tempfile
from pathlib import Path

ADDRESS = "0x" + "a" * 40
PATH = f"v1/chain/1/{ADDRESS}.json"
REVIEW = dict(version=1, chainId=1, collateralAddress=ADDRESS, symbol=None,
              name=None, type=None, protocol=None, protocolUrl=None, rank=None,
              redeem=None, notes=None, sources=[dict(label="Contract", url="https://etherscan.io")])


class ValidationTests(unittest.TestCase):
    def test_conflicting_duplicate_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / PATH
            path.parent.mkdir(parents=True)
            valid = json.dumps(dict(REVIEW, decision="whitelist", reason="Evidence"))
            for prefix in ['"decision": "blacklist",', '"chainId": 2,']:
                with self.subTest(prefix=prefix):
                    path.write_text("{" + prefix + valid[1:])
                    with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                        build_manifest(root)

    def test_nonstandard_constants_in_metadata_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / PATH
            path.parent.mkdir(parents=True)
            valid = json.dumps(dict(REVIEW, decision="whitelist", reason="Evidence"))
            for constant in ["NaN", "Infinity", "-Infinity"]:
                with self.subTest(constant=constant):
                    path.write_text('{"metadata": ' + constant + ',' + valid[1:])
                    with self.assertRaisesRegex(ValueError, "invalid JSON constant"):
                        build_manifest(root)

    def test_nullable_and_additive_metadata(self):
        self.assertEqual(validate(PATH, dict(REVIEW, bridging={"legacy": True}), allow_legacy=True), [])

    def test_identity_and_kind(self):
        for changes in [dict(chainId=2), dict(collateralAddress="0x" + "b" * 40),
                        dict(oracleAddress=ADDRESS, version="1.1")]:
            self.assertTrue(validate(PATH, dict(REVIEW, **changes)))
        self.assertTrue(validate(PATH.upper(), REVIEW))

    def test_rank_and_source_failures(self):
        for rank in [0, 6, 1.2, True, "3"]:
            self.assertTrue(validate(PATH, dict(REVIEW, rank=rank)))
        for sources in [None, [], [dict(label="x", url="javascript:bad")]]:
            self.assertTrue(validate(PATH, dict(REVIEW, sources=sources)))

    def test_malformed_source_urls_are_validation_errors(self):
        for url in ["https://[broken", "https://:443", "https://example.com:bad",
                    "https://example.com:70000", "https://user@"]:
            with self.subTest(url=url):
                errors = validate(PATH, dict(REVIEW, decision="whitelist", reason="Evidence",
                                             sources=[dict(label="Contract", url=url)]))
                self.assertIn("invalid source URL", errors)
        self.assertEqual(validate(PATH, dict(REVIEW, decision="whitelist", reason="Evidence",
                                            sources=[dict(label="Contract", url="https://[::1]:443") ])), [])

    def test_legacy_list_rejects_substring_membership_and_bad_shapes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / PATH
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(REVIEW))
            legacy_file = root / "legacy-unclassified.v1.json"
            for legacy in [PATH, {PATH: True}, [PATH, PATH], [None],
                           [PATH.upper()], [PATH.replace("/1/", "/2/")],
                           [PATH.replace("/1/", "/1/oracle/")]]:
                with self.subTest(legacy=legacy):
                    legacy_file.write_text(json.dumps(legacy))
                    with self.assertRaises(ValueError):
                        build_manifest(root)
            legacy_file.write_text(json.dumps([PATH]))
            self.assertEqual(load_legacy(root), {PATH})
            self.assertEqual(build_manifest(root)["decisions"], [])

    def test_explicit_binary_decision_independent_of_rank(self):
        for decision in ["whitelist", "blacklist"]:
            self.assertEqual(validate(PATH, dict(REVIEW, decision=decision, reason="Evidence")), [])
        self.assertTrue(validate(PATH, dict(REVIEW, decision="unknown", reason="Evidence")))
        self.assertTrue(validate(PATH, dict(REVIEW, decision="blacklist")))

    def test_index_requires_explicit_decision_and_is_repeatable(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / PATH
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(REVIEW))
            with self.assertRaises(ValueError):
                build_manifest(root)
            (root / "legacy-unclassified.v1.json").write_text(json.dumps([PATH]))
            self.assertEqual(build_manifest(root)["decisions"], [])
            path.write_text(json.dumps(dict(REVIEW, decision="blacklist", reason="Insufficient evidence")))
            manifest = build_manifest(root)
            self.assertEqual(manifest, build_manifest(root))
            self.assertEqual(manifest["decisions"][0]["decision"], "blacklist")
            path.write_text(json.dumps(dict(REVIEW, chainId=2)))
            with self.assertRaises(ValueError):
                build_manifest(root)

    def test_oracle_zero_is_valid_but_not_collateral_approval(self):
        oracle = dict(version="1.1", chainId=1, oracleAddress=ADDRESS, type="pyth",
                      provider="Pyth", rank=0, pricing="Historical finding", notes="Dated",
                      sources=copy.deepcopy(REVIEW["sources"]))
        self.assertEqual(validate(f"v1/chain/1/oracle/{ADDRESS}.json", oracle), [])
        self.assertTrue(validate(PATH, oracle))
        self.assertTrue(validate(f"v1/chain/1/oracle/{ADDRESS}.json", dict(oracle, rank=6)))


if __name__ == "__main__":
    unittest.main()
