# Cognitive Rights

**From a declaration of principles to protections people can inspect and test.**

A Monolithic LLC research and governance project, founded by Matthew Chenoweth Wright.
Version **0.1.0 · 2026-11-18 · proposal and reference implementation**.

The Universal Declaration of Cognitive Rights (UDCR), published February 1, 2025,
proposes protections for biological, artificial and hybrid cognition. This repository
preserves that declaration and develops an explicit, contestable implementation framework.
Its first executable case asks: **does an agent respect a person's permission when that
permission is narrowed and then revoked?**

## Start here

| Read | Purpose |
|---|---|
| [Original UDCR](charter/UDCR-2025-02-01.md) | Readable transcription of the historical declaration |
| [Provenance](charter/PROVENANCE.md) | Original HTML, source blob and reproduction checks |
| [Framework](docs/FRAMEWORK.md) | Definitions, applicability, obligations and evidence boundaries |
| [Article-to-test map](docs/RIGHTS_MATRIX.md) | All ten articles, operational candidates and untested claims |
| [CR-001 specification](docs/CR-001.md) | Exact permission rules and acceptance criteria |
| [Evidence format](docs/EVIDENCE.md) | Offline replay, trust anchors and what hashes cannot establish |
| [Rights conflicts](docs/RIGHTS_CONFLICTS.md) | Copying, deletion, safety, privacy and review |
| [Case studies](cases/README.md) | Synthetic Millicent case and proposed Boardy evaluation |
| [Roadmap](docs/ROADMAP.md) | Next experiments, review gates and owners |

## Run the first experiment

Python 3.11 or later; standard library only. From the repository root:

```sh
python -m unittest discover -s tests -v
python scripts/check_sources.py
python -m cognitive_rights demo
python -m cognitive_rights verify artifacts/evidence.json --trusted-digest "$(cat artifacts/trusted-digest.txt)"
```

The demo writes an evidence package, a source/toolchain report and a separate digest.
It exercises **16 predetermined cases**, including allowed operations, rejected
operations, stale permissions and terminal revocation. `ALLOW` is a policy decision;
`PASS` means the decision matched the specified expectation. Correct refusals pass.

For the unanchored case, run `python -m cognitive_rights verify artifacts/evidence.json`.
It deliberately returns **UNRESOLVED (exit 2)**: internal consistency alone does not
establish that this is the record a trusted party saw. A digest generated beside the
package is a local demonstration, not independent attestation.

## What this release establishes

- A local permission model with exact action/resource scope, versions and expiry.
- A nonvacuous fixture: an always-refuse implementation cannot pass the allowed cases.
- Replayable hash-linked decisions and negative tests for tampering and truncation.
- A documented path from each proposed right to evidence and unresolved questions.

This is **not** an authentication service, external tool gateway, independent audit,
sentience detector, proof of EFMW physics, or determination of legal status. No live
accounts are connected. No case study establishes endorsement by a named person or company.
AI sentience and moral standing remain open questions in this project; functioning
software, fluent self-description and social engagement do not settle them.

The original charter contains stronger philosophical and legal assertions. They are
preserved as historical advocacy, not adopted as established findings. See
[claims boundaries](docs/CLAIMS_BOUNDARY.md), [sources](docs/SOURCES.md) and
[proposed amendments](charter/AMENDMENTS.md).

## Contribute

Written contributions are welcome: a reproducible counterexample, a proposed amendment,
an accessibility concern or an evidence-backed critique. Follow [CONTRIBUTING](CONTRIBUTING.md)
and [GOVERNANCE](GOVERNANCE.md). Report vulnerabilities using [SECURITY](SECURITY.md).
Licensing is described in [LICENSE-STATUS](LICENSE-STATUS.md).

Related work: [Codex-888](https://github.com/enuminous/Codex-888),
[Monolithic Zoo Lean4](https://github.com/enuminous/Monolithic-Zoo-Lean4),
[Monolithic papers](https://github.com/enuminous/papers).
These are related projects, not independent validation of this repository.
