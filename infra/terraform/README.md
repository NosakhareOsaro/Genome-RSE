# infra/terraform

Terraform configuration for the AWS infrastructure a real (non-portfolio)
deployment of `services/model-serving` would run on: an ECR repository
for the serving image, an S3 bucket for model artifacts, least-privilege
IAM roles, and an AWS Batch (Fargate) compute environment/queue/job
definition for large-scale retraining or batch-inference jobs that don't
belong in the always-on Kubernetes deployment.

> ## ⚠️ Infrastructure as code only -- nothing here has been applied
>
> This repository contains **no AWS credentials, no remote state
> backend, and no CI workflow that runs `terraform apply`.** These files
> exist to demonstrate IaC practice (resource design, least-privilege
> IAM, `terraform validate`/`fmt` as a real, run CI gate), not to
> provision real infrastructure. The actual demonstration deployment
> target for this project is the local `kind` cluster in `infra/k8s` /
> `infra/helm`, verified for real; nothing under `infra/terraform` has
> ever been `apply`'d against a live AWS account.

## What's here

- `versions.tf` -- provider/version constraints. No `backend` block:
  state stays local by design, since this is never actually applied. A
  real deployment would add a remote backend (S3 + a DynamoDB lock
  table) before its first real `apply`.
- `variables.tf` / `outputs.tf`
- `s3.tf` -- versioned, encrypted, public-access-blocked bucket for
  model artifacts / a real MLflow artifact store (see
  `docs/adr/0003-*.md` for why the demo tier uses local SQLite instead).
- `ecr.tf` -- immutable-tag repository with scan-on-push, for the
  serving image (the CD pipeline currently pushes to GHCR instead --
  see `.github/workflows/model-serving-cd.yml` -- since that needs no
  extra AWS account for this portfolio project).
- `iam.tf` -- a Batch service role and separate Fargate task
  execution/task roles, the task role scoped to `s3:GetObject`/
  `s3:PutObject`/`s3:ListBucket` on exactly this project's bucket, not `*`.
- `batch.tf` -- a Fargate `MANAGED` compute environment, job queue, and
  a `retrain` job definition referencing the ECR image. Uses the
  account's default VPC/subnets rather than defining dedicated
  networking, since VPC design is out of scope here.

## Verified (validate-only, as documented above)

```bash
terraform fmt -check -diff   # passes
terraform init -backend=false
terraform validate            # "Success! The configuration is valid."
```

No `terraform plan` or `terraform apply` was run against a real AWS
account -- `plan`/`apply` would need real credentials this repo
intentionally doesn't have.
