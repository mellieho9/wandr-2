#!/bin/bash

# Google Cloud Memorystore Redis Setup Script
# This script automates the setup of Redis for OAuth state management

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-}"
REGION="${GCP_REGION:-us-central1}"
REDIS_INSTANCE_NAME="social-video-redis"
VPC_CONNECTOR_NAME="redis-connector"
VPC_NETWORK="default"
VPC_CONNECTOR_RANGE="10.8.0.0/28"
REDIS_TIER="${REDIS_TIER:-BASIC}"  # BASIC or STANDARD
REDIS_SIZE="${REDIS_SIZE:-1}"  # GB
CLOUD_RUN_SERVICE="social-video-processor"

# Functions
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if project ID is set
    if [ -z "$PROJECT_ID" ]; then
        PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
        if [ -z "$PROJECT_ID" ]; then
            print_error "GCP_PROJECT_ID is not set. Please set it or configure gcloud default project."
            exit 1
        fi
    fi
    
    print_info "Using project: $PROJECT_ID"
    print_info "Using region: $REGION"
}

enable_apis() {
    print_info "Enabling required Google Cloud APIs..."
    
    gcloud services enable vpcaccess.googleapis.com --project=$PROJECT_ID
    gcloud services enable redis.googleapis.com --project=$PROJECT_ID
    gcloud services enable compute.googleapis.com --project=$PROJECT_ID
    gcloud services enable run.googleapis.com --project=$PROJECT_ID
    
    print_info "APIs enabled successfully"
}

create_vpc_connector() {
    print_info "Creating VPC connector: $VPC_CONNECTOR_NAME..."
    
    # Check if connector already exists
    if gcloud compute networks vpc-access connectors describe $VPC_CONNECTOR_NAME \
        --region=$REGION --project=$PROJECT_ID &>/dev/null; then
        print_warning "VPC connector $VPC_CONNECTOR_NAME already exists. Skipping creation."
        return 0
    fi
    
    gcloud compute networks vpc-access connectors create $VPC_CONNECTOR_NAME \
        --region=$REGION \
        --network=$VPC_NETWORK \
        --range=$VPC_CONNECTOR_RANGE \
        --project=$PROJECT_ID
    
    print_info "VPC connector created successfully"
}

create_redis_instance() {
    print_info "Creating Redis instance: $REDIS_INSTANCE_NAME..."
    print_info "Tier: $REDIS_TIER, Size: ${REDIS_SIZE}GB"
    
    # Check if instance already exists
    if gcloud redis instances describe $REDIS_INSTANCE_NAME \
        --region=$REGION --project=$PROJECT_ID &>/dev/null; then
        print_warning "Redis instance $REDIS_INSTANCE_NAME already exists. Skipping creation."
        return 0
    fi
    
    print_warning "This operation takes 5-10 minutes. Please wait..."
    
    gcloud redis instances create $REDIS_INSTANCE_NAME \
        --size=$REDIS_SIZE \
        --region=$REGION \
        --redis-version=redis_7_0 \
        --tier=$REDIS_TIER \
        --network=$VPC_NETWORK \
        --project=$PROJECT_ID
    
    print_info "Redis instance created successfully"
}

get_redis_connection_info() {
    print_info "Retrieving Redis connection information..."
    
    REDIS_HOST=$(gcloud redis instances describe $REDIS_INSTANCE_NAME \
        --region=$REGION \
        --project=$PROJECT_ID \
        --format="get(host)")
    
    REDIS_PORT=$(gcloud redis instances describe $REDIS_INSTANCE_NAME \
        --region=$REGION \
        --project=$PROJECT_ID \
        --format="get(port)")
    
    if [ -z "$REDIS_HOST" ] || [ -z "$REDIS_PORT" ]; then
        print_error "Failed to retrieve Redis connection information"
        exit 1
    fi
    
    print_info "Redis Host: $REDIS_HOST"
    print_info "Redis Port: $REDIS_PORT"
    
    # Export for use in other scripts
    export REDIS_HOST
    export REDIS_PORT
}

update_cloud_run_service() {
    print_info "Checking if Cloud Run service exists..."
    
    # Check if Cloud Run service exists
    if ! gcloud run services describe $CLOUD_RUN_SERVICE \
        --region=$REGION --project=$PROJECT_ID &>/dev/null; then
        print_warning "Cloud Run service $CLOUD_RUN_SERVICE does not exist yet."
        print_warning "Please deploy the service first, then run this script again or manually configure:"
        print_info "  REDIS_HOST=$REDIS_HOST"
        print_info "  REDIS_PORT=$REDIS_PORT"
        print_info "  VPC_CONNECTOR=$VPC_CONNECTOR_NAME"
        return 0
    fi
    
    print_info "Updating Cloud Run service with Redis configuration..."
    
    gcloud run services update $CLOUD_RUN_SERVICE \
        --region=$REGION \
        --update-env-vars REDIS_HOST=$REDIS_HOST,REDIS_PORT=$REDIS_PORT \
        --vpc-connector=$VPC_CONNECTOR_NAME \
        --vpc-egress=private-ranges-only \
        --project=$PROJECT_ID
    
    print_info "Cloud Run service updated successfully"
}

print_summary() {
    echo ""
    echo "=========================================="
    echo "Redis Setup Complete!"
    echo "=========================================="
    echo ""
    echo "Redis Connection Details:"
    echo "  Host: $REDIS_HOST"
    echo "  Port: $REDIS_PORT"
    echo ""
    echo "VPC Connector: $VPC_CONNECTOR_NAME"
    echo "Region: $REGION"
    echo ""
    echo "Next Steps:"
    echo "1. Update your .env file with:"
    echo "   REDIS_HOST=$REDIS_HOST"
    echo "   REDIS_PORT=$REDIS_PORT"
    echo ""
    echo "2. If Cloud Run service wasn't updated automatically, run:"
    echo "   gcloud run services update $CLOUD_RUN_SERVICE \\"
    echo "     --region=$REGION \\"
    echo "     --update-env-vars REDIS_HOST=$REDIS_HOST,REDIS_PORT=$REDIS_PORT \\"
    echo "     --vpc-connector=$VPC_CONNECTOR_NAME \\"
    echo "     --vpc-egress=private-ranges-only \\"
    echo "     --project=$PROJECT_ID"
    echo ""
    echo "3. Proceed to task 3.5.2: Implement Redis-backed OAuth state storage"
    echo ""
    echo "Monitoring:"
    echo "  View Redis metrics: https://console.cloud.google.com/memorystore/redis/instances"
    echo "  View Cloud Run logs: gcloud run logs read $CLOUD_RUN_SERVICE --region=$REGION"
    echo ""
}

# Main execution
main() {
    echo "=========================================="
    echo "Google Cloud Memorystore Redis Setup"
    echo "=========================================="
    echo ""
    
    check_prerequisites
    enable_apis
    create_vpc_connector
    create_redis_instance
    get_redis_connection_info
    update_cloud_run_service
    print_summary
}

# Run main function
main
