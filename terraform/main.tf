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
  region = var.aws_region
}

# Provider for ACM certificate (must be in us-east-1 for CloudFront)
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Route 53 Hosted Zone
resource "aws_route53_zone" "main" {
  name = var.domain_name

  tags = {
    Name        = var.domain_name
    Environment = var.environment
  }
}

# S3 Bucket for website hosting
resource "aws_s3_bucket" "website" {
  bucket = "${var.domain_name}-website-${random_string.bucket_suffix.result}"

  tags = {
    Name        = "${var.domain_name}-website"
    Environment = var.environment
  }
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# S3 Bucket Public Access Block
resource "aws_s3_bucket_public_access_block" "website" {
  bucket = aws_s3_bucket.website.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Bucket Policy for CloudFront
resource "aws_s3_bucket_policy" "website" {
  bucket = aws_s3_bucket.website.id
  depends_on = [aws_s3_bucket_public_access_block.website]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowCloudFrontServicePrincipal"
        Effect    = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.website.arn}/*"
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = aws_cloudfront_distribution.website.arn
          }
        }
      }
    ]
  })
}

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

# IAM Policy for Lambda
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
          "dynamodb:*"
        ]
        Resource = [
          "arn:aws:dynamodb:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:table/khaneducation_*",
          "arn:aws:dynamodb:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:table/khaneducation_*/index/*"
        ]
      }
    ]
  })
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
      DEBUG          = "False"
      SECRET_KEY     = var.secret_key
      ALGORITHM      = "HS256"
      ACCESS_TOKEN_EXPIRE_MINUTES = "30"
    }
  }
  depends_on = [
    aws_iam_role_policy.lambda_policy,
    aws_cloudwatch_log_group.khaneducation_lambda_logs,
    null_resource.build_and_push_image,
    aws_ecr_repository_policy.khaneducation_repo_policy,
  ]
  tags = var.tags
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "khaneducation_lambda_logs" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = 14
  tags              = var.tags
}

# 🔧 Build & Deploy Frontend
resource "null_resource" "web_build_and_deploy" {
  provisioner "local-exec" {
    command = <<EOT
      cd ../web
      npm install
      VITE_API_URL=https://api.${var.domain_name} npm run build
      aws s3 sync dist/ s3://${aws_s3_bucket.website.id} --delete
      aws cloudfront create-invalidation --distribution-id ${aws_cloudfront_distribution.website.id} --paths "/*"
    EOT
  }
  triggers = {
    # This will trigger on every apply if we don't have a good hash, 
    # but we can use the backend image tag as a proxy for a new deployment
    deployment_id = var.image_tag
  }
  depends_on = [aws_s3_bucket.website, aws_cloudfront_distribution.website]
}

# ACM Certificates
resource "aws_acm_certificate" "website" {
  provider          = aws.us_east_1
  domain_name       = var.domain_name
  validation_method = "DNS"

  subject_alternative_names = [
    "www.${var.domain_name}"
  ]

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name        = var.domain_name
    Environment = var.environment
  }
}

resource "aws_acm_certificate" "api_certificate" {
  domain_name       = "api.${var.domain_name}"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = merge(var.tags, {
    Name = "api.${var.domain_name}"
  })
}

# Route 53 records for ACM certificate validation (website)
resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.website.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = aws_route53_zone.main.zone_id
}

# Route 53 records for ACM certificate validation (API)
resource "aws_route53_record" "api_cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.api_certificate.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = aws_route53_zone.main.zone_id
}

# ACM certificate validations
resource "aws_acm_certificate_validation" "website" {
  provider                = aws.us_east_1
  certificate_arn         = aws_acm_certificate.website.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]

  timeouts {
    create = "15m"
  }
}

resource "aws_acm_certificate_validation" "api_certificate" {
  certificate_arn         = aws_acm_certificate.api_certificate.arn
  validation_record_fqdns = [for record in aws_route53_record.api_cert_validation : record.fqdn]

  timeouts {
    create = "15m"
  }
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
    allow_origins     = var.cors_origins != null ? var.cors_origins : ["https://${var.domain_name}", "https://www.${var.domain_name}"]
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

############################################################# CUSTOM DOMAIN CONFIGURATION #############################################################

# API Gateway Custom Domain
resource "aws_apigatewayv2_domain_name" "api_domain" {
  domain_name = "api.${var.domain_name}"

  domain_name_configuration {
    certificate_arn = aws_acm_certificate_validation.api_certificate.certificate_arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }

  depends_on = [aws_acm_certificate_validation.api_certificate]
  tags       = var.tags
}

# API Gateway Domain Mapping
resource "aws_apigatewayv2_api_mapping" "api_mapping" {
  api_id      = aws_apigatewayv2_api.khaneducation_api.id
  domain_name = aws_apigatewayv2_domain_name.api_domain.id
  stage       = aws_apigatewayv2_stage.default_stage.id
}

# Route 53 A record for API subdomain
resource "aws_route53_record" "api_record" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.${var.domain_name}"
  type    = "A"

  alias {
    name                   = aws_apigatewayv2_domain_name.api_domain.domain_name_configuration[0].target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.api_domain.domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = false
  }
}

############################################################# CLOUDFRONT DISTRIBUTION #############################################################

# CloudFront Origin Access Control
resource "aws_cloudfront_origin_access_control" "website" {
  name                              = "${var.domain_name}-oac"
  description                       = "OAC for ${var.domain_name}"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "website" {
  origin {
    domain_name              = aws_s3_bucket.website.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.website.id
    origin_id                = "S3-${aws_s3_bucket.website.id}"
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "${var.domain_name} website"
  default_root_object = "index.html"

  aliases = [var.domain_name, "www.${var.domain_name}"]

  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.website.id}"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
    compress               = true
  }

  # Cache behavior for static assets
  ordered_cache_behavior {
    path_pattern     = "/assets/*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "S3-${aws_s3_bucket.website.id}"

    forwarded_values {
      query_string = false
      headers      = ["Origin"]
      cookies {
        forward = "none"
      }
    }

    min_ttl                = 0
    default_ttl            = 86400
    max_ttl                = 31536000
    compress               = true
    viewer_protocol_policy = "redirect-to-https"
  }

  price_class = "PriceClass_100"

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate_validation.website.certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  custom_error_response {
    error_code         = 403
    response_code      = 200
    response_page_path = "/index.html"
  }

  tags = {
    Name        = "${var.domain_name}-cloudfront"
    Environment = var.environment
  }
}

# Route 53 A record for apex domain
resource "aws_route53_record" "website_a" {
  zone_id = aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.website.domain_name
    zone_id                = aws_cloudfront_distribution.website.hosted_zone_id
    evaluate_target_health = false
  }
}

# Route 53 A record for www subdomain
resource "aws_route53_record" "website_www" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "www.${var.domain_name}"
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.website.domain_name
    zone_id                = aws_cloudfront_distribution.website.hosted_zone_id
    evaluate_target_health = false
  }
}

############################################################# OUTPUTS #############################################################

# Frontend outputs
output "nameservers" {
  description = "Route 53 nameservers to configure in domain registrar"
  value       = aws_route53_zone.main.name_servers
}

output "s3_bucket_name" {
  description = "S3 bucket name for website hosting"
  value       = aws_s3_bucket.website.id
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = aws_cloudfront_distribution.website.id
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.website.domain_name
}

output "website_url" {
  description = "Website URL"
  value       = "https://${var.domain_name}"
}

# Backend outputs
output "api_gateway_url" {
  description = "API Gateway URL"
  value       = aws_apigatewayv2_api.khaneducation_api.api_endpoint
}

output "custom_api_url" {
  description = "Custom API URL"
  value       = "https://api.${var.domain_name}"
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.khaneducation_lambda.function_name
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.khaneducation_repo.repository_url
}
