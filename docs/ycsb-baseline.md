# YCSB baseline for kv-app (end-to-end from a laptop)

## Setup
- Client: laptop (Europe/Kyiv timezone), YCSB 0.18.0-SNAPSHOT, custom binding `KvRestClient` (`bench/kvrest`), 8 threads, Java 11.
- Target: coordinator in `us-east-1` (`98.93.234.141`), two shards in private subnets, 10,000 records in `usertable`.
- Every operation travels over the internet from the laptop to AWS. This is an end-to-end baseline. Network time dominates it, so it does not measure the store alone.

## Results

### Load: 10,000 inserts (workload A load phase)
| Operation | Count | Average | p50 | p95 | p99 | Max | Status |
|---|---|---|---|---|---|---|---|
| INSERT | 10,000 | 173.8 ms | 173.3 ms | 205.1 ms | 570.9 ms | 1,909.8 ms | all `OK` |

Raw output: `docs/raw/ycsb-load-a.txt`.

### Workload A: 50% read, 50% update, 10,000 operations
| Operation | Count | Average | p50 | p95 | p99 | Max | Status |
|---|---|---|---|---|---|---|---|
| READ | 4,969 | 429.1 ms | 398.8 ms | 797.7 ms | 854.5 ms | 2,055.2 ms | all `OK` |
| UPDATE | 5,031 | 192.5 ms | 176.0 ms | 209.8 ms | 585.7 ms | 1,434.6 ms | all `OK` |

Raw output: `docs/raw/ycsb-run-a.txt`. Overall throughput: TBD (from the `[OVERALL]` line in that file).

### Workloads B and C
Not run yet. Workload E is skipped: the store has no range queries (ADR-006).

## Network and server context
| Measurement | Where | Result |
|---|---|---|
| GET `/tables/usertable/items/user1` (10 requests, median) | laptop, curl | 0.55 s |
| PUT `/tables/usertable/items/user1` (10 requests, median) | laptop, curl | 0.35 s |
| Shard A GET (5 requests) | inside the VPC, via SSM | 200 in 1.3 ms |
| Shard B GET, key on the other shard (5 requests) | inside the VPC, via SSM | 404 in 1.7 ms |
| Coordinator GET, including the forward to the shard (5 requests) | inside the VPC, via SSM | 200 in 2.3 ms |

## Reading the numbers
- Inside the VPC, a request takes about 2 ms, including the forward from the coordinator to the shard. The 170 to 430 ms in the tables above is the trip from the laptop to AWS.
- The laptop GET median (0.55 s) is higher than the laptop PUT median (0.35 s), but the server-side times are the same order. The cause of this gap is not established. It is not attributed to the store.
- These numbers are a baseline for this setup. They can't be compared with a store that runs inside the same region without network time, until a benchmark client runs inside the VPC.

## Reproduce
```powershell
$cp = (Get-Content cp.txt -Raw).Trim() + ";target\kvrest-binding-0.18.0-SNAPSHOT.jar"
java -cp $cp site.ycsb.Client -load -db site.ycsb.db.KvRestClient -P ..\workloads\workloada -p kvrest.url=http://98.93.234.141:8080 -p recordcount=10000 -threads 8 -s > ..\..\docs\raw\ycsb-load-a.txt 2>&1
java -cp $cp site.ycsb.Client -t -db site.ycsb.db.KvRestClient -P ..\workloads\workloada -p kvrest.url=http://98.93.234.141:8080 -p operationcount=10000 -threads 8 -s > ..\..\docs\raw\ycsb-run-a.txt 2>&1
```
Run from `YCSB\kvrest`. Replace the IP with the current `CoordinatorPublicIp` output.
