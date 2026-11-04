# ADR-003: CIDR addressing scheme

The VPC must have public and private subnets. M2 needs a coordinator and 2 shards,
M3 needs 2 shards x 3 replicas spread over separate AZs, and M5
autoscaling adds more servers. Changing ranges later is painful: a changed subnet
is replaced, and the app stack importing it blocks the change. I use only us-east-1.

- VPC: 10.0.0.0/16 (65,536 addresses)
- 2 AZs, 4 subnets of /24 (251 usable addresses):

| Subnet | AZ | CIDR | Holds |
|---|---|---|---|
| Public A | a | 10.0.0.0/24 | coordinator |
| Public B | b | 10.0.1.0/24 | coordinator (spare) |
| Private A | a | 10.0.10.0/24 | shards, replicas |
| Private B | b | 10.0.11.0/24 | shards, replicas |

- Public ranges start at 10.0.0.x, private at 10.0.10.x, so the type is readable from the address.
- 10.0.2.x-10.0.9.x and 10.0.12.x+ stay unused for a future third AZ or new subnets.

## Alternatives rejected
- /24 VPC: only 256 addresses in total, no room for 4 subnets or growth.

## Consequences

\+ Plenty of room for M3 and M5 without renumbering.

\+ Subnet type visible from the IP address.

\- Wastes address space (just a little out of 65,536 is used).
