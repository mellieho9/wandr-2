# Deployment Checklist

This checklist ensures all infrastructure components are properly configured before deploying to Google Cloud Run.

## Prerequisites

- [ ] Google Cloud Project created with billing enabled
- [ ] `gcloud` CLI installed and authenticated
- [ ] Project ID configured: `gcloud config set project YOUR_PROJECT_ID`
- [ ] Required APIs enabled (automated by setup scripts)

## Infrastructure Setup

### 1. Redis Setup (OAuth State Management)

**For Production Deployment:**

```bash
# Set environment variables
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"
export REDIS_TIER="BASIC"  # or "STANDARD" for HA

# Run automated setup script
./scripts/setup_redis.sh
```

This script will:

- Enable required Google Cloud APIs
- Create VPC connector for Cloud Run → Redis connectivity
- Create Memorystore Redis instance
- Configure Cloud Run service with Redis connection details

**Manual Setup:**
See `REDIS_SETUP_GUIDE.md` for detailed step-by-step instructions.

**For Local Development:**
Leave `REDIS_HOST` empty in `.env` - the application will use in-memory storage.

### 2. PostgreSQL Database

- [ ] Create Cloud SQL PostgreSQL instance OR use external PostgreSQL
- [ ] Update `DATABASE_URL` in Cloud Run environment variables
- [ ] Run Prisma migrations: `prisma migrate deploy`

### 3. Service Account & IAM

- [ ] Create service account for Cloud Run
- [ ] Grant permissions:
  - Cloud SQL Client (if using Cloud SQL)
  - Secret Manager Secret Accessor
  - Redis Editor (for Memorystore access)

### 4. Secrets Management

Store sensitive values in Google Secret Manager:

```bash
# Create secrets
echo -n "your_notion_client_secret" | gcloud secrets create notion-client-secret --data-file=-
echo -n "your_whisper_api_key" | gcloud secrets create whisper-api-key --data-file=-
echo -n "your_gemini_api_key" | gcloud secrets create gemini-api-key --data-file=-
echo -n "your_database_url" | gcloud secrets create database-url --data-file=-
echo -n "your_flask_secret_key" | gcloud secrets create flask-secret-key --data-file=-
echo -n "your_grafana_api_key" | gcloud secrets create grafana-cloud-api-key --data-file=-
```

## Environment Variables

### Required for Cloud Run

| Variable                | Source           | Example                                             |
| ----------------------- | ---------------- | --------------------------------------------------- |
| `NOTION_CLIENT_ID`      | Notion OAuth App | `2a2d872b-594c-80c3-8e2e-003748006abd`              |
| `NOTION_CLIENT_SECRET`  | Secret Manager   | `secret_xxx...`                                     |
| `NOTION_REDIRECT_URI`   | Cloud Run URL    | `https://your-service.run.app/auth/notion/callback` |
| `REDIS_HOST`            | Memorystore IP   | `10.0.0.3`                                          |
| `REDIS_PORT`            | Memorystore Port | `6379`                                              |
| `WHISPER_API_KEY`       | Secret Manager   | `sk-xxx...`                                         |
| `GEMINI_API_KEY`        | Secret Manager   | `AIza...`                                           |
| `DATABASE_URL`          | Secret Manager   | `postgresql://user:pass@host/db`                    |
| `GRAFANA_CLOUD_API_KEY` | Secret Manager   | `glc_xxx...`                                        |
| `GRAFANA_CLOUD_URL`     | Grafana Cloud    | `https://logs-prod-us-central1.grafana.net`         |
| `FLASK_ENV`             | Static           | `production`                                        |
| `FLASK_SECRET_KEY`      | Secret Manager   | Random string                                       |
| `LOG_LEVEL`             | Static           | `INFO`                                              |

### Optional Configuration

| Variable                    | Default | Description                         |
| --------------------------- | ------- | ----------------------------------- |
| `POLLING_INTERVAL_SECONDS`  | `60`    | Link Database polling frequency     |
| `MAX_CONCURRENT_PROCESSING` | `5`     | Max videos processed simultaneously |

## Deployment Steps

### 1. Build and Deploy

```bash
# Build container image
gcloud builds submit --tag gcr.io/$PROJECT_ID/social-video-processor

# Deploy to Cloud Run
gcloud run deploy social-video-processor \
  --image gcr.io/$PROJECT_ID/social-video-processor \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --vpc-connector redis-connector \
  --vpc-egress private-ranges-only \
  --set-env-vars NOTION_CLIENT_ID=$NOTION_CLIENT_ID,REDIS_HOST=$REDIS_HOST,REDIS_PORT=6379 \
  --set-secrets NOTION_CLIENT_SECRET=notion-client-secret:latest,WHISPER_API_KEY=whisper-api-key:latest
```

### 2. Verify Deployment

```bash
# Check service status
gcloud run services describe social-video-processor --region us-central1

# View logs
gcloud run logs read social-video-processor --region us-central1 --limit 50

# Test health endpoint
curl https://your-service.run.app/health
```

### 3. Update Notion OAuth Redirect URI

- [ ] Go to Notion OAuth app settings
- [ ] Update redirect URI to: `https://your-service.run.app/auth/notion/callback`
- [ ] Update `NOTION_REDIRECT_URI` environment variable in Cloud Run

## Post-Deployment

### Monitoring

- [ ] Set up Grafana Cloud dashboards
- [ ] Configure alerts for:
  - Processing failure rate > 10%
  - Redis memory usage > 80%
  - Cloud Run error rate > 5%

### Testing

- [ ] Test OAuth flow
- [ ] Register test Content Database
- [ ] Register test Link Database
- [ ] Add test video URL and verify processing

### Cost Optimization

- [ ] Review Cloud Run auto-scaling settings
- [ ] Monitor Redis memory usage (consider smaller instance)
- [ ] Set up budget alerts

## Troubleshooting

### Redis Connection Issues

```bash
# Check Redis instance status
gcloud redis instances describe social-video-redis --region us-central1

# Check VPC connector
gcloud compute networks vpc-access connectors describe redis-connector --region us-central1

# Verify Cloud Run is using VPC connector
gcloud run services describe social-video-processor --region us-central1 --format="get(spec.template.metadata.annotations)"
```

### Application Logs

```bash
# Stream logs in real-time
gcloud run logs tail social-video-processor --region us-central1

# Filter for errors
gcloud run logs read social-video-processor --region us-central1 --log-filter="severity>=ERROR"
```

## Rollback

If deployment fails:

```bash
# List revisions
gcloud run revisions list --service social-video-processor --region us-central1

# Rollback to previous revision
gcloud run services update-traffic social-video-processor \
  --to-revisions REVISION_NAME=100 \
  --region us-central1
```

## Resources

- [REDIS_SETUP_GUIDE.md](./REDIS_SETUP_GUIDE.md) - Detailed Redis setup instructions
- [cloud-run-config.yaml](./cloud-run-config.yaml) - Cloud Run configuration template
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Memorystore for Redis Documentation](https://cloud.google.com/memorystore/docs/redis)
