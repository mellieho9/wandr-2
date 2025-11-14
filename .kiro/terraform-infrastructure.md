# Terraform Infrastructure for Wandr

This document describes the Terraform configuration in `/terraform` for managing Google Cloud infrastructure.

## Resources Managed

- **VPC Access Connector**: Allows Cloud Run to connect to Redis (~$0.30-0.40/hour = ~$7-9/day)
- **Redis Instance (Memorystore)**: Optional Redis instance for OAuth state management

## Prerequisites

1. Install Terraform: https://developer.hashicorp.com/terraform/downloads
2. Install gcloud CLI: https://cloud.google.com/sdk/docs/install
3. Authenticate with GCP:
   ```bash
   gcloud auth application-default login
   ```

## Setup

1. Copy the example variables file:
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars
   ```

2. Edit `terraform.tfvars` and set your `project_id`:
   ```hcl
   project_id = "your-actual-project-id"
   ```

3. Initialize Terraform:
   ```bash
   terraform init
   ```

## Usage

### Create Infrastructure

```bash
# Preview what will be created
terraform plan

# Create the resources
terraform apply
```

After applying, Terraform will output connection details:
- Redis host and port
- VPC connector name
- Connection string for your application

### Destroy Infrastructure (Stop Charges!)

```bash
# Preview what will be destroyed
terraform plan -destroy

# Destroy all resources
terraform destroy
```

This will delete both the VPC connector and Redis instance, **stopping all charges**.

### Partial Destroy (Only Delete VPC Connector)

If you want to keep Redis but delete the VPC connector:

```bash
# Delete only the VPC connector
terraform destroy -target=google_vpc_access_connector.redis_connector
```

Or edit `terraform.tfvars` to disable Redis:
```hcl
create_redis = false
```

Then run `terraform apply` to remove it.

## Cost Breakdown

- **VPC Access Connector**: ~$0.30-0.40/hour (~$7-9/day) - **ALWAYS CHARGES EVEN WHEN IDLE**
- **Redis BASIC (1GB)**: ~$0.049/GB/hour (~$35/month)
- **Redis STANDARD_HA (1GB)**: ~$0.139/GB/hour (~$100/month)

## Importing Existing Resources

If you already created resources using the bash script, you can import them:

```bash
# Import VPC connector
terraform import google_vpc_access_connector.redis_connector \
  projects/YOUR_PROJECT_ID/locations/us-central1/connectors/redis-connector

# Import Redis instance
terraform import 'google_redis_instance.main[0]' \
  projects/YOUR_PROJECT_ID/locations/us-central1/instances/social-video-redis
```

Replace `YOUR_PROJECT_ID` with your actual GCP project ID.

## Files

- `main.tf` - Main resource definitions
- `variables.tf` - Variable declarations
- `outputs.tf` - Output values (connection info, etc.)
- `terraform.tfvars` - Your actual values (gitignored)
- `terraform.tfvars.example` - Example configuration

## State Management

Terraform state is stored locally in `terraform.tfstate`. **Do not commit this file** - it may contain sensitive information.

For production use, consider using [remote state](https://developer.hashicorp.com/terraform/language/state/remote) in GCS:

```hcl
terraform {
  backend "gcs" {
    bucket = "your-terraform-state-bucket"
    prefix = "wandr/state"
  }
}
```
