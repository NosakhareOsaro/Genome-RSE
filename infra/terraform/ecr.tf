# Registry for the serving image in a real AWS deployment. The CD
# pipeline (.github/workflows/model-serving-cd.yml) currently pushes to
# GHCR instead, since that needs no extra account/secrets for this
# portfolio project -- this repository would push here too/instead.
resource "aws_ecr_repository" "model_serving" {
  name                 = var.project_name
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = var.tags
}

resource "aws_ecr_lifecycle_policy" "model_serving" {
  repository = aws_ecr_repository.model_serving.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Expire untagged images after 14 days"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 14
        }
        action = { type = "expire" }
      }
    ]
  })
}
