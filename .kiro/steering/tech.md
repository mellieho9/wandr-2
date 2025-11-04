# Technology Stack

## Core Framework

- **Runtime**: Python 3.11
- **Web Framework**: Flask with Gunicorn WSGI server
- **Deployment**: Google Cloud Run with auto-scaling
- **Database**: PostgreSQL with psycopg2-binary driver

## External Services & APIs

- **Notion API**: OAuth authentication, database read/write operations
- **OpenAI Whisper API**: Audio transcription
- **Google Vision API**: OCR text extraction from video frames
- **Gemini API**: Schema-specific content summarization (Gemini 1.5 Pro)
- **Grafana Cloud**: Centralized logging and monitoring

## Key Libraries

- `notion-client` - Notion API wrapper
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
# Install dependencies
pip install -r requirements.txt

# Run database migrations
python scripts/setup_database.py

# Start Flask development server
flask run --host=0.0.0.0 --port=8080

# Run tests
pytest tests/
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

# Run migrations
psql $DATABASE_URL -f migrations/001_initial_schema.sql
```

## Environment Configuration

Required environment variables in `.env`:

- `NOTION_CLIENT_ID`, `NOTION_CLIENT_SECRET`, `NOTION_REDIRECT_URI`
- `WHISPER_API_KEY` (OpenAI API key)
- `GEMINI_API_KEY` (Google Gemini API key)
- `GOOGLE_APPLICATION_CREDENTIALS` (path to service account JSON)
- `DATABASE_URL` (PostgreSQL connection string)
- `GRAFANA_CLOUD_API_KEY`, `GRAFANA_CLOUD_URL`
- `FLASK_ENV`, `LOG_LEVEL`
