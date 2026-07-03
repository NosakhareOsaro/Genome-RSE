# Least-privilege roles for AWS Batch (Fargate) jobs -- e.g. a
# large-scale retraining or batch-inference job that pulls the ECR image
# and reads/writes model artifacts in S3. Scoped to exactly this
# project's bucket and repository, not "*".

resource "aws_iam_role" "batch_service_role" {
  name = "${var.project_name}-batch-service-role"
  tags = var.tags

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "batch.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "batch_service_role" {
  role       = aws_iam_role.batch_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}

resource "aws_iam_role" "batch_task_execution_role" {
  name = "${var.project_name}-batch-task-execution-role"
  tags = var.tags

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

# Covers pulling the image from ECR and writing container logs to
# CloudWatch -- the standard AWS-managed policy for Fargate task
# execution (not the task's own application permissions, see below).
resource "aws_iam_role_policy_attachment" "batch_task_execution_role" {
  role       = aws_iam_role.batch_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "batch_task_role" {
  name = "${var.project_name}-batch-task-role"
  tags = var.tags

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "batch_task_s3_access" {
  name = "${var.project_name}-batch-task-s3-access"
  role = aws_iam_role.batch_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ListArtifactBucket"
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = [aws_s3_bucket.model_artifacts.arn]
      },
      {
        Sid      = "ReadWriteArtifactObjects"
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject"]
        Resource = ["${aws_s3_bucket.model_artifacts.arn}/*"]
      }
    ]
  })
}
