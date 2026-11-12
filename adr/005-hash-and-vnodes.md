# ADR-005: Hash function and virtual nodes

## Context
Needs to be deterministic across processes. Keys must spread evenly across servers and fast.

## Decision
- Hash: xxHash64 - gives the same hashes for the same keys, non-creptographic, which means faster. Tiny change in the input prodeces very different output.
- Virtual nodes: 100 per shard. The ring is a sorted list of (point, shard). A key goes to the first point at or after its hash, wrapping to the start of the list. Lookup uses binary search.

## Alternatives rejected
- Python's built-in hash(): randomized per process for strings, so we would get different hashes upon restart.
- hash(key) % N: adding shards remaps almost every key.
- MD5 or SHA: uniform, but slower, and cryptographic strength is not needed.
