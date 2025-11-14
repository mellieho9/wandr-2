#!/bin/bash

# Google Cloud VPC Cleanup Script
# Deletes VPC connector and optionally Redis instance to stop charges

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration (matching setup_redis.sh)
PROJECT_ID="${GCP_PROJECT_ID:-}"
REGION="${GCP_REGION:-us-central1}"
REDIS_INSTANCE_NAME="social-video-redis"
VPC_CONNECTOR_NAME="redis-connector"

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

delete_vpc_connector() {
    print_info "Checking for VPC connector: $VPC_CONNECTOR_NAME..."

    # Check if connector exists
    if ! gcloud compute networks vpc-access connectors describe $VPC_CONNECTOR_NAME \
        --region=$REGION --project=$PROJECT_ID &>/dev/null; then
        print_warning "VPC connector $VPC_CONNECTOR_NAME does not exist. Nothing to delete."
        return 0
    fi

    print_info "Deleting VPC connector: $VPC_CONNECTOR_NAME..."
    print_warning "This will stop the daily charges for the VPC connector."

    gcloud compute networks vpc-access connectors delete $VPC_CONNECTOR_NAME \
        --region=$REGION \
        --project=$PROJECT_ID \
        --quiet

    print_info "VPC connector deleted successfully!"
}

delete_redis_instance() {
    print_info "Checking for Redis instance: $REDIS_INSTANCE_NAME..."

    # Check if instance exists
    if ! gcloud redis instances describe $REDIS_INSTANCE_NAME \
        --region=$REGION --project=$PROJECT_ID &>/dev/null; then
        print_warning "Redis instance $REDIS_INSTANCE_NAME does not exist. Nothing to delete."
        return 0
    fi

    print_info "Deleting Redis instance: $REDIS_INSTANCE_NAME..."
    print_warning "This will also stop charges for the Redis instance."

    gcloud redis instances delete $REDIS_INSTANCE_NAME \
        --region=$REGION \
        --project=$PROJECT_ID \
        --quiet

    print_info "Redis instance deleted successfully!"
}

print_summary() {
    echo ""
    echo "=========================================="
    echo "Cleanup Complete!"
    echo "=========================================="
    echo ""
    echo "Resources deleted:"
    echo "  - VPC Connector: $VPC_CONNECTOR_NAME"
    if [ "$DELETE_REDIS" = "true" ]; then
        echo "  - Redis Instance: $REDIS_INSTANCE_NAME"
    fi
    echo ""
    echo "The daily charges should stop within 24 hours."
    echo ""
    echo "You can verify deletion at:"
    echo "  VPC Connectors: https://console.cloud.google.com/networking/connectors"
    echo "  Redis Instances: https://console.cloud.google.com/memorystore/redis/instances"
    echo ""
}

# Main execution
main() {
    echo "=========================================="
    echo "Google Cloud VPC Cleanup"
    echo "=========================================="
    echo ""

    check_prerequisites

    # Ask if user wants to delete Redis instance too
    echo ""
    echo "This script will delete the VPC connector that's causing charges."
    echo ""
    read -p "Do you also want to delete the Redis instance? (y/N): " -n 1 -r
    echo ""

    DELETE_REDIS="false"
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        DELETE_REDIS="true"
    fi

    echo ""
    print_warning "This will delete the following resources:"
    print_warning "  - VPC Connector: $VPC_CONNECTOR_NAME (region: $REGION)"
    if [ "$DELETE_REDIS" = "true" ]; then
        print_warning "  - Redis Instance: $REDIS_INSTANCE_NAME (region: $REGION)"
    fi
    echo ""
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleanup cancelled."
        exit 0
    fi

    echo ""
    delete_vpc_connector

    if [ "$DELETE_REDIS" = "true" ]; then
        delete_redis_instance
    fi

    print_summary
}

# Run main function
main
