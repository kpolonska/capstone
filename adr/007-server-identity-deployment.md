# ADR-007: Server identity and deployment



## Context

The shards are in private subnets, so they cannot reach the internet to download code (ADR-006 and M1 have no NAT Gateway). M2 requires a CI/CD pipeline. The sandbox denies iam:CreateRole, so no new roles can be created. Sandbox checks are in docs/raw/20-m2-sandbox.txt.

## Decision

* Servers run as LabRole through LabInstanceProfile, so no access keys are stored on any server.
* Application code is packaged as a zip, uploaded to the bucket kv-code-211125386643, and downloaded by the servers through the S3 gateway endpoint.
* CI/CD uses AWS credentials stored as GitHub secrets, refreshed at the start of each lab session.

## Alternatives rejected

* Access keys in files on the servers: long-lived secrets that can leak.
* OIDC (GitHub proves its identity to AWS): the standard solution, but it needs iam:CreateRole, which the sandbox denies.
* Installing packages from the internet at boot: needs a NAT Gateway (about $33 a month).

