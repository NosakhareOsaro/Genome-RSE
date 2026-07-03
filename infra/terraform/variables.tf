variable "aws_region" {
  description = "AWS region for all resources."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Short name used to prefix/tag all resources."
  type        = string
  default     = "genomerse-model-serving"
}

variable "environment" {
  description = "Deployment environment tag (e.g. dev, staging, prod)."
  type        = string
  default     = "dev"
}

variable "batch_max_vcpus" {
  description = "Maximum vCPUs for the Fargate Batch compute environment."
  type        = number
  default     = 16
}

variable "tags" {
  description = "Common tags applied to every resource."
  type        = map(string)
  default = {
    Project   = "GenomeRSE"
    ManagedBy = "Terraform"
  }
}
