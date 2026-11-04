# ADR-001: IaC tool

AWS CloudFormation because it is the simplest to use inside the sandbox setting and also native to AWS.

* Why not Terraform: needs a remote state file to track what is already created. CloudFormation stores stack and resource IDs. ALso learner lab credentials change every session, which is fine for M1. But that would become a problem later, since M2 requires CI/CD pipeline.
* Why not CDK: would basically be just an additional layer on top of cloudformation and just extra work. Also does not work inside the sandbox. Needs to create IAM users, which is forbidden for LabRole.

## Consequences

\+ Nothing to install, no state to manage, native change sets and drift detection.

− Locked to AWS: moving to another cloud means rewriting templates.

− Verbose YAML: repeated blocks (4 subnets) and no simple loops, more room for copy-paste errors.
