# Project Structure

## Directory Organization

```
.
├── app.py                      # Flask application entry point with route definitions
├── config/
│   └── settings.py             # Environment configuration and settings loader
├── services/                   # Business logic and processing services
│   ├── database_monitor.py     # Background worker polling Link Database
│   ├── video_downloader.py     # Video download from TikTok/Instagram
│   ├── whisper_service.py      # Audio transcription via Whisper API
│   ├── ocr_service.py          # Text extraction via Google Vision OCR
│   ├── gemini_summarizer.py    # Schema-specific summarization via Gemini
│   ├── processing_pipeline.py  # Orchestrates full processing workflow
│   └── cleanup_job.py          # Scheduled cleanup of temporary files
├── clients/
│   └── notion_client.py        # Notion API wrapper for OAuth and database ops
├── prisma/
│   └── schema.prisma           # Prisma schema definition
├── utils/
│   ├── logger.py               # Grafana Cloud logging configuration
│   └── db.py                   # Prisma client initialization and utilities
├── scripts/
│   ├── deploy.sh               # Cloud Run deployment script
│   └── setup_database.sh       # Database initialization script
├── tests/                      # Test suite
│   ├── conftest.py             # Pytest fixtures and test utilities
│   ├── fixtures/               # Sample videos and test data
│   ├── test_pipeline.py        # End-to-end integration tests
│   └── test_*.py               # Service-specific test files
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container image definition
├── cloudbuild.yaml             # Google Cloud Build configuration
├── app.yaml                    # Cloud Run service configuration
└── .env.example                # Environment variable template
```

## Architecture Patterns

### Pipeline Architecture

Processing follows a sequential pipeline pattern:

1. Database Monitor → 2. Video Downloader → 3. Whisper Transcription → 4. OCR Service → 5. Gemini Summarization → 6. Notion Content Writer

Each stage updates Link Database status and handles errors independently.

### Service Layer Pattern

Business logic is encapsulated in service classes (`services/`) with clear interfaces. Services are injected as dependencies into the pipeline orchestrator.

### Prisma ORM Pattern

Database operations use Prisma Client Python for type-safe queries and automatic migrations. The Prisma schema (`prisma/schema.prisma`) defines all models and relationships.

## Key Conventions

- **Error Handling**: All services raise custom exceptions (e.g., `DownloadException`, `TranscriptionException`) that are caught by the pipeline orchestrator
- **Status Updates**: Link Database status field is updated at every pipeline stage: "pending" → "downloading" → "transcribing" → "processing" → "saving" → "completed" or "failed"
- **Temporary Files**: Videos stored in `/tmp` with unique filenames, cleaned up after processing or on failure
- **Async Processing**: Background worker polls every 60 seconds; processing queue table manages concurrent video processing
- **Logging**: Structured JSON logs sent to Grafana Cloud with context (user_id, entry_id, stage, error details)
- **Retry Logic**: Exponential backoff with 3 attempts for transient failures (network, rate limits)
- **Graceful Degradation**: OCR failures don't stop processing; pipeline continues with transcription only
