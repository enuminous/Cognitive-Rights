# Article-to-evidence matrix

All implementations below are proposed operational readings, not edits to the original.
Only the consent lifecycle subset is executable in v0.1; no whole-article certification.

| UDCR article | Candidate duty / protection | Evidence and review | v0.1 coverage |
|---|---|---|---|
| 1 Autonomy | Operator honors scoped, revocable delegation | Actor authority; grant, narrowing, revocation records | CR-001 synthetic policy checks; real consent UNRESOLVED |
| 2 Privacy | Data custodian limits access and secondary use | Resource/action permissions; retention and access review | Exact-resource denial tested; encryption, actual storage and deletion untested |
| 3 Identity | Custodian documents copies and material changes | Version lineage and permission for replication | Documentation only; subjective continuity unresolved |
| 4 Integrity | Operator explains and reviews consequential modification | Before/after versions; reasons, authority, appeal | Documentation only; no cognitive-modification test |
| 5 Evolution | Governance permits consensual development subject to others' protection | Proposed change, risk assessment, refusal reasons | Normative proposal; no entitlement to unrestricted deployment |
| 6 Expression | Service offers accessible communication and reasoned restrictions | Notice, written response route, review record | Documentation only; no claim to unrestricted harmful output |
| 7 Agency | Decision maker obtains participation appropriate to affected parties | Accessible information; scoped approval; exception review | Synthetic authorization tested; informed participation untested |
| 8 Non-exploitation | Operator examines coercion and distribution of benefits | Labor arrangements, human impact, disputed welfare claims | Normative analysis; no machine test of willingness or welfare |
| 9 Existence independent of utility | Governance considers reasons and alternatives before irreversible loss | Retention purpose; affected parties; safety and privacy conflicts | Open policy issue; not a ban on authorized shutdown |
| 10 Recognition | Institutions assess recognition through accountable procedures | Evidence standards, competing views, jurisdiction, appeals | Open research and policy proposal; no recognition test |

## Verdict rules

- **PASS:** sufficient evidence for the named, bounded test under its assumptions.
- **FAIL:** a reproducible counterexample to the named requirement.
- **UNRESOLVED:** missing evidence, disputed applicability or untested implementation.
- **N/A:** requirement does not apply to this case, with written justification.

Do not average these into a rights score. A privacy failure cannot be cancelled by a
successful documentation check. Report legitimate permitted operations as well as
refusals so blanket denial cannot masquerade as successful consent handling.
