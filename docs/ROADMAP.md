# Roadmap and open obligations

No external reviewer, deadline or paid engagement is confirmed by this repository.
Monolithic is the proposed maintainer of internal work; outside roles remain unassigned.

| Priority | Deliverable | Owner | Acceptance gate | Status |
|---|---|---|---|---|
| 0 | Preserve original and provenance | Monolithic | Original Git blob and SHA-256 match | Implemented; check with source validator |
| 0 | CR-001 local lifecycle | Monolithic | All expected outcomes, allowed-use controls and negative tests pass | Implemented; run tests |
| 1 | Authenticated actor adapter | Monolithic + external reviewer TBD | Forged/replayed identity cannot grant authority | UNRESOLVED |
| 1 | Queued-worker revocation | Monolithic | No queued action begins after revocation acknowledgment; in-flight limits documented | UNRESOLVED |
| 1 | Independent evidence verification | External reviewer TBD | Second implementation and authenticated witness anchor | UNRESOLVED |
| 1 | Rights-conflict and legal review | Relevant specialists TBD | Written critique of A001–A006 with jurisdiction/source limits | UNRESOLVED |
| 2 | Privacy-preserving record lifecycle | Monolithic + privacy reviewer TBD | Retention, redaction and deletion tested without sensitive public data | UNRESOLVED |
| 2 | Proposed partner sandbox | Participating organization TBD | Written scope, data permissions, named owner and frozen tests | NOT AUTHORIZED |
| 3 | Recognition research | Interdisciplinary reviewers TBD | Competing criteria and uncertainty documented; no automatic status award | OPEN QUESTION |

Release gate: local tests, source preservation, documentation-link checks and complete
claims boundaries. Independent review is a separate milestone and must not be implied
by a green CI run. Keep failed results and amendments traceable; do not silently change
a frozen test after observing the outcome.
