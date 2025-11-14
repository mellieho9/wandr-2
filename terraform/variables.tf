variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud region"
  type        = string
  default     = "us-central1"
}

variable "vpc_connector_name" {
  description = "Name of the VPC Access Connector"
  type        = string
  default     = "redis-connector"
}

variable "vpc_network" {
  description = "VPC network to use"
  type        = string
  default     = "default"
}

variable "vpc_connector_range" {
  description = "IP CIDR range for VPC connector"
  type        = string
  default     = "10.8.0.0/28"
}

variable "create_redis" {
  description = "Whether to create the Redis instance"
  type        = bool
  default     = true
}

variable "redis_instance_name" {
  description = "Name of the Redis instance"
  type        = string
  default     = "social-video-redis"
}

variable "redis_tier" {
  description = "Redis tier (BASIC or STANDARD_HA)"
  type        = string
  default     = "BASIC"

  validation {
    condition     = contains(["BASIC", "STANDARD_HA"], var.redis_tier)
    error_message = "Redis tier must be either BASIC or STANDARD_HA"
  }
}

variable "redis_size_gb" {
  description = "Redis memory size in GB"
  type        = number
  default     = 1

  validation {
    condition     = var.redis_size_gb >= 1 && var.redis_size_gb <= 300
    error_message = "Redis size must be between 1 and 300 GB"
  }
}
