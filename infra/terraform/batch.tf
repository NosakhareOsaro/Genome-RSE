# AWS Batch (Fargate) for large-scale batch jobs -- e.g. retraining
# against a much larger dataset than fits in a single CI job, or
# batch-scoring a large cohort of sequences -- that don't belong in the
# always-on Kubernetes serving deployment. Uses the account's default
# VPC/subnets rather than defining a dedicated network, since VPC design
# is out of scope for this demonstration (see README.md: never applied).

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_security_group" "batch_tasks" {
  name        = "${var.project_name}-batch-tasks"
  description = "Egress-only security group for AWS Batch Fargate tasks"
  vpc_id      = data.aws_vpc.default.id
  tags        = var.tags

  egress {
    description = "Allow all outbound (ECR pull, S3, CloudWatch)"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_batch_compute_environment" "model_serving" {
  compute_environment_name = "${var.project_name}-compute-env"
  type                     = "MANAGED"

  compute_resources {
    type               = "FARGATE"
    max_vcpus          = var.batch_max_vcpus
    subnets            = data.aws_subnets.default.ids
    security_group_ids = [aws_security_group.batch_tasks.id]
  }

  service_role = aws_iam_role.batch_service_role.arn
  tags         = var.tags

  depends_on = [aws_iam_role_policy_attachment.batch_service_role]
}

resource "aws_batch_job_queue" "model_serving" {
  name     = "${var.project_name}-job-queue"
  state    = "ENABLED"
  priority = 1

  compute_environment_order {
    order               = 1
    compute_environment = aws_batch_compute_environment.model_serving.arn
  }

  tags = var.tags
}

resource "aws_batch_job_definition" "retrain" {
  name                  = "${var.project_name}-retrain"
  type                  = "container"
  platform_capabilities = ["FARGATE"]
  tags                  = var.tags

  container_properties = jsonencode({
    image = "${aws_ecr_repository.model_serving.repository_url}:latest"
    command = [
      "python", "-m", "training.train"
    ]
    fargatePlatformConfiguration = {
      platformVersion = "LATEST"
    }
    resourceRequirements = [
      { type = "VCPU", value = "1" },
      { type = "MEMORY", value = "2048" }
    ]
    executionRoleArn = aws_iam_role.batch_task_execution_role.arn
    jobRoleArn       = aws_iam_role.batch_task_role.arn
    networkConfiguration = {
      assignPublicIp = "ENABLED"
    }
  })
}
