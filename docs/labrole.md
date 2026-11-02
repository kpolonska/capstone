# LabRole analysis

**Identity:** CLI/console runs as `voclabs` (account 211125386643), restricted further by Pvoclabs1/2. LabRole is the role given to services (EC2, EKS).

**Policies:** 4 AWS-managed (SSM, EKS cluster, EKS worker, ECR read-only) + 3 Academy custom (VocLabPolicy1–3, unreadable: explicit deny by Pvoclabs1). No inline policies.

| Action | Result | Method |
|---|---|---|
| ec2:CreateVpc, RunInstances (t3.micro) | Allowed | Simulator + dry-run |
| s3, dynamodb, lambda, cloudformation create | Allowed | Simulator |
| RunInstances m5.4xlarge | Explicit deny (Pvoclabs2) | Dry-run |
| iam:CreateUser, CreateRole | Implicit deny | Simulator + CLI |
| Reading VocLab policies / voclabs role | Explicit deny (Pvoclabs1/2) | CLI |
| Any action outside us-east-1/us-west-2 | Implicit deny | CLI --region |

**Conclusion:** I can build infra (small instances, us-east-1) but not IAM identities, so tasks 2–3 are IaC-only.

**Method:** CLI policy reads, dry-run/create probes, Policy Simulator. Raw output in `docs/raw/`.