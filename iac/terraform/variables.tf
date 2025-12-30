variable "project_name" {
  type    = string
  default = "egain-knowledge"
}

variable "aws_region" {
  type    = string
  default = "us-west-2"
}

variable "image_tag" {
  type    = string
  default = "latest"
}

variable "desired_count" {
  type    = number
  default = 2
}

variable "task_cpu" {
  type    = number
  default = 512
}

variable "task_memory" {
  type    = number
  default = 1024
}

variable "api_keys_json" {
  type        = string
  description = "JSON map of tenantId -> apiKey"
  default     = "{"tenantA":"keyA"}"
}

variable "db_path" {
  type        = string
  description = "SQLite DB path inside container"
  default     = "egain_knowledge.db"
}

variable "rds_username" {
  type    = string
  default = "egainadmin"
}

variable "rds_password" {
  type      = string
  sensitive = true
}
