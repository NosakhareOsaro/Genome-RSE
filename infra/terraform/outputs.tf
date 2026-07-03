output "ecr_repository_url" {
  description = "ECR repository URL for the model-serving image."
  value       = aws_ecr_repository.model_serving.repository_url
}

output "model_artifacts_bucket" {
  description = "S3 bucket name for model artifacts / MLflow artifact storage."
  value       = aws_s3_bucket.model_artifacts.bucket
}

output "batch_job_queue_arn" {
  description = "AWS Batch job queue ARN for retraining/batch-inference jobs."
  value       = aws_batch_job_queue.model_serving.arn
}

output "batch_retrain_job_definition_arn" {
  description = "AWS Batch job definition ARN for the retraining job."
  value       = aws_batch_job_definition.retrain.arn
}
