# Service quotas for M2

|Quota|Limit|M2 needs|M3 needs (7 servers)|
|-|-|-|-|
|On-Demand Standard vCPUs (T family)|256|6|14|
|VPCs per region|5 (2 used: default + kv-vpc)|1|1|
|Internet gateways per region|5|1|1|
|Subnets per VPC|200|4|4|
|Instance types / count (Learner Lab Readme)|...|3x t3.micro|7x t3.micro|

Conclusion: AWS quotas are not the bottleneck. The limits come from the sandbox (explicit deny on large instance types, Pvoclabs2) and the credit ($50).
Files: docs/raw/15-quota-ec2.txt, 16-quota-vpc.txt.
