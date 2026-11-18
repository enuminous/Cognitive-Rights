# Evidence package and offline verification

## Format

`schema_version=1`, `policy=CR-001/0.1.0`, `principal`, `agent`, `records`,
`package_hash`. Each record contains `seq`, `policy`, `event`, `decision`, `reason`,
`version`, `previous_hash` and `hash`. Sequence begins at zero; the first previous hash
is 64 zeros. Event fields are defined and checked strictly by `ConsentEngine.apply`.
Unknown fields and malformed events are rejected. UTF-8 JSON serialization for hashing
sorts keys, uses separators `(',', ':')`, preserves Unicode and forbids NaN.

Each record hash covers all its fields except `hash`. The package hash covers all
package fields except `package_hash`, including identities, ordered records and their
count. It is SHA-256 integrity evidence, **not a digital signature**.

## Verification contract

1. Require the supported format and a nonempty record sequence.
2. Replay events from the initial state using the declared policy implementation.
3. Compare every sequence number, decision, reason, version and chained digest.
4. Recompute the complete package digest.
5. Compare with a separately supplied trusted digest, if available.

Malformed, inconsistent or anchored-mismatching evidence returns FAIL (exit 1).
Consistent unanchored evidence returns UNRESOLVED (exit 2).
Anchored, consistent evidence returns PASS (exit 0) **only for this verification claim**.
Replay uses the same implementation as generation, so shared bugs can survive both.
Expected-outcome tests and external review are additional, different checks.

## What an anchor means

In the demo the digest is generated locally beside the package. For independent use,
a reviewer must obtain it through an authenticated separate channel or a previously
trusted signed release. Replacing both package and digest defeats an unauthenticated
comparison. Full rewrites and truncation are detectable against the original trusted
digest; internal hashes alone cannot establish original completeness or origin.

The record does not establish that real actions happened, a signer told the truth,
consent was informed, a system is conscious, or a legal obligation was satisfied.
Hashing also does not encrypt low-entropy sensitive data. Keep real personal content out.

## Reproduction record

`report.json` contains the policy version, Python version, source commit when available,
dirty-tree indicator, per-file SHA-256 values for code/tests/fixtures, expected and
observed outcomes and the package digest. A dirty checkout is identified explicitly.
Keep the source checkout and generated report together. CI uploads them as run artifacts;
workflow success is not an independent endorsement.

## Possible ALEX interface (design only)

| Needed evidence | Proposed mapping | Open integration question |
|---|---|---|
| Work order and permitted scope | Principal/agent binding and grant event | Who authenticates the grant and binds it to this run? |
| Execution and checks | Ordered request decisions plus worker receipts | Is actual execution tied atomically to permission checks? |
| Human approval | Referenced authenticated approval record | Is it specific, informed and revocable? |
| Signed Evidence Package | External signed envelope around this record | How are signing keys trusted and revoked? |
| Offline verifier | Format adapter plus pinned policy | Is there an independently implemented validator? |

No ALEX schema has been imported or validated; this is a proposed discussion interface,
not an assertion of compatibility, certification or partnership.
