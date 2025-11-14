terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# VPC Access Connector for Cloud Run to access Redis
resource "google_vpc_access_connector" "redis_connector" {
  name          = var.vpc_connector_name
  region        = var.region
  network       = var.vpc_network
  ip_cidr_range = var.vpc_connector_range

  # This is what's costing $1/day even when not in use
  # Comment out this entire resource block if you don't need it
}

# Redis Instance (Memorystore)
resource "google_redis_instance" "main" {
  count = var.create_redis ? 1 : 0

  name               = var.redis_instance_name
  tier               = var.redis_tier
  memory_size_gb     = var.redis_size_gb
  region             = var.region
  redis_version      = "REDIS_7_0"
  authorized_network = var.vpc_network

  display_name = "Social Video Redis"

  # Optional: Configure maintenance window
  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 2
        minutes = 0
      }
    }
  }
}
