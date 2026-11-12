# ADR-006: Partition key strategy

# 

# Context

Items must be placed on shards. M2's compound key (partition key plus sort key) is optional. M3 replication and M5 rebalancing will move data by partition.

## Decision

* Partition key = table name + "/" + item key, then hashed. user42 in table users is hashed as the string users/user42.

## Alternatives rejected

* Hash the item key alone: the same key in two tables would become the same item.
* Partition by table: a busy table overloads one shard, and scaling does not help.
* Range partitioning: sequential keys hit one shard; needs extra rebalancing logic.

