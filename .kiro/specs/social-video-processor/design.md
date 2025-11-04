# Design Document

## Overview

The Social Video Processor is a cloud-native microservice built with Flask and deployed on Google Cloud Run. It monitors a user's Notion Link Database for new video URLs, downloads videos from TikTok and Instagram, extracts content through audio transcription (Whisper) and OCR (Google Vision API), generates schema-specific summaries using Gemini API, and saves the processed content to the appropriate Notion Content Database based on user-defined tags.

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│  User's Notion  │
│  Link Database  │
└────────┬────────┘
         │
         │ Polling (60s interval)
         ▼
┌─────────────────────────────────────────────────────────┐
│           Google Cloud Run Service                       │
│  ┌───────────────────────────────────────────────────┐  │
│  │              Flask Application                     │  │
│  │  ┌──────────────────────────────────────────────┐ │  │
│  │  │  Database Monitor (Background Worker)        │ │  │
│  │  └──────────────────────────────────────────────┘ │  │
│  │  ┌──────────────────────────────────────────────┐ │  │
│  │  │  Video Processing Pipeline                   │ │  │
│  │  │  1. Video Downloader                         │ │  │
│  │  │  2. Whisper Transcription                    │ │  │
│  │  │  3. Google Vision OCR                        │ │  │
│  │  │  4. Gemini Summarization                     │ │  │
│  │  │  5. Notion Content Writer                    │ │  │
│  │  └──────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
         │
         │ Logs & Metrics
         ▼
┌─────────────────┐
│  Grafana Cloud  │
└─────────────────┘

External Services:
- Notion API (OAuth, Database Read/Write)
- Whisper API (Audio Transcription)
- Google Vision API (OCR)
- Gemini API (Content Summarization)
- PostgreSQL (User & Schema Storage)
```

### Component Architecture

The system follows a pipeline architecture with the following components:

1. **API Layer**: Flask REST API for user authentication, database registration, and webhook endpoints
2. **Background Worker**: Polling service that monitors Link Database for new entries
3. **Processing Pipeline**: Sequential stages for video download, transcription, OCR, summarization, and storage
4. **External Service Clients**: Wrappers for Notion, Whisper, Google Vision, and Gemini APIs
5. **Data Layer**: PostgreSQL database for user data, schema mappings, and processing state

## Components and Interfaces

### 1. Flask Application (`app.py`)

Main application entry point with route definitions and service initialization.

**Endpoints:**

- `POST /auth/notion/callback` - OAuth callback handler
- `GET /auth/notion/login` - Initiates Notion OAuth flow
- `POST /api/databases/register` - Register Content Database with schema
- `GET /api/databases` - List registered Content Databases
- `POST /api/link-database/register` - Register Link Database
- `GET /health` - Health check endpoint for Cloud Run

### 2. Database Monitor (`services/database_monitor.py`)

Background worker that polls the Notion Link Database for new entries.

**Interface:**

```python
class DatabaseMonitor:
    def __init__(self, notion_client, db_repository):
        pass

    def start_monitoring(self, interval_seconds: int = 60):
        """Start polling loop"""
        pass

    def check_for_new_entries(self, user_id: str, link_db_id: str) -> List[LinkEntry]:
        """Query Link Database for entries with status='pending'"""
        pass

    def queue_for_processing(self, entry: LinkEntry):
        """Add entry to processing queue"""
        pass
```

### 3. Video Downloader (`services/video_downloader.py`)

Downloads videos from TikTok and Instagram using platform-specific libraries.

**Interface:**

```python
class VideoDownloader:
    def download(self, url: str, entry_id: str) -> str:
        """
        Download video and return local file path
        Returns: Path to downloaded video file
        Raises: DownloadException on failure
        """
        pass

    def _download_tiktok(self, url: str) -> bytes:
        """TikTok-specific download logic using yt-dlp"""
        pass

    def _download_instagram(self, url: str) -> bytes:
        """Instagram-specific download logic using yt-dlp"""
        pass
