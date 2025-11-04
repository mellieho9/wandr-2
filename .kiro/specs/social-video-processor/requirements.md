# Requirements Document

## Introduction

The Social Video Processor is a cloud-hosted service that monitors a Notion link database for tagged TikTok and Instagram Reels URLs, automatically downloads videos, transcribes audio using Whisper, extracts text using OCR, and generates schema-specific summaries using Gemini API. The processed content is then saved to the appropriate Notion database based on user-defined tags and database schemas.

## Glossary

- **Social Video Processor**: The Flask-based service hosted on Google Cloud Run that orchestrates the entire video processing pipeline
- **Link Database**: A Notion database where users save video URLs with tags indicating the target Content Database
- **Content Database**: User-defined Notion databases (e.g., cooking, places, news) with specific schemas where processed content is stored
- **Notion Schema**: The structure of a Content Database including field names, types, and relationships stored in the system
- **Schema Prompt**: A user-defined or system-generated prompt that instructs Gemini API how to summarize content to fit a specific Notion Schema
- **Video Downloader**: The component that downloads videos from TikTok and Instagram platforms
- **Whisper Service**: The audio transcription service that converts video audio to text
- **OCR Service**: Google's OCR service that extracts visible text from video frames
- **Gemini Summarizer**: The component that uses Gemini API to generate schema-specific summaries from transcriptions and OCR content
- **Database Monitor**: The component that polls the Link Database for new entries to process
- **Tag**: A user-assigned label on a Link Database entry that maps to a specific Content Database

## Requirements

### Requirement 1

**User Story:** As a user, I want to authenticate with my Notion account using OAuth, so that the service can access my databases

#### Acceptance Criteria

1. THE Social Video Processor SHALL provide a Notion OAuth authentication flow
2. WHEN authentication is successful, THE Social Video Processor SHALL store the oauth_id in the User table
3. IF authentication fails, THEN THE Social Video Processor SHALL display an error message with the failure reason
4. THE Social Video Processor SHALL maintain valid OAuth tokens for API access

### Requirement 2

**User Story:** As a user, I want to register my Content Databases with their schemas and tags, so that the service knows where to save processed content

#### Acceptance Criteria

1. THE Social Video Processor SHALL allow users to select one or more Notion databases as Content Databases
2. WHEN a Content Database is selected, THE Social Video Processor SHALL retrieve and store the database schema in JSONB format
3. THE Social Video Processor SHALL require users to assign a unique tag to each Content Database
4. THE Social Video Processor SHALL allow users to provide a custom Schema Prompt for each Content Database
5. THE Social Video Processor SHALL store the mapping between user_id, db_id, tag, schema, and prompt in the notion_schema table

### Requirement 3

**User Story:** As a user, I want to create a Link Database in my Notion account, so that I can save video URLs for processing

#### Acceptance Criteria

1. THE Social Video Processor SHALL provide instructions for creating a Link Database with required fields: url, tag, processing_type, status, updated_time
2. THE Social Video Processor SHALL allow users to register their Link Database with the service
3. THE Social Video Processor SHALL validate that the Link Database contains the required fields
4. THE Social Video Processor SHALL store the Link Database ID for monitoring

### Requirement 4

**User Story:** As a user, I want to save TikTok or Instagram Reels URLs to my Link Database with a tag, so that they are processed and saved to the correct Content Database

#### Acceptance Criteria

1. WHEN a new entry is added to the Link Database, THE Database Monitor SHALL detect the new entry within 60 seconds
2. THE Database Monitor SHALL extract the url and tag fields from the Link Database entry
3. THE Database Monitor SHALL validate that the url is from TikTok or Instagram Reels
4. THE Database Monitor SHALL validate that the tag matches a registered Content Database
5. IF validation fails, THEN THE Social Video Processor SHALL update the status field to "failed" with an error message

### Requirement 5

**User Story:** As a user, I want videos to be downloaded automatically, so that they can be processed

#### Acceptance Criteria

1. WHEN a valid Link Database entry is detected, THE Video Downloader SHALL update the status field to "downloading"
2. THE Video Downloader SHALL download the video file from the provided url
3. THE Video Downloader SHALL handle platform-specific requirements for TikTok and Instagram
4. IF the download fails, THEN THE Video Downloader SHALL retry up to 3 times with exponential backoff
5. WHEN download completes successfully, THE Video Downloader SHALL store the video file temporarily and update status to "transcribing"
6. IF all download attempts fail, THEN THE Social Video Processor SHALL update status to "failed" with the error message

