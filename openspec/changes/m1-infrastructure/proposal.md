# M1: Infrastructure setup

Build a reproducible network and permissions baseline for the key-value store.

## In scope
- VPC `kv-network`: 2 public and 2 private subnets across 2 AZs, with an Internet Gateway (CloudFormation, `infra/network.yaml`)
- Read-only IAM policy and role as IaC (`infra/iam-readonly.yaml`); the sandbox refuses to create it
- LabRole analysis, M2 quotas, M2 budget, teardown and rebuild test

## Out of scope
Application code, NAT Gateway, CI/CD.

## Done when
- Public subnets route 0.0.0.0/0 to the IGW; private subnets have only the local route (`docs/raw/17-routes-rebuilt.txt`)
- `kv-network` can be deleted and rebuilt from the template with no manual steps (`docs/recreate.md`)
