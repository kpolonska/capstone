# YCSB baseline for kv-app

## What is measured
Workloads A (50% read, 50% update), B (95% read) and C (100% read), against the deployed coordinator. Workload E (scans) is skipped: the store has no range queries (ADR-006).

## Files
- `kvrest/src/main/java/site/ycsb/db/KvRestClient.java`: YCSB binding for the REST API (ADR-004).

## Build (once)
1. Install Java 11 or later and Maven. Git Bash or WSL is needed to run the YCSB launcher script on Windows.
2. Clone YCSB: `git clone https://github.com/brianfrankcooper/YCSB.git`
3. Copy `bench/kvrest` into `YCSB/kvrest` and add a `pom.xml` based on another binding's pom in YCSB, pointing its `site.ycsb:core` dependency at the YCSB version you cloned. Confirm the module compiles before the first run.
4. From the YCSB folder: `mvn -pl site.ycsb:kvrest-binding -am clean package -DskipTests`

## Run
```bash
bin/ycsb load kvrest -P workloads/workloada -p kvrest.url=http://<COORD_IP>:8080 -p recordcount=10000 -threads 8
bin/ycsb run  kvrest -P workloads/workloada -p kvrest.url=http://<COORD_IP>:8080 -p operationcount=10000 -threads 8 -s > run-a.txt
```
Repeat `run` with `workloadb` and `workloadc`. Load once before each workload, or keep the table between runs.

## Results
Record throughput (ops/sec) and the average and p99 latency per operation from `-s` output in `docs/ycsb-baseline.md`.
