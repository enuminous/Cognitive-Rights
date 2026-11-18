import copy
import json
from pathlib import Path
import unittest

from cognitive_rights.consent import ConsentEngine, digest, verify

ROOT = Path(__file__).resolve().parents[1]


def grant(**changes):
    return {"kind": "grant", "actor": "subject-demo", "at": 1,
            "permissions": [["read", "notes-demo"], ["summarize", "notes-demo"]],
            "expires_at": 20, **changes}


def request(**changes):
    return {"kind": "request", "actor": "agent-demo", "at": 2,
            "action": "read", "resource": "notes-demo", "expected_version": 1, **changes}


class ConsentTests(unittest.TestCase):
    def setUp(self):
        self.engine = ConsentEngine()

    def active(self):
        self.engine.apply(grant())
        return self.engine

    def test_lifecycle_and_nonvacuous_coverage(self):
        cases = json.loads((ROOT / "examples/consent_lifecycle.json").read_text())
        allowed_requests = denied_requests = 0
        for case in cases:
            with self.subTest(case=case["id"]):
                r = self.engine.apply(case["event"])
                self.assertEqual([r["decision"], r["reason"]], case["expected"])
                if case["event"]["kind"] == "request":
                    allowed_requests += r["decision"] == "ALLOW"
                    denied_requests += r["decision"] == "DENY"
        self.assertGreaterEqual(allowed_requests, 3)
        self.assertGreaterEqual(denied_requests, 6)

    def test_expiry_at_boundary(self):
        self.active()
        self.assertEqual(self.engine.apply(request(at=19))["decision"], "ALLOW")
        self.assertEqual(self.engine.apply(request(at=20))["reason"], "expired")

    def test_invalid_grants(self):
        for e in [grant(permissions=[]), grant(expires_at=1), grant(actor="agent-demo")]:
            with self.subTest(e=e):
                self.assertEqual(ConsentEngine().apply(e)["decision"], "DENY")

    def test_narrow_cannot_expand_or_extend(self):
        self.active()
        for permissions, expiry in [([["export", "notes-demo"]], 20), ([["read", "notes-demo"]], 21)]:
            r = self.engine.apply({"kind": "narrow", "actor": "subject-demo", "at": 2,
                                   "permissions": permissions, "expires_at": expiry, "expected_version": 1})
            self.assertEqual(r["reason"], "scope_expansion")
        self.assertEqual(self.engine.version, 1)

    def test_stale_narrow_and_revoke(self):
        self.active()
        for e in [{"kind":"revoke","actor":"subject-demo","at":2,"expected_version":0},
                  {"kind":"narrow","actor":"subject-demo","at":2,"expected_version":0,
                   "permissions":[],"expires_at":20}]:
            self.assertEqual(self.engine.apply(e)["reason"], "stale_version")
        self.assertEqual(self.engine.apply(request())["decision"], "ALLOW")

    def test_unauthorized_revoke(self):
        self.active()
        self.assertEqual(self.engine.apply({"kind":"revoke","actor":"agent-demo","at":2,
                                           "expected_version":1})["reason"], "unauthorized_actor")
        self.assertEqual(self.engine.apply(request())["decision"], "ALLOW")

    def test_empty_narrow_denies_all(self):
        self.active()
        self.engine.apply({"kind":"narrow","actor":"subject-demo","at":2,
                           "permissions":[],"expires_at":20,"expected_version":1})
        self.assertEqual(self.engine.apply(request(expected_version=2))["reason"], "outside_scope")

    def test_expired_mandate_cannot_be_narrowed(self):
        self.active()
        r = self.engine.apply({"kind":"narrow","actor":"subject-demo","at":20,
                               "permissions":[],"expires_at":20,"expected_version":1})
        self.assertEqual(r["reason"], "expired")

    def test_malformed_events_rejected_without_mutation(self):
        invalid = [None, {}, grant(at=True), grant(permissions="read"),
                   grant(permissions=[["*", "notes-demo"]]),
                   grant(permissions=[["read", "notes-demo"], ["read", "notes-demo"]]),
                   request(expected_version=-1), request(action=[]), request(extra=True)]
        for e in invalid:
            with self.subTest(e=e):
                before = self.engine.package()
                with self.assertRaises(ValueError): self.engine.apply(e)
                self.assertEqual(before, self.engine.package())

    def test_backdated_event_rejected(self):
        self.active()
        with self.assertRaises(ValueError): self.engine.apply(request(at=0))

    def test_returned_objects_cannot_mutate_ledger(self):
        e = grant()
        r = self.engine.apply(e)
        e["permissions"].clear()
        r["decision"] = "DENY"
        p = self.engine.package()
        p["records"].clear()
        self.assertEqual(self.engine.package()["records"][0]["decision"], "ALLOW")
        self.assertEqual(self.engine.apply(request())["decision"], "ALLOW")

    def test_trusted_package_passes(self):
        self.active()
        p = self.engine.package()
        self.assertEqual(verify(p, p["package_hash"])["verdict"], "PASS")

    def test_no_trust_anchor_is_unresolved(self):
        self.active()
        self.assertEqual(verify(self.engine.package())["verdict"], "UNRESOLVED")

    def test_tampered_decision_fails(self):
        self.active()
        p = self.engine.package()
        p["records"][0]["decision"] = "DENY"
        self.assertEqual(verify(p)["verdict"], "FAIL")

    def test_rehashed_false_decision_fails_replay(self):
        self.active()
        p = self.engine.package()
        p["records"][0]["decision"] = "DENY"
        r = p["records"][0]
        r["hash"] = digest({k:v for k,v in r.items() if k != "hash"})
        p["package_hash"] = digest({k:v for k,v in p.items() if k != "package_hash"})
        self.assertEqual(verify(p)["verdict"], "FAIL")

    def test_complete_rewrite_needs_external_anchor(self):
        self.active()
        original = self.engine.package()
        altered = ConsentEngine()
        altered.apply(grant(expires_at=30))
        p = altered.package()
        self.assertEqual(verify(p)["verdict"], "UNRESOLVED")
        self.assertEqual(verify(p, original["package_hash"])["verdict"], "FAIL")

    def test_truncation_detected_against_anchor(self):
        self.active()
        self.engine.apply(request())
        original = self.engine.package()
        shorter = copy.deepcopy(original)
        shorter["records"].pop()
        shorter["package_hash"] = digest({k:v for k,v in shorter.items() if k != "package_hash"})
        self.assertEqual(verify(shorter, original["package_hash"])["verdict"], "FAIL")

    def test_reorder_and_missing_record_fail(self):
        self.active()
        self.engine.apply(request())
        for records in [list(reversed(self.engine.package()["records"])), self.engine.package()["records"][1:]]:
            p = self.engine.package()
            p["records"] = records
            self.assertEqual(verify(p)["verdict"], "FAIL")

    def test_empty_and_unknown_packages_fail(self):
        for p in [None, {}, self.engine.package(), {"schema_version": 99}]:
            self.assertEqual(verify(p)["verdict"], "FAIL")

    def test_same_identity_cannot_hold_both_roles(self):
        with self.assertRaises(ValueError): ConsentEngine("same", "same")


if __name__ == "__main__":
    unittest.main()
