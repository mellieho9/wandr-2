# Product Overview

Social Video Processor is a cloud-hosted service that automates content extraction from social media videos. Users save TikTok and Instagram Reels URLs to a Notion Link Database with tags, and the service automatically downloads videos, transcribes audio using Whisper, extracts on-screen text via OCR, generates schema-specific summaries using Gemini API, and saves structured content to user-defined Notion Content Databases.

## Core Workflow

1. User authenticates with Notion OAuth
2. User registers Content Databases (e.g., cooking, places, news) with custom schemas and tags
3. User creates a Link Database in Notion with required fields
4. User adds video URLs with tags to Link Database
5. Service monitors Link Database, processes videos through pipeline, and saves structured content to appropriate Content Database

## Key Features

- Multi-platform video download (TikTok, Instagram Reels)
- Audio transcription via Whisper API
- Text extraction from video frames via Google Vision OCR
- Schema-aware content summarization via Gemini API
- Automatic mapping to user-defined Notion databases
- Real-time status tracking and error reporting
- Scalable cloud-native architecture on Google Cloud Run
