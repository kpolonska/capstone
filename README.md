# kv-store

A light key-value store: a coordinator routes each request to one of two shards using a consistent-hash ring. Built in five milestones. This README covers M1 (infrastructure) and M2 (sharding).

## Prerequisites
- AWS Academy Learner Lab session, region `us-east-1`. Put the session credentials in `%USERPROFILE%\.aws\credentials`. They expire after about 4 hours, so copy fresh ones each session.
- AWS CLI v2, Git, Python 3 (for the tests).

## Repository layout

| Path | Contents |
|---|---|
| `infra/network.yaml` | VPC, two public and two private subnets, route tables, S3 gateway endpoint (M1, M2) |
| `infra/app.yaml` | Coordinator (public subnet) and two shards (private subnets) (M2) |
| `infra/iam-readonly.yaml` | Read-only IAM policy and role (M1). Its role creation is denied in the Learner Lab, so it is kept for review only |
| `app/kvapp/` | Application code: ring, shard server, coordinator server, entry point (M2) |
| `app/tests/` | Unit and end-to-end tests |
| `adr/` | Architecture decision records, one per decision |
| `openspec/changes/` | Proposals written per milestone |
| `docs/` | Cost, quotas, AI critiques, evidence (`docs/raw/` has command output) |

## Deploy (per session)

1. Network (skip if `kv-network` already exists):
   ```powershell
   aws cloudformation deploy --template-file infra\network.yaml --stack-name kv-network
   ```
   Creates the VPC and subnets. Exports the IDs that `app.yaml` imports.

2. Build and upload the application code:
   ```powershell
   cd app
   python -m zipfile -c app.zip kvapp
   aws s3 cp app.zip s3://kv-code-211125386643/app.zip
   cd ..
   ```
   Packages the `kvapp` package and uploads it to the code bucket. Each instance downloads the zip on first boot.

3. Application stack:
   ```powershell
   aws cloudformation deploy --template-file infra\app.yaml --stack-name kv-app
   aws cloudformation describe-stacks --stack-name kv-app --query "Stacks[0].Outputs" --output table
   ```
   Creates the coordinator and two shards. The outputs give the coordinator's public IP and the shards' private IPs.

4. Register the shards with the coordinator (replace the addresses with the outputs):
   ```powershell
   '{"id":"a","url":"http://<SHARD_A_IP>:8081"}' | Set-Content -Encoding ascii shard-a.json
   curl.exe -i -X POST http://<COORD_IP>:8080/shards -H "Content-Type: application/json" --data-binary "@shard-a.json"
   ```
   Repeat with `"id":"b"` for shard B. Registration lives in memory, so repeat it after any restart.

## Verify

```powershell
curl.exe http://<COORD_IP>:8080/health
curl.exe -i -X PUT http://<COORD_IP>:8080/tables/demo
curl.exe -i -X PUT http://<COORD_IP>:8080/tables/demo/items/hello -d "world"
curl.exe -i http://<COORD_IP>:8080/tables/demo/items/hello
```
The health check lists the registered shards. The last command returns `200 OK` and `world`.

## Tests

```powershell
cd app
python -m unittest -v tests.test_kvapp
```
Runs the hash reference vectors, the ring balance and movement checks, and end-to-end CRUD on localhost with two in-process shards.

## Tear down

```powershell
aws cloudformation delete-stack --stack-name kv-app
aws cloudformation wait stack-delete-complete --stack-name kv-app
aws cloudformation delete-stack --stack-name kv-network
```
Delete `kv-app` first, because it imports values from `kv-network`. Do this at the end of every session to protect the credit.

## What changed in M2
- `app/kvapp/`: pure-Python xxHash64, a 100-virtual-node consistent-hash ring, the shard server (port 8081), and the coordinator (port 8080) with shard registration.
- `infra/app.yaml`: three instances, security groups (coordinator open on 8080, shards only from the coordinator), and a systemd service that starts the app on boot.
- `infra/network.yaml`: S3 gateway endpoint on the private route table, so the private instances reach S3 without internet access.
- ADR-004 to ADR-007 and the M2 proposal.

## Known limits
The API has no authentication, data and routing live only in memory, and adding a shard does not move existing keys. Each limit and its planned fix is listed in `docs/ai-critique.md`.
