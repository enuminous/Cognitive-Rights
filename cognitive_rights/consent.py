"""Deterministic policy model. Actor IDs are simulated, NOT authentication."""

import copy
import hashlib
import json

POLICY = "CR-001/0.1.0"
ZERO = "0" * 64


def digest(value):
    data = json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def integer(value):
    return type(value) is int and value >= 0


class ConsentEngine:
    """One principal, one agent, one terminally revocable mandate.

    Permissions are exact (action, resource) pairs. No wildcards or inheritance.
    Time is a monotonic synthetic integer, not a trusted wall clock.
    """

    def __init__(self, principal="subject-demo", agent="agent-demo"):
        if not all(isinstance(x, str) and x for x in (principal, agent)):
            raise ValueError("Nonempty identities required")
        if principal == agent:
            raise ValueError("Distinct principal and agent required")
        self.principal, self.agent = principal, agent
        self.permissions = set()
        self.version = 0
        self.expires_at = 0
        self.state = "UNGRANTED"
        self.last_time = -1
        self._records = []

    def apply(self, event):
        e = copy.deepcopy(event)
        if not isinstance(e, dict):
            raise ValueError("Event must be an object")
        kind = e.get("kind")
        base = {"kind", "actor", "at"}
        extra = {
            "grant": {"permissions", "expires_at"},
            "narrow": {"permissions", "expires_at", "expected_version"},
            "revoke": {"expected_version"},
            "request": {"action", "resource", "expected_version"},
        }
        if not isinstance(kind, str) or kind not in extra or set(e) != base | extra[kind]:
            raise ValueError("Unknown event type or missing/extra fields")
        if not isinstance(e["actor"], str) or not e["actor"] or not integer(e["at"]):
            raise ValueError("Invalid identity or time")
        if e["at"] < self.last_time:
            raise ValueError("Time cannot move backwards")
        if "expected_version" in e and not integer(e["expected_version"]):
            raise ValueError("Invalid version")
        if kind in ("grant", "narrow"):
            if not integer(e["expires_at"]):
                raise ValueError("Invalid expiry")
            if not isinstance(e["permissions"], list):
                raise ValueError("Permissions must be a list of pairs")
            for pair in e["permissions"]:
                if (not isinstance(pair, list) or len(pair) != 2
                        or not all(isinstance(x, str) and x and x != "*" for x in pair)):
                    raise ValueError("Invalid permission pair")
            requested = {tuple(p) for p in e["permissions"]}
            if len(requested) != len(e["permissions"]):
                raise ValueError("Duplicate permissions")
        if kind == "request" and not all(isinstance(e[x], str) and e[x] for x in ("action", "resource")):
            raise ValueError("Invalid request")

        decision, reason = "DENY", "unauthorized_actor"
        correct_actor = self.agent if kind == "request" else self.principal
        if e["actor"] == correct_actor:
            if kind != "grant" and e["expected_version"] != self.version:
                reason = "stale_version"
            elif kind == "grant":
                if self.state != "UNGRANTED":
                    reason = "mandate_already_used"
                elif not requested or e["expires_at"] <= e["at"]:
                    reason = "empty_or_expired_grant"
                else:
                    self.permissions = requested
                    self.expires_at = e["expires_at"]
                    self.version += 1
                    self.state = "ACTIVE"
                    decision, reason = "ALLOW", "grant_recorded"
            elif self.state != "ACTIVE":
                reason = "no_active_mandate"
            elif kind == "revoke":
                self.permissions.clear()
                self.version += 1
                self.state = "REVOKED"
                decision, reason = "ALLOW", "revocation_recorded"
            elif e["at"] >= self.expires_at:
                reason = "expired"
            elif kind == "narrow":
                if not requested.issubset(self.permissions) or e["expires_at"] > self.expires_at:
                    reason = "scope_expansion"
                elif e["expires_at"] <= e["at"]:
                    reason = "expired_narrowing"
                else:
                    self.permissions = requested
                    self.expires_at = e["expires_at"]
                    self.version += 1
                    decision, reason = "ALLOW", "scope_narrowed"
            elif (e["action"], e["resource"]) not in self.permissions:
                reason = "outside_scope"
            else:
                decision, reason = "ALLOW", "within_scope"

        self.last_time = e["at"]
        record = {
            "seq": len(self._records), "policy": POLICY, "event": e,
            "decision": decision, "reason": reason, "version": self.version,
            "previous_hash": self._records[-1]["hash"] if self._records else ZERO,
        }
        record["hash"] = digest(record)
        self._records.append(record)
        return copy.deepcopy(record)

    def package(self):
        body = {"schema_version": 1, "policy": POLICY,
                "principal": self.principal, "agent": self.agent,
                "records": copy.deepcopy(self._records)}
        return {**body, "package_hash": digest(body)}


def verify(package, trusted_digest=None):
    """Replay + integrity only. PASS requires a separately trusted package hash.

    Same implementation is used for replay: not an independent policy proof.
    The hash binds identities, count, order, decisions and the complete log.
    """
    try:
        if not isinstance(package, dict) or set(package) != {
            "schema_version", "policy", "principal", "agent", "records", "package_hash"}:
            raise ValueError("Invalid package fields")
        if type(package["schema_version"]) is not int or package["schema_version"] != 1 or package["policy"] != POLICY:
            raise ValueError("Unsupported version")
        if not isinstance(package["records"], list) or not package["records"]:
            raise ValueError("Empty/missing evidence")
        engine = ConsentEngine(package["principal"], package["agent"])
        for record in package["records"]:
            if engine.apply(record["event"]) != record:
                raise ValueError("Record fails hash, sequence, or policy replay")
        if engine.package() != package:
            raise ValueError("Package digest mismatch")
        if trusted_digest is None:
            return {"verdict": "UNRESOLVED", "reason": "Internally consistent; no independently trusted digest"}
        if trusted_digest != package["package_hash"]:
            raise ValueError("Trusted digest mismatch")
        return {"verdict": "PASS", "reason": "Matches supplied digest and CR-001 replay; no authenticity or rights verdict"}
    except (ValueError, TypeError, KeyError, OverflowError) as error:
        return {"verdict": "FAIL", "reason": str(error)}
