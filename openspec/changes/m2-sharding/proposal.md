# M2: Sharding the load

## Goal
Route key-value requests through a coordinator to two shards, so that data is split across two servers.

## Done when
- `PUT`, `GET`, `HEAD` and `DELETE` work through the coordinator on the deployed stack, verified with curl
- A measurement of 100,000 keys shows both shards holding a share close to 50%
- A push to `main` deploys both the infrastructure and the application
- The YCSB baseline is recorded in `docs/`