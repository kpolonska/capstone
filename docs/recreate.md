# Task 8

|Step|Duration|
|-|-|
|Delete kv-network|33.6 s|
|Rebuild from infra/network.yaml|40.0 s|

New VPC ID: vpc-05995e9d75ad0b5af (old: vpc-0be5a59a15c55abf6). New IGW: igw-065393fc7caf2fbd4. IDs change on every rebuild, the structure does not.
Verification: public route table has 0.0.0.0/0 -> IGW, private has local only (docs/raw/17-routes-rebuilt.txt).

What broke on the first attempt: nothing. Possible failure points were avoided by design:

* No hardcoded AZ names (!GetAZs), so it works in any account.
* No other stack imports the exports (kv-app does not exist yet), so deletion was not blocked.
* Nothing was created by hand inside the VPC, so no DependencyViolation on delete.
* Session credentials were still valid (a risk to check first: ExpiredToken).

Impact for M2: anything stored in the old VPC is gone after a rebuild, and kv-app must be deleted before kv-network can be (export lock from ADR-002).
