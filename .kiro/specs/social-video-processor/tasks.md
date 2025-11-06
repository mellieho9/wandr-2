# Implementation Plan

- [x] 1. Set up project structure and dependencies

  - Create Flask application directory structure with folders: `app/`, `services/`, `clients/`, `prisma/`, `config/`, `utils/`, `tests/`
  - Create `requirements.txt` with all Python dependencies (flask, gunicorn, prisma, notion-client, yt-dlp, openai, google-cloud-vision, google-generativeai, opencv-python-headless, ffmpeg-python)
  - Create `.env.example` file with all required environment variables
  - Create `app.py` as main Flask application entry point
  - Create `config/settings.py` for environment configuration loading
  - _Requirements: 12.4_

- [x] 2. Implement database models and migrations

  - [x] 2.1 Create Prisma schema

    - Write Prisma schema file `prisma/schema.prisma` with models: User, NotionSchema, VideoContent, LinkDatabase, ProcessingQueue
    - Configure PostgreSQL datasource and Prisma Client Python generator
    - Define relationships, indexes, and constraints
    - _Requirements: 1.2, 2.5_

  - [x] 2.2 Create Prisma client utilities
    - Create `utils/db.py` with Prisma client initialization and connection management
    - Implement context managers for database transactions
    - Add helper functions for common database operations
    - _Requirements: 2.5, 8.5_

- [x] 3. Implement Notion OAuth authentication

  - [x] 3.1 Create Notion OAuth flow endpoints

    - Implement `/auth/notion/login` endpoint to initiate OAuth flow in `app.py`
    - Implement `/auth/notion/callback` endpoint to handle OAuth callback and store tokens
    - Create user record in database with oauth_id and access_token
    - _Requirements: 1.1, 1.2, 1.4_

  - [x] 3.2 Create Notion API client wrapper
    - Implement `clients/notion_client.py` with methods: `get_databases()`, `get_database_schema()`, `query_database()`, `create_page()`, `update_page()`
    - Add OAuth token refresh logic for expired tokens
    - _Requirements: 1.4, 2.1_

- [ ] 3.5 Add Redis for OAuth state management (Production)

  - [x] 3.5.1 Set up Google Cloud Memorystore Redis instance

    - Create Redis instance in Google Cloud Console
    - Configure VPC connector for Cloud Run to access Redis
    - Add Redis connection details to environment variables (REDIS_HOST, REDIS_PORT)
    - _Requirements: 1.1, 12.1_

  - [ ] 3.5.2 Implement Redis-backed OAuth state storage
    - Add `redis` to `requirements.txt`
    - Create `utils/redis_client.py` with Redis connection management
    - Update `app.py` to use Redis for `oauth_states` instead of in-memory dictionary
    - Implement state storage with 5-minute TTL (auto-expiration)
    - Add fallback to in-memory storage for local development when Redis is unavailable
    - _Requirements: 1.1, 12.2_

- [x] 4. Implement database registration endpoints

  - [x] 4.1 Create Content Database registration endpoint

    - Implement `POST /api/databases/register` endpoint to register Content Databases
    - Retrieve and store database schema in JSONB format in notion_schemas table
    - Validate that tag is unique per user
    - Allow optional custom Schema Prompt input
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 4.2 Create Link Database registration endpoint

    - Implement `POST /api/link-database/register` endpoint
    - Validate Link Database has required fields: url, tag, processing_type, status, updated_time
    - Store Link Database ID in link_databases table
    - _Requirements: 3.2, 3.3_

  - [x] 4.3 Create database listing endpoint
    - Implement `GET /api/databases` endpoint to list registered Content Databases for authenticated user
    - Return db_id, tag, schema, and prompt for each database
    - _Requirements: 2.1_

- [ ] 5. Implement video downloader service

  - [ ] 5.1 Create video downloader with yt-dlp

    - Implement `services/video_downloader.py` with `download()` method
    - Add platform detection for TikTok and Instagram URLs
    - Implement `_download_tiktok()` and `_download_instagram()` using yt-dlp
    - Store downloaded videos in `/tmp` directory with unique filenames
    - _Requirements: 5.2, 5.3_

  - [ ] 5.2 Add retry logic and error handling
    - Implement exponential backoff retry logic (3 attempts)
    - Update Link Database status to "downloading" at start
    - Update status to "transcribing" on success or "failed" on failure
    - _Requirements: 5.1, 5.4, 5.5, 5.6_

- [ ] 6. Implement Whisper transcription service

  - [ ] 6.1 Create Whisper service for audio transcription

    - Implement `services/whisper_service.py` with `transcribe()` method
    - Add `_extract_audio()` method using ffmpeg to extract audio as MP3
    - Call OpenAI Whisper API with audio file
    - Store transcription in video_contents table
    - _Requirements: 6.1, 6.2, 6.3_

  - [ ] 6.2 Add error handling and status updates
    - Handle API rate limits and timeouts with retry logic
    - Update Link Database status to "processing" on success or "failed" on failure
    - _Requirements: 6.4, 6.5_

- [ ] 7. Implement OCR service for text extraction

  - [ ] 7.1 Create OCR service with Google Vision API

    - Implement `services/ocr_service.py` with `extract_text()` method
    - Add `_extract_frames()` method using opencv to extract frames every 2 seconds
    - Implement `_ocr_frame()` method to call Google Vision API for each frame
    - Deduplicate extracted text from multiple frames
    - Store OCR content in video_contents table
    - _Requirements: 7.1, 7.2, 7.3_

  - [ ] 7.2 Add graceful error handling
    - Log OCR errors but continue processing with transcription only
    - Implement 120-second timeout for OCR processing
    - _Requirements: 7.4, 7.5_

