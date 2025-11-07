# Frontend Integration Guide

This guide explains how the React frontend is integrated with the Flask backend.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Development Setup                     │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  React Dev Server (Vite)          Flask Backend          │
│  http://localhost:3000            http://localhost:8080  │
│         │                                  │              │
│         │  Proxy /api, /auth, /health     │              │
│         └─────────────────────────────────►              │
│                                                           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   Production Setup                       │
├─────────────────────────────────────────────────────────┤
│                                                           │
│              Flask Server (Cloud Run)                    │
│              http://your-app.run.app                     │
│                       │                                   │
│         ┌─────────────┴─────────────┐                   │
│         │                           │                    │
│    Static Files              API Endpoints               │
│    (React Build)             /api/*, /auth/*, /health    │
│    Served from               Handled by Flask            │
│    frontend/build/           Blueprints                  │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

## Directory Structure

```
wandr-2/
├── frontend/                    # React frontend (Vite + TypeScript)
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── config.ts           # API endpoint configuration
│   │   ├── App.tsx             # Main app component
│   │   └── main.tsx            # Entry point
│   ├── build/                  # Production build output (gitignored)
│   ├── package.json
│   ├── vite.config.ts          # Vite configuration with proxy
│   └── index.html
│
├── app.py                      # Flask app (serves frontend + API)
├── endpoints/                  # Flask API blueprints
│   ├── auth.py                # OAuth endpoints
│   ├── database.py            # Database management endpoints
│   └── health.py              # Health check
└── ...
```

## Development Workflow

### 1. Start Flask Backend

```bash
# In the root directory (wandr-2/)
flask run --host=0.0.0.0 --port=8080
```

The Flask backend will:

- Run on http://localhost:8080
- Serve API endpoints: `/api/*`, `/auth/*`, `/health`
- Attempt to serve frontend from `frontend/build/` (if built)

### 2. Start React Frontend (Development Mode)

```bash
# In a new terminal
cd frontend
npm install  # First time only
npm run dev
```

The Vite dev server will:

- Run on http://localhost:3000
- Provide hot module replacement (HMR)
- Proxy API requests to Flask backend (port 8080)
- Open browser automatically

### 3. Access the Application

- **Frontend**: http://localhost:3000 (with HMR)
- **Backend API**: http://localhost:8080/api/\*
- **Health Check**: http://localhost:8080/health

## Production Build

### Build the Frontend

```bash
cd frontend
npm run build
```

This creates an optimized production build in `frontend/build/`:

```
frontend/build/
├── index.html
├── assets/
│   ├── index-[hash].js
│   ├── index-[hash].css
│   └── ...
└── ...
```

### Serve from Flask

Once built, Flask automatically serves the frontend:

```bash
# Start Flask (from root directory)
flask run --host=0.0.0.0 --port=8080
```

Now visit http://localhost:8080 to see the production build served by Flask.

## API Integration

### Frontend Configuration

The frontend uses `frontend/src/config.ts` to determine API endpoints:

```typescript
// Development: Points to Flask backend
const API_BASE_URL = "http://localhost:8080";

// Production: Same origin (Flask serves both)
const API_BASE_URL = "";
```

### Making API Calls

Example API call from React:

```typescript
import { API_ENDPOINTS } from "./config";

// List available databases
const response = await fetch(API_ENDPOINTS.listAvailableDatabases, {
  credentials: "include", // Include cookies for session
});
const data = await response.json();
```

### Available Endpoints

| Endpoint                      | Method | Description                     |
| ----------------------------- | ------ | ------------------------------- |
| `/health`                     | GET    | Health check                    |
| `/auth/notion/login`          | GET    | Start OAuth flow                |
| `/auth/notion/callback`       | GET    | OAuth callback                  |
| `/api/databases`              | GET    | List registered databases       |
| `/api/databases/available`    | GET    | List available Notion databases |
| `/api/databases/register`     | POST   | Register Content Database       |
| `/api/link-database/register` | POST   | Register Link Database          |

## Vite Proxy Configuration

During development, Vite proxies API requests to Flask:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': 'http://localhost:8080',
    '/auth': 'http://localhost:8080',
    '/health': 'http://localhost:8080',
  }
}
```

This allows the frontend to make requests to `/api/databases` which are automatically forwarded to `http://localhost:8080/api/databases`.

## Flask Static File Serving

Flask is configured to serve the built frontend:

```python
# app.py
app = Flask(
    __name__,
    static_folder="frontend/build",
    static_url_path=""
)

@app.route("/")
def serve_frontend():
    """Serve React app"""
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    """Serve static assets or fallback to index.html"""
    # Serves JS, CSS, images, etc.
    # Falls back to index.html for client-side routing
```

## Session Management

The Flask backend uses session cookies for authentication:

```python
# Flask sets session cookie after OAuth
session['user_id'] = user.id

# Frontend includes credentials in requests
fetch(url, { credentials: 'include' })
```

## CORS Configuration (if needed)

If you need to enable CORS for development:

```bash
pip install flask-cors
```

```python
# app.py
from flask_cors import CORS

CORS(app, supports_credentials=True, origins=['http://localhost:3000'])
```

## Deployment to Cloud Run

### 1. Build Frontend

```bash
cd frontend
npm run build
```

### 2. Deploy Flask App

The `frontend/build/` directory is included in the Docker image:

```dockerfile
# Dockerfile
COPY frontend/build /app/frontend/build
```

### 3. Cloud Run serves everything

```
https://your-app.run.app/          → React app (index.html)
https://your-app.run.app/api/*     → Flask API
https://your-app.run.app/auth/*    → OAuth endpoints
```

## Troubleshooting

### Frontend not loading

**Problem**: Visiting http://localhost:8080 shows "Frontend not built yet"

**Solution**: Build the frontend first:

```bash
cd frontend && npm run build
```

### API requests failing in development

**Problem**: API calls from React dev server (port 3000) fail

**Solution**:

1. Ensure Flask is running on port 8080
2. Check Vite proxy configuration in `vite.config.ts`
3. Verify CORS is enabled if needed

### Session cookies not working

**Problem**: Authentication fails, session not persisting

**Solution**:

1. Use `credentials: 'include'` in fetch requests
2. Ensure Flask `SECRET_KEY` is set in `.env`
3. Check browser console for cookie errors

### Build errors

**Problem**: `npm run build` fails

**Solution**:

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

## Testing the Integration

### 1. Test Health Check

```bash
curl http://localhost:8080/health
```

### 2. Test Frontend Serving

```bash
# Build frontend
cd frontend && npm run build && cd ..

# Start Flask
flask run --host=0.0.0.0 --port=8080

# Visit in browser
open http://localhost:8080
```

### 3. Test OAuth Flow

1. Visit http://localhost:3000 (dev) or http://localhost:8080 (prod)
2. Click "Login with Notion"
3. Complete OAuth flow
4. Should redirect back with session cookie

### 4. Test API Endpoints

```bash
# Get session cookie from browser DevTools
# Then test API:

curl http://localhost:8080/api/databases/available \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

## Next Steps

1. **Update React components** to call the API endpoints
2. **Add error handling** for API failures
3. **Implement loading states** during API calls
4. **Add authentication guards** to protect routes
5. **Test OAuth flow** end-to-end
6. **Build and deploy** to Cloud Run

## Quick Reference

```bash
# Development
flask run --host=0.0.0.0 --port=8080  # Terminal 1
cd frontend && npm run dev             # Terminal 2

# Production build
cd frontend && npm run build           # Build frontend
flask run --host=0.0.0.0 --port=8080  # Serve from Flask

# Clean build
cd frontend
rm -rf build node_modules
npm install
npm run build
```
