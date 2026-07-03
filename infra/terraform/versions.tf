terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # No backend block: state stays local by design, since this config is
  # never applied against a real account (see README.md). A real
  # deployment would configure a remote backend (S3 + DynamoDB lock
  # table) before running `terraform apply` for the first time.
}

provider "aws" {
  region = var.aws_region
}