- [ ] 8. Implement Gemini summarization service

  - [ ] 8.1 Create Gemini summarizer for schema-specific summaries

    - Implement `services/gemini_summarizer.py` with `summarize()` method
    - Add `_build_prompt()` method to construct prompt with schema, transcription, OCR text, and user prompt
    - Call Gemini 1.5 Pro API requesting JSON output format
    - Implement `_parse_response()` to parse API response into structured data matching Notion schema
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

  - [ ] 8.2 Add validation and error handling
    - Validate parsed response against Notion schema structure
    - Handle API rate limits with exponential backoff
    - Update Link Database status to "saving" on success or "failed" on failure
    - _Requirements: 8.5, 8.6_

- [ ] 9. Implement Notion content writer

  - [ ] 9.1 Create content writer to save to Content Databases

    - Implement method in `clients/notion_client.py` to create pages with structured data
    - Retrieve db_id from notion_schemas table based on tag
    - Map summarized data fields to Notion database properties
    - Include original video_link in the created page
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

  - [ ] 9.2 Add status updates and error handling
    - Update Link Database status to "completed" on successful page creation
    - Update status to "failed" with error message on failure
    - _Requirements: 9.5, 9.6_

- [ ] 10. Implement processing pipeline orchestrator

  - [ ] 10.1 Create pipeline orchestrator

    - Implement `services/processing_pipeline.py` with `process_entry()` method
    - Orchestrate sequential execution: download → transcribe → OCR → summarize → save
    - Inject all service dependencies (downloader, whisper, ocr, summarizer, notion_client)
    - Add `_update_status()` helper method to update Link Database at each stage
    - _Requirements: 5.1, 6.5, 8.6, 9.5_

  - [ ] 10.2 Add cleanup and error handling
    - Implement `_cleanup_temp_files()` method to delete video and audio files
    - Call cleanup after successful completion or failure
    - Handle exceptions at each pipeline stage and update status accordingly
    - _Requirements: 11.1, 11.2_

- [ ] 11. Implement database monitor background worker

  - [ ] 11.1 Create database monitor service

    - Implement `services/database_monitor.py` with `start_monitoring()` method
    - Add `check_for_new_entries()` method to query Link Database for entries with status='pending'
    - Poll every 60 seconds for new entries
    - Validate URL is from TikTok or Instagram
    - Validate tag matches a registered Content Database
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [ ] 11.2 Add queue management
    - Implement `queue_for_processing()` method to add entries to processing_queue table
    - Create background thread or async task to process queued entries
    - Call ProcessingPipeline.process_entry() for each queued entry
    - Update status to "failed" if validation fails
    - _Requirements: 4.5_

- [ ] 12. Implement monitoring and logging

  - [ ] 12.1 Set up Grafana Cloud logging integration

    - Create `utils/logger.py` with Grafana Cloud log shipping configuration
    - Configure structured logging with JSON format
    - Add log levels: INFO, WARNING, ERROR
    - Include context in logs: user_id, entry_id, processing stage
    - _Requirements: 10.4, 10.5_

  - [ ] 12.2 Add health check endpoint

    - Implement `GET /health` endpoint in `app.py`
    - Check database connectivity
    - Check Notion API connectivity
    - Return status and timestamp
    - _Requirements: 12.4_

  - [ ] 12.3 Add status tracking
    - Update Link Database status field at each processing stage
    - Support status values: "pending", "downloading", "transcribing", "processing", "saving", "completed", "failed"
    - Update updated_time field on status changes
    - _Requirements: 10.1, 10.2, 10.3_

- [ ] 13. Implement cleanup job for temporary files

  - Create scheduled job in `services/cleanup_job.py` to run every 24 hours
  - Delete orphaned temporary files older than 24 hours from `/tmp` directory
  - Log all file deletion operations
  - _Requirements: 11.3, 11.4_

- [ ] 14. Create deployment configuration

  - [ ] 14.1 Create Cloud Run deployment files

    - Create `Dockerfile` with Python 3.11 base image and system dependencies (ffmpeg, postgresql-client)
    - Create `cloudbuild.yaml` for Google Cloud Build
    - Create `app.yaml` with Cloud Run configuration (scaling, env vars, VPC connector)
    - _Requirements: 12.1_

  - [ ] 14.2 Create deployment scripts
    - Create `scripts/deploy.sh` to build and deploy to Cloud Run
    - Create `scripts/setup_database.sh` to run database migrations
    - Add instructions in `README.md` for deployment process
    - _Requirements: 12.1_

- [ ]\* 15. Write integration tests

  - [ ]\* 15.1 Create test fixtures and utilities

    - Create `tests/fixtures/` directory with sample videos and Notion database schemas
    - Create `tests/conftest.py` with pytest fixtures for mocked services
    - Create test database setup and teardown utilities
    - _Requirements: All_

  - [ ]\* 15.2 Write end-to-end pipeline tests

    - Write `tests/test_pipeline.py` with test cases for complete processing flow
    - Test successful processing with cooking video example
    - Test processing with OCR failure (transcription only)
    - Test error handling for invalid URLs
    - _Requirements: All_

  - [ ]\* 15.3 Write service integration tests
    - Write `tests/test_notion_integration.py` for Notion API operations
    - Write `tests/test_video_downloader.py` for download functionality
    - Write `tests/test_whisper_service.py` for transcription
    - Write `tests/test_gemini_summarizer.py` for summarization
    - _Requirements: 5.1-5.6, 6.1-6.5, 8.1-8.6, 9.1-9.6_
