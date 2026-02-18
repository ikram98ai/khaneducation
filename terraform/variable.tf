variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "api_domain_name" {
  description = "API domain name (e.g., api.yourdomain.ai)"
  type        = string
  default     = "api.khaneducation.ai"

}

variable "root_domain_name" {
  description = "Root domain name (e.g., yourdomain.ai)"
  type        = string
  default     = "khaneducation.ai"

}

variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "khaneducation-app"
}

variable "ecr_repository_name" {
  description = "Name of the ECR repository"
  type        = string
  default     = "khaneducation-app"
}

variable "image_tag" {
  description = "Docker image tag"
  type        = string
  default     = "latest"
}

variable "stage_name" {
  description = "API Gateway stage name"
  type        = string
  default     = "prod"
}


variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default = {
    Environment = "production"
    Project     = "khaneducation-app"
    ManagedBy   = "terraform"
  }
}

variable "secret_key" {
  description = "secret key for the application"
  type        = string
  sensitive = true   
} 

variable "gemini_api_key" {
  description = "Gemini API key"
  type        = string
  sensitive   = true
}

variable "cors_origins" {
  description = "CORS allowed origins"
  type        = list(string)
  default     = null
}
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "khaneducation.ai"
}