output "ecr_repository_url" {
  value = aws_ecr_repository.repo.repository_url
}

output "alb_dns_name" {
  value = aws_lb.alb.dns_name
}

output "api_gateway_invoke_url" {
  value = aws_apigatewayv2_api.http_api.api_endpoint
}
