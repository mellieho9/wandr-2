output "vpc_connector_name" {
  description = "Name of the VPC Access Connector"
  value       = google_vpc_access_connector.redis_connector.name
}

output "vpc_connector_id" {
  description = "Full ID of the VPC Access Connector"
  value       = google_vpc_access_connector.redis_connector.id
}

output "redis_host" {
  description = "Redis instance host IP"
  value       = var.create_redis ? google_redis_instance.main[0].host : null
}

output "redis_port" {
  description = "Redis instance port"
  value       = var.create_redis ? google_redis_instance.main[0].port : null
}

output "redis_connection_string" {
  description = "Redis connection string for application use"
  value       = var.create_redis ? "${google_redis_instance.main[0].host}:${google_redis_instance.main[0].port}" : null
}

output "cloud_run_vpc_connector_config" {
  description = "VPC connector configuration for Cloud Run"
  value = {
    vpc_connector = google_vpc_access_connector.redis_connector.name
    vpc_egress    = "private-ranges-only"
  }
}