```

**Implementation Notes:**

- Use `yt-dlp` library for video downloads
- Store videos temporarily in `/tmp` directory
- Implement retry logic with exponential backoff (3 attempts)
- Update Link Database status during download

### 4. Whisper Service (`services/whisper_service.py`)

Transcribes audio from videos using OpenAI's Whisper API.

**Interface:**

```python
class WhisperService:
    def __init__(self, api_key: str):
        pass

    def transcribe(self, video_path: str) -> str:
        """
        Extract audio and transcribe to text
        Returns: Transcription text
        Raises: TranscriptionException on failure
        """
        pass

    def _extract_audio(self, video_path: str) -> str:
        """Extract audio track using ffmpeg"""
        pass
```

**Implementation Notes:**

- Use `ffmpeg` to extract audio as MP3
- Call Whisper API with audio file
- Store transcription in `video_content` table
- Handle API rate limits and timeouts

### 5. OCR Service (`services/ocr_service.py`)

Extracts text from video frames using Google Vision API.

**Interface:**

```python
class OCRService:
    def __init__(self, credentials_path: str):
        pass

    def extract_text(self, video_path: str) -> str:
        """
        Extract key frames and perform OCR
        Returns: Concatenated text from all frames
        Raises: OCRException on failure
        """
        pass

    def _extract_frames(self, video_path: str, interval_seconds: int = 2) -> List[bytes]:
        """Extract frames at regular intervals using opencv"""
        pass

    def _ocr_frame(self, frame_bytes: bytes) -> str:
        """Perform OCR on single frame"""
        pass
```

**Implementation Notes:**

- Extract frames every 2 seconds using `opencv-python`
- Call Google Vision API for each frame
- Deduplicate extracted text
- Continue processing even if OCR fails

### 6. Gemini Summarizer (`services/gemini_summarizer.py`)

Generates schema-specific summaries using Gemini API.

**Interface:**

```python
class GeminiSummarizer:
    def __init__(self, api_key: str):
        pass

    def summarize(self, transcription: str, ocr_text: str, schema: dict, prompt: str) -> dict:
        """
        Generate structured summary matching Notion schema
        Returns: Dictionary with keys matching schema fields
        Raises: SummarizationException on failure
        """
        pass

    def _build_prompt(self, transcription: str, ocr_text: str, schema: dict, user_prompt: str) -> str:
        """Construct prompt for Gemini API"""
        pass

    def _parse_response(self, response: str, schema: dict) -> dict:
        """Parse Gemini response into structured data"""
        pass
```

**Implementation Notes:**

- Use Gemini 1.5 Pro model
- Include schema structure in prompt
- Request JSON output format
- Validate response against schema
- Handle API rate limits

### 7. Notion Client (`clients/notion_client.py`)

Wrapper for Notion API operations.

**Interface:**

```python
class NotionClient:
    def __init__(self, access_token: str):
        pass

    def get_databases(self) -> List[dict]:
        """List all databases accessible to user"""
        pass

    def get_database_schema(self, db_id: str) -> dict:
        """Retrieve database schema/properties"""
        pass

    def query_database(self, db_id: str, filter: dict) -> List[dict]:
        """Query database with filters"""
        pass

    def create_page(self, db_id: str, properties: dict) -> dict:
        """Create new page in database"""
        pass

    def update_page(self, page_id: str, properties: dict) -> dict:
        """Update existing page properties"""
        pass
```

### 8. Processing Pipeline (`services/processing_pipeline.py`)

Orchestrates the entire processing workflow.

**Interface:**

```python
class ProcessingPipeline:
    def __init__(self, downloader, whisper, ocr, summarizer, notion_client):
        pass

    async def process_entry(self, entry: LinkEntry, schema_config: SchemaConfig):
        """
        Execute full pipeline for a single entry
        Updates Link Database status at each stage
        """
        pass

    def _update_status(self, entry_id: str, status: str, error: str = None):
        """Update Link Database entry status"""
        pass

    def _cleanup_temp_files(self, video_path: str):
        """Delete temporary video and audio files"""
        pass
```

## Data Models

### Prisma Schema

```prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider             = "prisma-client-py"
  recursive_type_depth = 5
}

model User {
  id                  Int             @id @default(autoincrement())
  oauthId             String          @unique @map("oauth_id")
  notionAccessToken   String          @map("notion_access_token")
  createdAt           DateTime        @default(now()) @map("created_at")
  updatedAt           DateTime        @updatedAt @map("updated_at")
  notionSchemas       NotionSchema[]
  linkDatabases       LinkDatabase[]
  processingQueue     ProcessingQueue[]

  @@map("users")
}

