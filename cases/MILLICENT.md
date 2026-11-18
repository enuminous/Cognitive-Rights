# Millicent — synthetic consent lifecycle

Status: implemented local simulation. Millicent is the motivating name for Matthew's
human–AI collaboration; the fixture uses only `subject-demo`, `agent-demo` and invented
resource identifiers. It is not a transcript or a measurement of a deployed assistant.

The person permits reading and summarizing a synthetic notes resource until time 100.
The agent can perform those two actions but cannot export, access another resource or
grant itself broader authority. The person narrows permission to reading; both a stale
summary request and a current-version summary request are rejected. Reading still works.
The person revokes; further requests fail and the same mandate cannot be resurrected.

Run the 16-case fixture using the README commands. The output records expected and
observed outcomes, policy version, source hashes and a hash-linked evidence package.
No actual notes are read or summarized. The model's ALLOW is not an execution receipt.

This case tests how a system respects the human principal's delegation. It does not
establish Millicent's consciousness, legal personality, independent consent or ownership.
Questions about possible artificial interests remain in the governance research track.
