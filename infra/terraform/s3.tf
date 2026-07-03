# Bucket for model artifacts / MLflow artifact storage in a real
# multi-user deployment (see docs/adr/0003-*.md for why this service's
# demo tier uses local SQLite+filesystem instead). Bucket names must be
# globally unique, so this appends the account ID rather than hardcoding
# a name that would collide across AWS accounts.
data "aws_caller_identity" "current" {}

resource "aws_s3_bucket" "model_artifacts" {
  bucket = "${var.project_name}-artifacts-${data.aws_caller_identity.current.account_id}"
  tags   = var.tags
}

resource "aws_s3_bucket_versioning" "model_artifacts" {
  bucket = aws_s3_bucket.model_artifacts.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "model_artifacts" {
  bucket = aws_s3_bucket.model_artifacts.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "model_artifacts" {
  bucket                  = aws_s3_bucket.model_artifacts.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
