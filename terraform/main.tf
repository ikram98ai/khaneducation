terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  alias  = "us-east-1"
  region = "us-east-1"
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_availability_zones" "available" {
  state = "available"
}

################################################# Creating Aurora Serverless v2 Cluster with VPC and Networking #################################################

resource "aws_rds_cluster" "aurora" {
  cluster_identifier = "${var.function_name}-aurora-cluster"
  engine             = "aurora-postgresql"
  engine_mode        = "provisioned"
  engine_version     = "17.5"
  database_name      = var.db_name
  master_username    = var.db_username
  master_password    = var.db_password
  skip_final_snapshot = true
  storage_encrypted  = true

  serverlessv2_scaling_configuration {
    max_capacity             = 2
    min_capacity             = 0.0
    seconds_until_auto_pause = 600
  }
}

resource "aws_rds_cluster_instance" "aurora" {
  cluster_identifier = aws_rds_cluster.aurora.id
  instance_class     = "db.serverless"
  engine             = aws_rds_cluster.aurora.engine
  engine_version     = aws_rds_cluster.aurora.engine_version
}


######################################################### ECR Repository and Lambda Function #########################################################

# ECR Repository
resource "aws_ecr_repository" "khaneducation_repo" {
  name                 = var.ecr_repository_name
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = var.tags
}

# ECR Repository Policy
resource "aws_ecr_repository_policy" "khaneducation_repo_policy" {
  repository = aws_ecr_repository.khaneducation_repo.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowPull"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
      }
    ]
  })
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.function_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

# IAM Policy for Lambda (Updated with VPC and RDS permissions)
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.function_name}-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = aws_ecr_repository.khaneducation_repo.arn
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface",
          "ec2:AttachNetworkInterface",
          "ec2:DetachNetworkInterface"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "rds-db:connect"
        ]
        Resource = "arn:aws:rds-db:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:dbuser:${aws_rds_cluster.aurora.cluster_identifier}/${var.db_username}"
      }
    ]
  })
}

# Attach AWS managed policy for VPC access
resource "aws_iam_role_policy_attachment" "lambda_vpc_access" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# 🔧 Build & Push Docker Image
resource "null_resource" "build_and_push_image" {
  provisioner "local-exec" {
    command = <<EOT
      cd ..
      aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_ecr_repository.khaneducation_repo.repository_url}
      docker build -t ${var.ecr_repository_name} .
      docker tag ${var.ecr_repository_name}:latest ${aws_ecr_repository.khaneducation_repo.repository_url}:${var.image_tag}
      docker push ${aws_ecr_repository.khaneducation_repo.repository_url}:${var.image_tag}
    EOT
  }

  triggers = {
    image_tag = var.image_tag
  }

  depends_on = [aws_ecr_repository.khaneducation_repo]
}

# Lambda Function (Updated with VPC configuration and database environment variables)
resource "aws_lambda_function" "khaneducation_lambda" {
  function_name = var.function_name
  role         = aws_iam_role.lambda_role.arn
  package_type = "Image"
  image_uri    = "${aws_ecr_repository.khaneducation_repo.repository_url}:${var.image_tag}"
  timeout      = 30
  memory_size  = 512
  architectures = ["x86_64"]


  environment {
    variables = {
      GEMINI_API_KEY = var.gemini_api_key
      DB_HOSTNAME    = aws_rds_cluster.aurora.endpoint
      DB_PORT        = aws_rds_cluster.aurora.port
      DB_PASSWORD    = var.db_password
      DB_NAME        = var.db_name
      DB_USERNAME    = var.db_username

      DEBUG          = "False"
      SECRET_KEY     = var.secret_key
      ALGORITHM      = "HS256"
      ACCESS_TOKEN_EXPIRE_MINUTES = "30"
    }
  }

  depends_on = [
    aws_iam_role_policy.lambda_policy,
    aws_iam_role_policy_attachment.lambda_vpc_access,
    aws_cloudwatch_log_group.khaneducation_lambda_logs,
    null_resource.build_and_push_image,
    aws_ecr_repository_policy.khaneducation_repo_policy,
    aws_rds_cluster_instance.aurora,
  ]

  tags = var.tags
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "khaneducation_lambda_logs" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = 14
  tags              = var.tags
}

############################################################# API GATEWAY CONFIGURATION #############################################################

# API Gateway (HTTP API)
resource "aws_apigatewayv2_api" "khaneducation_api" {
  name          = "${var.function_name}-api"
  protocol_type = "HTTP"
  tags          = var.tags

   cors_configuration {
    allow_credentials = false
    expose_headers    = ["*"]
    allow_headers     = ["*"]
    allow_methods     = ["*"]
    allow_origins     = ["*"]
    max_age          = 86400
  }
}

# API Gateway Integration with Lambda
resource "aws_apigatewayv2_integration" "khaneducation_integration" {
  api_id             = aws_apigatewayv2_api.khaneducation_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.khaneducation_lambda.arn
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "proxy_route" {
  api_id    = aws_apigatewayv2_api.khaneducation_api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.khaneducation_integration.id}"
}

# OPTIONS method for CORS preflight
resource "aws_apigatewayv2_route" "options_route" {
  api_id    = aws_apigatewayv2_api.khaneducation_api.id
  route_key = "OPTIONS /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.khaneducation_integration.id}"
}

# API Gateway Stage
resource "aws_apigatewayv2_stage" "default_stage" {
  api_id      = aws_apigatewayv2_api.khaneducation_api.id
  name        = "$default"
  auto_deploy = true
}

# Lambda Permission for API Gateway
resource "aws_lambda_permission" "api_gw_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.khaneducation_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.khaneducation_api.execution_arn}/*/*"
}
