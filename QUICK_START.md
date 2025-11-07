# Quick Start Guide

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL database
- Notion OAuth credentials

## Setup

### 1. Clone and Install Backend

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Generate Prisma client
prisma generate

# Set up database
prisma db push
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:

- `NOTION_CLIENT_ID` and `NOTION_CLIENT_SECRET`
- `DATABASE_URL` (PostgreSQL connection string)
- `FLASK_SECRET_KEY` (random string for sessions)

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

## Development

### Option 1: Run Both Servers (Recommended)

```bash
./scripts/dev.sh
```

This starts:

- Flask backend on http://localhost:8080
- React frontend on http://localhost:3000 (with hot reload)

### Option 2: Run Separately

```bash
# Terminal 1: Backend
flask run --host=0.0.0.0 --port=8080

# Terminal 2: Frontend
cd frontend && npm run dev
```

## Testing the Integration

### 1. Check Health

```bash
curl http://localhost:8080/health
```

### 2. Test OAuth Flow

1. Visit http://localhost:3000
2. Click "Login with Notion"
3. Complete OAuth flow
4. You should be redirected back with a session

### 3. Test API Endpoints

```bash
# Get your session cookie from browser DevTools
# Then test:

curl http://localhost:8080/api/databases/available \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

## Production Build

### Build Frontend

```bash
cd frontend
npm run build
cd ..
```

### Run Production Server

```bash
flask run --host=0.0.0.0 --port=8080
```

Visit http://localhost:8080 to see the production build.

## Project Structure

```
wandr-2/
├── frontend/              # React + Vite frontend
│   ├── src/
│   │   ├── config.ts     # API endpoint configuration
│   │   └── ...
│   ├── build/            # Production build (gitignored)
│   └── package.json
│
├── app.py                # Flask app (serves frontend + API)
├── endpoints/            # API blueprints
│   ├── auth.py          # OAuth endpoints
│   ├── database.py      # Database management
│   └── health.py        # Health check
├── services/            # Business logic
├── clients/             # External API clients
├── utils/               # Utilities
└── prisma/              # Database schema
```

## Key Features

### Backend (Flask)

- ✅ Notion OAuth authentication
- ✅ Database registration endpoints
- ✅ List available Notion databases
- ✅ Session management with Redis fallback
- ✅ Serves React frontend in production

### Frontend (React + Vite)

- ✅ Modern React with TypeScript
- ✅ Radix UI components
- ✅ Tailwind CSS styling
- ✅ Hot module replacement in dev
- ✅ Proxy to Flask backend
- ✅ API integration ready

## Next Steps

1. **Update React components** to use the API endpoints
2. **Implement OAuth UI** in the frontend
3. **Add database registration forms**
4. **Test end-to-end flow**
5. **Deploy to Cloud Run**

## Documentation

- [Frontend Integration Guide](FRONTEND_INTEGRATION_GUIDE.md) - Detailed integration docs
- [Testing Guide](TESTING_GUIDE.md) - API testing with curl
- [API Endpoints](API_ENDPOINTS.md) - Complete API reference
- [Deployment Checklist](DEPLOYMENT_CHECKLIST.md) - Production deployment

## Troubleshooting

### Frontend not loading

```bash
cd frontend && npm run build
```

### API calls failing

- Check Flask is running on port 8080
- Verify proxy configuration in `vite.config.ts`
- Ensure `credentials: 'include'` in fetch requests

### Database errors

```bash
prisma generate
prisma db push
```

### Session not persisting

- Check `FLASK_SECRET_KEY` is set in `.env`
- Verify cookies are enabled in browser
- Use `credentials: 'include'` in API calls

## Support

For issues or questions, check:

- [Frontend Integration](frontend/INTEGRATION.md)
- [API Documentation](API_ENDPOINTS.md)
- [Testing Guide](TESTING_GUIDE.md)
