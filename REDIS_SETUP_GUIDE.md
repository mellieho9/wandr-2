# Google Cloud Memorystore Redis Setup Guide

This guide walks you through setting up Google Cloud Memorystore Redis for OAuth state management in production.

## Overview

Redis is used in production to store OAuth state tokens across multiple Cloud Run instances. For local development, the application falls back to in-memory storage.

## Prerequisites

- Google Cloud Project with billing enabled
- `gcloud` CLI installed and authenticated
- Cloud Run service deployed or ready to deploy
- Appropriate IAM permissions (Redis Admin, Compute Network Admin)

## Step 1: Create VPC Connector

Cloud Run needs a VPC connector to access Memorystore Redis (which runs in a VPC).

```bash
# Set your project ID
export PROJECT_ID="your-project-id"
export REGION="us-central1"

# Enable required APIs
gcloud services enable vpcaccess.googleapis.com --project=$PROJECT_ID
gcloud services enable redis.googleapis.com --project=$PROJECT_ID
gcloud services enable compute.googleapis.com --project=$PROJECT_ID

# Create VPC connector
gcloud compute networks vpc-access connectors create redis-connector \
  --region=$REGION \
  --network=default \
  --range=10.8.0.0/28 \
  --project=$PROJECT_ID
```

**Note**: The `--range` must be an unused /28 CIDR block in your VPC.

## Step 2: Create Redis Instance

Create a Memorystore Redis instance:

```bash
# Create Redis instance (Basic tier for development, Standard tier for production)
gcloud redis instances create social-video-redis \
  --size=1 \
  --region=$REGION \
  --redis-version=redis_7_0 \
  --tier=BASIC \
  --network=default \
  --project=$PROJECT_ID
```

**Options**:

- `--tier=BASIC`: Single node (development/staging)
- `--tier=STANDARD`: High availability with automatic failover (production)
- `--size=1`: 1GB memory (adjust based on needs)

This command takes 5-10 minutes to complete.

## Step 3: Get Redis Connection Details

Once the instance is created, retrieve the connection details:

```bash
# Get Redis host IP
gcloud redis instances describe social-video-redis \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="get(host)"

# Get Redis port (default is 6379)
gcloud redis instances describe social-video-redis \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="get(port)"
```

Example output:

```
10.0.0.3
6379
```

## Step 4: Configure Environment Variables

Add the Redis connection details to your Cloud Run service:

### Option A: Using gcloud CLI

```bash
export REDIS_HOST="10.0.0.3"  # Replace with your Redis host IP
export REDIS_PORT="6379"

gcloud run services update social-video-processor \
  --region=$REGION \
  --update-env-vars REDIS_HOST=$REDIS_HOST,REDIS_PORT=$REDIS_PORT \
  --project=$PROJECT_ID
```

### Option B: Using Cloud Console

1. Go to Cloud Run in Google Cloud Console
2. Select your service `social-video-processor`
3. Click "Edit & Deploy New Revision"
4. Go to "Variables & Secrets" tab
5. Add environment variables:
   - `REDIS_HOST`: `10.0.0.3` (your Redis IP)
   - `REDIS_PORT`: `6379`
6. Click "Deploy"

### Option C: Update .env for Local Testing

For local development with Redis (optional):

```bash
# .env
REDIS_HOST=localhost
REDIS_PORT=6379
```

Then run Redis locally:

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

## Step 5: Configure VPC Access for Cloud Run

Update your Cloud Run service to use the VPC connector:

```bash
gcloud run services update social-video-processor \
  --region=$REGION \
  --vpc-connector=redis-connector \
  --vpc-egress=private-ranges-only \
  --project=$PROJECT_ID
```

**Note**: `--vpc-egress=private-ranges-only` ensures only private IP traffic goes through the VPC connector, while public API calls go directly through the internet.

## Step 6: Verify Connection

Deploy your application and check the logs:

```bash
# View logs
gcloud run logs read social-video-processor \
  --region=$REGION \
  --project=$PROJECT_ID \
  --limit=50
```

