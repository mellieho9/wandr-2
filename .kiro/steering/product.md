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

## User Interface

The application includes a React frontend that provides:

- **Landing Page**: Marketing content and OAuth login button
- **Database Selection**: Browse and select Notion databases to register
- **Database Registration**: Assign tags and custom prompts to databases
- **Setup Completion**: Confirmation after successful configuration

### Frontend-Backend Integration

- **Development Mode**: React dev server (port 3000) proxies API calls to Flask (port 8080)
- **Production Mode**: Flask serves the built React app and API endpoints from a single server
- **Session Management**: Flask session cookies for authentication, included in all API requests
- **OAuth Flow**: Seamless redirect to Notion → callback → authenticated session

## Testing Workflows

### Local Development Testing

1. Start Flask backend: `flask run --host=0.0.0.0 --port=8080`
2. Start React frontend: `cd frontend && npm run dev`
3. Visit http://localhost:3000
4. Test OAuth flow and database registration

### Production Build Testing

1. Build frontend: `cd frontend && npm run build`
2. Start Flask: `flask run --host=0.0.0.0 --port=8080`
3. Visit http://localhost:8080
4. Verify all features work with production build

### API Testing

Use curl or browser DevTools to test endpoints:

- Health check: `curl http://localhost:8080/health`
- List databases: `curl http://localhost:8080/api/databases/available -H "Cookie: session=..."`
- Register database: `curl -X POST http://localhost:8080/api/databases/register -d '{"db_id":"...","tag":"..."}' -H "Content-Type: application/json" -H "Cookie: session=..."`
