# Security and research limits

This is an offline prototype. It authenticates no users, executes no tools and protects
no live resource. Do not place it directly in front of a production account or represent
it as a hardened authorization server.

Report non-sensitive reproducible bugs in repository issues. For secrets or exploitable
issues affecting a real service, use that service's private security channel; do not
post credentials or personal data here. No private reporting endpoint is established
for this new repository yet.

Threats explicitly outside v0.1: malicious host or administrator, identity impersonation,
key compromise, clock rollback outside the engine, concurrent check/use races, in-flight
tool cancellation, distributed caches, data already exported, forged outside witnesses
and denial of service from unbounded input sizes. Use trusted small local fixtures.

Hash chains reveal changes only relative to trusted evidence. They cannot prevent a
host from rewriting the entire history and replacing an unauthenticated root digest.