Look for log messages indicating Redis connection status. The application should log whether it's using Redis or falling back to in-memory storage.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Cloud Run Service                     │
│                (social-video-processor)                  │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  Flask App                                      │    │
│  │  - Uses Redis for OAuth state (production)      │    │
│  │  - Falls back to in-memory (local dev)          │    │
│  └────────────────────────────────────────────────┘    │
│                         │                                │
│                         │ via VPC Connector              │
└─────────────────────────┼────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  VPC Connector        │
              │  (redis-connector)    │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  Memorystore Redis    │
              │  (social-video-redis) │
              │  - Host: 10.0.0.3     │
              │  - Port: 6379         │
              └───────────────────────┘
```

## Cost Considerations

**Memorystore Redis Pricing** (us-central1):

- Basic tier (1GB): ~$35/month
- Standard tier (1GB): ~$70/month

**VPC Connector Pricing**:

- ~$0.07/hour (~$50/month) when in use
- Scales with throughput

**Cost Optimization**:

- Use Basic tier for development/staging
- Use Standard tier only for production (high availability)
- Consider smaller instance sizes (1GB is minimum)
- Delete unused instances

## Monitoring

### Check Redis Instance Status

```bash
gcloud redis instances describe social-video-redis \
  --region=$REGION \
  --project=$PROJECT_ID
```

### View Redis Metrics

1. Go to Cloud Console → Memorystore → Redis
2. Click on `social-video-redis`
3. View metrics: CPU usage, memory usage, connections, operations/sec

### Set Up Alerts

Create alerts for:

- Memory usage > 80%
- Connection count > 1000
- High eviction rate

## Troubleshooting

### Cloud Run can't connect to Redis

**Check VPC connector**:

```bash
gcloud compute networks vpc-access connectors describe redis-connector \
  --region=$REGION \
  --project=$PROJECT_ID
```

**Verify Cloud Run is using the connector**:

```bash
gcloud run services describe social-video-processor \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="get(spec.template.spec.containers[0].resources.limits)"
```

### Redis connection timeout

- Ensure Redis instance is in the same region as Cloud Run
- Verify VPC connector is in the same region
- Check firewall rules allow traffic from VPC connector subnet

### Application falls back to in-memory storage

- Check environment variables are set correctly
- View Cloud Run logs for connection errors
- Verify Redis instance is running: `gcloud redis instances list`

## Security Best Practices

1. **Network Isolation**: Redis is only accessible within VPC (not public internet)
2. **IAM Permissions**: Limit Redis Admin role to necessary users
3. **Encryption**: Enable in-transit encryption for production:
   ```bash
   gcloud redis instances create social-video-redis \
     --transit-encryption-mode=SERVER_AUTHENTICATION \
     ...
   ```
4. **AUTH String**: For additional security, enable Redis AUTH:
   ```bash
   gcloud redis instances update social-video-redis \
     --region=$REGION \
     --update-auth-string
   ```
   Then add `REDIS_PASSWORD` to environment variables.

## Cleanup

To delete resources and stop incurring costs:

```bash
# Delete Redis instance
gcloud redis instances delete social-video-redis \
  --region=$REGION \
  --project=$PROJECT_ID

# Delete VPC connector
gcloud compute networks vpc-access connectors delete redis-connector \
  --region=$REGION \
  --project=$PROJECT_ID
```

## Next Steps

After completing this setup:

1. Proceed to task 3.5.2: Implement Redis-backed OAuth state storage
2. Update `app.py` to use Redis instead of in-memory dictionary
3. Test OAuth flow with multiple Cloud Run instances
4. Monitor Redis metrics in production

## References

- [Memorystore for Redis Documentation](https://cloud.google.com/memorystore/docs/redis)
- [Serverless VPC Access Documentation](https://cloud.google.com/vpc/docs/configure-serverless-vpc-access)
- [Cloud Run VPC Connectivity](https://cloud.google.com/run/docs/configuring/vpc-connectors)