### Requirement 6

**User Story:** As a user, I want video audio to be transcribed using Whisper, so that spoken content is captured as text

#### Acceptance Criteria

1. WHEN a video is downloaded successfully, THE Whisper Service SHALL extract audio from the video file
2. THE Whisper Service SHALL transcribe the audio to text using the Whisper API
3. THE Whisper Service SHALL store the transcription in the video_content table
4. IF transcription fails, THEN THE Social Video Processor SHALL update status to "failed" with the error message
5. WHEN transcription completes, THE Whisper Service SHALL update status to "processing"

### Requirement 7

**User Story:** As a user, I want text visible in videos to be extracted using OCR, so that on-screen content is captured

#### Acceptance Criteria

1. WHEN a video is downloaded successfully, THE OCR Service SHALL extract key frames from the video
2. THE OCR Service SHALL apply Google's OCR to extract text from the frames
3. THE OCR Service SHALL store the extracted text in the ocr_content field of the video_content table
4. IF OCR fails, THEN THE Social Video Processor SHALL log the error but continue processing with transcription only
5. THE OCR Service SHALL complete processing within 120 seconds per video

### Requirement 8

**User Story:** As a user, I want content to be summarized according to my Content Database schema, so that it fits the structure of my database

#### Acceptance Criteria

1. WHEN transcription and OCR are complete, THE Gemini Summarizer SHALL retrieve the Schema Prompt for the tagged Content Database
2. THE Gemini Summarizer SHALL construct a prompt including the Schema Prompt, transcription, and OCR content
3. THE Gemini Summarizer SHALL call the Gemini API to generate a schema-specific summary
4. THE Gemini Summarizer SHALL parse the API response into structured data matching the Notion Schema
5. IF summarization fails, THEN THE Social Video Processor SHALL update status to "failed" with the error message
6. WHEN summarization completes, THE Gemini Summarizer SHALL update status to "saving"

### Requirement 9

**User Story:** As a user, I want processed content to be saved to the appropriate Content Database, so that I can access it in Notion

#### Acceptance Criteria

1. WHEN summarization is complete, THE Social Video Processor SHALL retrieve the db_id for the tagged Content Database
2. THE Social Video Processor SHALL create a new entry in the Content Database via Notion API
3. THE Social Video Processor SHALL populate the entry fields with the structured summary data
4. THE Social Video Processor SHALL include the original video_link in the Content Database entry
5. WHEN the entry is created successfully, THE Social Video Processor SHALL update the Link Database status to "completed"
6. IF entry creation fails, THEN THE Social Video Processor SHALL update status to "failed" with the error message

### Requirement 10

**User Story:** As a user, I want to monitor processing status and logs, so that I can troubleshoot issues

#### Acceptance Criteria

1. THE Social Video Processor SHALL update the status field in the Link Database at each processing stage
2. THE Social Video Processor SHALL support status values: "pending", "downloading", "transcribing", "processing", "saving", "completed", "failed"
3. THE Social Video Processor SHALL update the updated_time field whenever status changes
4. THE Social Video Processor SHALL send logs to Grafana Cloud for monitoring
5. THE Social Video Processor SHALL include error messages and stack traces in logs when failures occur

### Requirement 11

**User Story:** As a user, I want temporary video files to be cleaned up, so that storage costs are minimized

#### Acceptance Criteria

1. WHEN video processing completes with status "completed", THE Social Video Processor SHALL delete the temporary video file
2. WHEN video processing completes with status "failed", THE Social Video Processor SHALL delete the temporary video file
3. THE Social Video Processor SHALL run a cleanup job every 24 hours to delete orphaned temporary files
4. THE Social Video Processor SHALL log all file deletion operations

### Requirement 12

**User Story:** As a user, I want the service to be scalable and reliable, so that it can handle multiple videos concurrently

#### Acceptance Criteria

1. THE Social Video Processor SHALL be deployed on Google Cloud Run with auto-scaling enabled
2. THE Social Video Processor SHALL process multiple videos concurrently using asynchronous task queues
3. THE Social Video Processor SHALL handle API rate limits gracefully with exponential backoff
4. THE Social Video Processor SHALL implement health check endpoints for Cloud Run monitoring
5. THE Social Video Processor SHALL maintain 99% uptime for the monitoring and processing pipeline
