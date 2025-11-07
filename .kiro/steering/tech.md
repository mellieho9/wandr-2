# Technology Stack

## Core Framework

### Backend

- **Runtime**: Python 3.11
- **Web Framework**: Flask with Gunicorn WSGI server
- **Deployment**: Google Cloud Run with auto-scaling
- **Database**: PostgreSQL with Prisma ORM (Prisma Client Python)
- **Cache/Session Store**: Redis (Google Cloud Memorystore) for OAuth state management in production

### Frontend

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite (fast HMR, optimized builds)
- **UI Components**: Radix UI primitives
- **Styling**: Tailwind CSS
- **Routing**: Client-side routing with fallback to index.html

## External Services & APIs

- **Notion API**: OAuth authentication, database read/write operations
- **OpenAI Whisper API**: Audio transcription
- **Google Vision API**: OCR text extraction from video frames
- **Gemini API**: Schema-specific content summarization (Gemini 1.5 Pro)
- **Grafana Cloud**: Centralized logging and monitoring

## Key Libraries

- `prisma` - Prisma Client Python for database ORM
- `notion-client` - Notion API wrapper
- `redis` - Redis client for OAuth state storage (production)
- `yt-dlp` - Video downloader for TikTok and Instagram
- `opencv-python-headless` - Video frame extraction
- `ffmpeg-python` - Audio extraction from video
- `google-cloud-vision` - OCR service client
- `google-generativeai` - Gemini API client
- `requests` - HTTP client for API calls
- `python-dotenv` - Environment configuration

## System Dependencies

- `ffmpeg` - Audio/video processing
- `postgresql-client` - Database connectivity

## Common Commands

### Local Development

```bash
# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate Prisma Client
prisma generate

# Run database migrations
prisma db push

# Start Flask development server
flask run --host=0.0.0.0 --port=8080

# Run tests
pytest tests/

# Frontend setup (in a new terminal)
cd frontend
npm install
npm run dev
```

### Deployment

```bash
# Build and deploy to Cloud Run
./scripts/deploy.sh

# View logs
gcloud run logs read social-video-processor --region=us-central1

# Check service status
gcloud run services describe social-video-processor --region=us-central1
```

### Database Operations

```bash
# Connect to PostgreSQL
psql $DATABASE_URL

# Generate Prisma Client after schema changes
prisma generate

# Push schema changes to database
prisma db push

# Create a migration
prisma migrate dev --name migration_name

# Apply migrations in production
prisma migrate deploy

# Open Prisma Studio (database GUI)
prisma studio
```

## Environment Configuration

Required environment variables in `.env`:

- `NOTION_CLIENT_ID`, `NOTION_CLIENT_SECRET`, `NOTION_REDIRECT_URI`
- `WHISPER_API_KEY` (OpenAI API key)
- `GEMINI_API_KEY` (Google Gemini API key)
- `GOOGLE_APPLICATION_CREDENTIALS` (path to service account JSON)
- `DATABASE_URL` (PostgreSQL connection string)
- `REDIS_HOST`, `REDIS_PORT` (optional, for production OAuth state storage)
- `GRAFANA_CLOUD_API_KEY`, `GRAFANA_CLOUD_URL`
- `FLASK_ENV`, `LOG_LEVEL`, `FLASK_SECRET_KEY`

## Prisma ORM

The project uses Prisma Client Python for type-safe database operations:

### Key Commands

```bash
# Generate Prisma client after schema changes
prisma generate

# Push schema changes to database (development)
prisma db push

# Create a migration (production)
prisma migrate dev --name migration_name

# Apply migrations in production
prisma migrate deploy

# Open Prisma Studio (database GUI)
prisma studio
```

### Usage Pattern

```python
from utils.db import get_db

db = get_db()

# Create with relations
user = await db.user.create(
    data={
        'oauthId': 'oauth_123',
        'notionAccessToken': 'token',
        'notionSchemas': {
            'create': [
                {'dbId': 'db1', 'tag': 'cooking', 'schema': {...}}
            ]
        }
    }
)

# Query with relations
user = await db.user.find_unique(
    where={'id': user_id},
    include={'notionSchemas': True, 'linkDatabases': True}
)
```

## Redis Setup (Production)

For production deployments with multiple Cloud Run instances, Redis is required for OAuth state management.

### Automated Setup

```bash
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"
export REDIS_TIER="BASIC"  # or "STANDARD" for HA
./scripts/setup_redis.sh
```

This script:

1. Enables required Google Cloud APIs
2. Creates VPC connector for Cloud Run → Redis connectivity
3. Creates Memorystore Redis instance
4. Configures Cloud Run with Redis connection details

### Manual Setup Steps

1. **Create VPC Connector**:

   ```bash
   gcloud compute networks vpc-access connectors create redis-connector \
     --region=$GCP_REGION --network=default --range=10.8.0.0/28
   ```

2. **Create Redis Instance**:

   ```bash
   gcloud redis instances create social-video-redis \
     --size=1 --region=$GCP_REGION --redis-version=redis_7_0 \
     --tier=BASIC --network=default
   ```

3. **Get Connection Details**:

   ```bash
   gcloud redis instances describe social-video-redis \
     --region=$GCP_REGION --format="get(host,port)"
   ```

4. **Configure Cloud Run**:
   ```bash
   gcloud run services update social-video-processor \
     --vpc-connector=redis-connector \
     --vpc-egress=private-ranges-only \
     --update-env-vars REDIS_HOST=$REDIS_HOST,REDIS_PORT=6379
   ```

### Local Development

Leave `REDIS_HOST` empty in `.env` - the application automatically falls back to in-memory storage.

## Deployment Checklist

### Prerequisites

- [ ] Google Cloud Project with billing enabled
- [ ] `gcloud` CLI installed and authenticated
- [ ] Notion OAuth app configured with correct redirect URI

### Infrastructure Setup

- [ ] Redis instance created (production only)
- [ ] VPC connector configured (production only)
- [ ] PostgreSQL database provisioned
- [ ] Secrets stored in Secret Manager

### Environment Variables (Cloud Run)

- [ ] `NOTION_CLIENT_ID`, `NOTION_CLIENT_SECRET`, `NOTION_REDIRECT_URI`
- [ ] `REDIS_HOST`, `REDIS_PORT` (production)
- [ ] `DATABASE_URL`, `FLASK_SECRET_KEY`
- [ ] `WHISPER_API_KEY`, `GEMINI_API_KEY`
- [ ] `GRAFANA_CLOUD_API_KEY`, `GRAFANA_CLOUD_URL`

### Deployment

```bash
# Build frontend
cd frontend && npm run build && cd ..

# Build and deploy
gcloud builds submit --tag gcr.io/$PROJECT_ID/social-video-processor
gcloud run deploy social-video-processor \
  --image gcr.io/$PROJECT_ID/social-video-processor \
  --region us-central1 \
  --allow-unauthenticated \
  --vpc-connector redis-connector \
  --set-env-vars REDIS_HOST=$REDIS_HOST,REDIS_PORT=6379
```

### Post-Deployment

- [ ] Test health endpoint: `curl https://your-service.run.app/health`
- [ ] Test OAuth flow through UI
- [ ] Verify database registration works
- [ ] Set up Grafana Cloud dashboards and alerts
- [ ] Configure budget alerts in Google Cloud
