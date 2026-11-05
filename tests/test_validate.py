import copy
import unittest
from scripts.validate import validate

ADDRESS = "0x" + "a" * 40
PATH = f"v1/chain/1/{ADDRESS}.json"
REVIEW = dict(version=1, chainId=1, collateralAddress=ADDRESS, symbol=None,
              name=None, type=None, protocol=None, protocolUrl=None, rank=None,
              redeem=None, notes=None, sources=[dict(label="Contract", url="https://etherscan.io")])


class ValidationTests(unittest.TestCase):
    def test_nullable_and_additive_metadata(self):
        self.assertEqual(validate(PATH, dict(REVIEW, bridging={"legacy": True})), [])

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

    def test_explicit_binary_decision_independent_of_rank(self):
        for decision in ["whitelist", "blacklist"]:
            self.assertEqual(validate(PATH, dict(REVIEW, decision=decision, reason="Evidence")), [])
        self.assertTrue(validate(PATH, dict(REVIEW, decision="unknown", reason="Evidence")))
        self.assertTrue(validate(PATH, dict(REVIEW, decision="blacklist")))

    def test_oracle_zero_is_valid_but_not_collateral_approval(self):
        oracle = dict(version="1.1", chainId=1, oracleAddress=ADDRESS, type="pyth",
                      provider="Pyth", rank=0, pricing="Historical finding", notes="Dated",
                      sources=copy.deepcopy(REVIEW["sources"]))
        self.assertEqual(validate(f"v1/chain/1/oracle/{ADDRESS}.json", oracle), [])
        self.assertTrue(validate(PATH, oracle))
        self.assertTrue(validate(f"v1/chain/1/oracle/{ADDRESS}.json", dict(oracle, rank=6)))


if __name__ == "__main__":
    unittest.main()
