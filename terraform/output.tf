# Outputs
output "api_gateway_url" {
  description = "API Gateway URL"
  value       = aws_apigatewayv2_api.khaneducation_api.api_endpoint
}

output "lambda_function_arn" {
  description = "Lambda function ARN"
  value       = aws_lambda_function.khaneducation_lambda.arn
}