model NotionSchema {
  id        Int      @id @default(autoincrement())
  userId    Int      @map("user_id")
  dbId      String   @map("db_id")
  tag       String
  schema    Json
  prompt    String?
  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")
  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([userId, tag])
  @@index([userId])
  @@index([userId, tag])
  @@map("notion_schemas")
}

model VideoContent {
  id           Int      @id @default(autoincrement())
  linkEntryId  String   @unique @map("link_entry_id")
  transcription String?
  ocrContent   String?  @map("ocr_content")
  createdAt    DateTime @default(now()) @map("created_at")

  @@map("video_contents")
}

model LinkDatabase {
  id        Int      @id @default(autoincrement())
  userId    Int      @unique @map("user_id")
  dbId      String   @map("db_id")
  createdAt DateTime @default(now()) @map("created_at")
  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId])
  @@map("link_databases")
}

model ProcessingQueue {
  id           Int      @id @default(autoincrement())
  userId       Int      @map("user_id")
  linkEntryId  String   @map("link_entry_id")
  url          String
  tag          String
  status       String   @default("queued")
  retryCount   Int      @default(0) @map("retry_count")
  errorMessage String?  @map("error_message")
  createdAt    DateTime @default(now()) @map("created_at")
  updatedAt    DateTime @updatedAt @map("updated_at")
  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([status])
  @@index([userId])
  @@map("processing_queue")
}
```

### Notion Link Database Schema

Users must create a Link Database with these properties:

- `url` (URL type) - Video URL
- `tag` (Select type) - Maps to Content Database
- `processing_type` (Select type) - Optional processing preferences
- `status` (Select type) - Processing status
- `updated_time` (Date type) - Last update timestamp

### Example Content Database Schemas

**Cooking Database:**

```json
{
  "name": { "type": "title" },
  "video_link": { "type": "url" },
  "ingredients": { "type": "multi_select" },
  "steps": { "type": "rich_text" }
}
```

**Places Database:**

```json
{
  "name": { "type": "title" },
  "address": { "type": "rich_text" },
  "video_link": { "type": "url" },
  "categories": { "type": "multi_select" },
  "recommendation": { "type": "rich_text" },
  "hours": { "type": "rich_text" },
  "website": { "type": "url" },
  "is_popup": { "type": "checkbox" }
}
```

## Error Handling

### Error Categories

1. **Authentication Errors**: OAuth token expiration, invalid credentials
2. **Download Errors**: Invalid URL, video unavailable, network timeout
3. **Processing Errors**: Transcription failure, OCR failure, API rate limits
4. **Storage Errors**: Notion API errors, database write failures

### Error Handling Strategy

- **Retry Logic**: Implement exponential backoff for transient failures (network, rate limits)
- **Status Updates**: Always update Link Database status field with error details
- **Logging**: Send all errors to Grafana Cloud with context (user_id, entry_id, stage)
- **Graceful Degradation**: Continue processing if OCR fails (use transcription only)
- **Dead Letter Queue**: Move entries to failed state after 3 retry attempts

### Error Response Format

```python
{
    "error": "DownloadException",
    "message": "Failed to download video from TikTok",
    "entry_id": "notion_page_id",
    "timestamp": "2025-11-03T10:30:00Z",
    "retry_count": 2
}
```

## Testing Strategy

### Unit Tests

- Test each service component in isolation with mocked dependencies
- Test data model validation and transformations
- Test prompt construction for Gemini API
- Test schema parsing and validation

**Key Test Cases:**

- `test_video_downloader_tiktok_success()`
- `test_video_downloader_retry_logic()`
- `test_whisper_transcription()`
- `test_ocr_frame_extraction()`
- `test_gemini_prompt_construction()`
- `test_notion_client_create_page()`

### Integration Tests

- Test end-to-end pipeline with sample videos
- Test Notion API integration with test databases
- Test external API error handling

**Key Test Cases:**

- `test_pipeline_cooking_video()`
- `test_pipeline_with_ocr_failure()`
- `test_notion_oauth_flow()`

### Manual Testing

- Test with real TikTok and Instagram videos
- Verify schema-specific summaries match database structure
- Test concurrent processing of multiple videos
- Verify Grafana Cloud logging and monitoring

## Deployment Architecture

### Google Cloud Run Configuration

```yaml
service: social-video-processor
runtime: python311
instance_class: F2
automatic_scaling:
  min_instances: 0
  max_instances: 10
  target_cpu_utilization: 0.7

