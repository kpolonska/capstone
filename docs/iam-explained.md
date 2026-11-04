# Tasks 2-3: read-only policy and role

**Policy (kv-readonly):** allows read actions on chosen services; an explicit Deny blocks writes, since a Deny always overrides an Allow.

**Role (kv-readonly-role):** carries the policy; its trust policy lets identities in my account assume it, getting temporary read-only access.

**What happened when deployed:** the policy was created (CREATE_COMPLETE); the role was refused: `iam:CreateRole` has no allowing policy (implicit deny, same as task 1). CloudFormation rolled everything back. Evidence in docs/raw/12-\*, 13-\*.