env_variables:
  NOTION_CLIENT_ID: ${NOTION_CLIENT_ID}
  NOTION_CLIENT_SECRET: ${NOTION_CLIENT_SECRET}
  WHISPER_API_KEY: ${WHISPER_API_KEY}
  GEMINI_API_KEY: ${GEMINI_API_KEY}
  DATABASE_URL: ${DATABASE_URL}
  GRAFANA_CLOUD_API_KEY: ${GRAFANA_CLOUD_API_KEY}

vpc_access_connector:
  name: projects/PROJECT_ID/locations/REGION/connectors/vpc-connector
```

### Dependencies

**Python Packages:**

- `flask` - Web framework
- `gunicorn` - WSGI server
- `prisma` - Prisma Client Python for ORM
- `notion-client` - Notion API wrapper
- `yt-dlp` - Video downloader
- `openai` - Whisper API client
- `google-cloud-vision` - OCR service
- `google-generativeai` - Gemini API client
- `opencv-python-headless` - Video frame extraction
- `ffmpeg-python` - Audio extraction
- `requests` - HTTP client
- `python-dotenv` - Environment configuration
- `celery` - Async task queue (optional)
- `redis` - Task queue backend (optional)

**System Dependencies:**

- `ffmpeg` - Audio/video processing
- `postgresql-client` - Database access

### Environment Variables

```
NOTION_CLIENT_ID=<notion_oauth_client_id>
NOTION_CLIENT_SECRET=<notion_oauth_client_secret>
NOTION_REDIRECT_URI=https://your-service.run.app/auth/notion/callback
WHISPER_API_KEY=<openai_api_key>
GEMINI_API_KEY=<google_gemini_api_key>
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
DATABASE_URL=postgresql://user:pass@host:5432/dbname
GRAFANA_CLOUD_API_KEY=<grafana_api_key>
GRAFANA_CLOUD_URL=https://logs-prod-us-central1.grafana.net
FLASK_ENV=production
LOG_LEVEL=INFO
```

## Security Considerations

1. **OAuth Token Storage**: Encrypt Notion access tokens in PostgreSQL
2. **API Key Management**: Store API keys in Google Secret Manager
3. **Input Validation**: Validate all URLs and tags before processing
4. **Rate Limiting**: Implement rate limiting on API endpoints
5. **CORS Configuration**: Restrict CORS to authorized domains
6. **Temporary File Cleanup**: Ensure all temp files are deleted after processing
7. **Database Access**: Use connection pooling and prepared statements

## Monitoring and Observability

### Grafana Cloud Integration

**Logs:**

- Application logs (INFO, WARNING, ERROR levels)
- Processing pipeline stage transitions
- External API call logs with latency
- Error stack traces

**Metrics:**

- Processing success/failure rates
- Average processing time per video
- API call latencies (Notion, Whisper, Gemini, Vision)
- Queue depth and processing throughput
- Cloud Run instance count and CPU/memory usage

**Alerts:**

- Processing failure rate > 10%
- API error rate > 5%
- Average processing time > 5 minutes
- Queue depth > 50 entries

### Health Checks

```python
@app.route('/health')
def health_check():
    return {
        "status": "healthy",
        "database": check_database_connection(),
        "notion_api": check_notion_api(),
        "timestamp": datetime.utcnow().isoformat()
    }
```

## Performance Optimization

1. **Async Processing**: Use Celery with Redis for background task processing
2. **Frame Sampling**: Extract frames every 2-3 seconds for OCR (not every frame)
3. **Caching**: Cache Notion schema lookups for 1 hour
4. **Connection Pooling**: Reuse HTTP connections for API calls
5. **Batch Processing**: Process multiple videos concurrently (up to 5 at a time)
6. **Lazy Loading**: Only load video into memory when needed

## Future Enhancements

1. Support for YouTube Shorts and other platforms
2. Real-time processing via Notion webhooks (when available)
3. Custom ML models for content categorization
4. Video thumbnail extraction and storage
5. Multi-language transcription support
6. User dashboard for monitoring processing status
