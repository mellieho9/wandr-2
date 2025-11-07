# Frontend-Backend Connection Guide

## What Was Connected

I've successfully connected your React frontend to the Flask backend! Here's what was implemented:

### 1. OAuth Authentication Flow ✅

**LandingPage.tsx** - Updated the "Continue with Notion" button:

```typescript
const handleNotionConnect = () => {
  // Redirects to Flask OAuth endpoint
  window.location.href = "/auth/notion/login";
};
```

When clicked, it redirects to `/auth/notion/login` which:

1. Redirects to Notion OAuth
2. User authorizes the app
3. Notion redirects back to `/auth/notion/callback`
4. Flask creates a session
5. User is redirected back to the frontend (authenticated)

### 2. Database Selection Component ✅

**DatabaseSelection.tsx** - New component that:

- Fetches available Notion databases from `/api/databases/available`
- Shows registered databases from `/api/databases`
- Allows users to register databases with tags
- Calls `/api/databases/register` to save selections

### 3. App Flow ✅

**App.tsx** - Updated to handle the complete flow:

1. **Check Authentication** - On load, checks if user has a session
2. **Landing Page** - Shows if not authenticated
3. **Database Selection** - Shows after OAuth login
4. **Setup Complete** - Shows after databases are registered

### 4. API Configuration ✅

**config.ts** - Centralized API endpoints:

- Uses relative URLs (Vite proxy handles routing in dev)
- All endpoints defined in one place
- Easy to update

## How to Test

### Step 1: Start Backend

```bash
# From project root
source .venv/bin/activate  # Activate virtual environment
flask run --host=0.0.0.0 --port=8080
```

### Step 2: Start Frontend

```bash
# In a new terminal
cd frontend
npm install  # First time only
npm run dev
```

### Step 3: Test the Flow

1. **Visit** http://localhost:3000
2. **Click** "Continue with Notion"
3. **Authorize** the app in Notion
4. **You'll be redirected back** to the database selection page
5. **Select a database** from the list
6. **Enter a tag** (e.g., "cooking", "places")
7. **Optionally add a prompt** for AI extraction
8. **Click** "Register Database"
9. **Repeat** for more databases
10. **Click** "Continue to Setup" when done

## API Endpoints Used

### Authentication

- `GET /auth/notion/login` - Initiates OAuth flow
- `GET /auth/notion/callback` - Handles OAuth callback

### Database Management

- `GET /api/databases/available` - Lists all Notion databases
- `GET /api/databases` - Lists registered databases
- `POST /api/databases/register` - Registers a Content Database

## Component Breakdown

### LandingPage.tsx

```typescript
// Real OAuth redirect (no more mock)
const handleNotionConnect = () => {
  window.location.href = "/auth/notion/login";
};
```

### DatabaseSelection.tsx

```typescript
// Fetch available databases
const response = await fetch("/api/databases/available", {
  credentials: "include", // Important: sends session cookie
});

// Register a database
await fetch("/api/databases/register", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  credentials: "include",
  body: JSON.stringify({ db_id, tag, prompt }),
});
```

### App.tsx

```typescript
// Check if user is authenticated
const checkAuthentication = async () => {
  const response = await fetch("/api/databases", {
    credentials: "include",
  });
  if (response.ok) {
    setIsAuthenticated(true);
  }
};
```

## Session Management

The backend uses Flask sessions with cookies:

- After OAuth, Flask sets a session cookie
- Frontend includes `credentials: 'include'` in all fetch requests
- This sends the session cookie automatically
- Backend validates the session on each request

## Development Proxy

Vite proxies API requests to Flask (configured in `vite.config.ts`):

```typescript
proxy: {
  '/api': 'http://localhost:8080',
  '/auth': 'http://localhost:8080',
  '/health': 'http://localhost:8080',
}
```

This means:

- Frontend: http://localhost:3000
- Backend: http://localhost:8080
- Requests to `/api/*` are automatically forwarded to Flask

## Troubleshooting

### "Cannot find module" errors

```bash
cd frontend
npm install
```

### OAuth redirect not working

- Make sure Flask is running on port 8080
- Check `.env` has correct `NOTION_REDIRECT_URI`
- Verify Notion OAuth app settings

### Session not persisting

- Ensure `credentials: 'include'` in all fetch calls
- Check `FLASK_SECRET_KEY` is set in `.env`
- Clear browser cookies and try again

### Databases not loading

- Check Flask backend is running
- Open browser DevTools > Network tab
- Look for failed API requests
- Check Flask logs for errors

### CORS errors

- Should not happen with Vite proxy
- If you see CORS errors, check proxy config in `vite.config.ts`

## Next Steps

1. ✅ OAuth flow is connected
2. ✅ Database selection is working
3. ⏭️ Add Link Database registration
4. ⏭️ Add video URL submission
5. ⏭️ Add processing status display

## Testing Checklist

- [ ] Frontend loads at http://localhost:3000
- [ ] Backend responds at http://localhost:8080/health
- [ ] Click "Continue with Notion" redirects to Notion
- [ ] After OAuth, redirected back to app
- [ ] Database selection page shows
- [ ] Available databases list loads
- [ ] Can select a database
- [ ] Can enter a tag
- [ ] Can register a database
- [ ] Registered database shows in list
- [ ] Can register multiple databases
- [ ] "Continue to Setup" button appears
- [ ] Setup complete page shows

## Files Modified/Created

### Modified

- `frontend/src/components/LandingPage.tsx` - Real OAuth redirect
- `frontend/src/App.tsx` - Auth check and flow management

### Created

- `frontend/src/components/DatabaseSelection.tsx` - Database selection UI
- `frontend/src/config.ts` - API endpoint configuration
- `FRONTEND_BACKEND_CONNECTION.md` - This guide

## Quick Commands

```bash
# Start both servers
./scripts/dev.sh

# Or manually:
# Terminal 1: Backend
flask run --host=0.0.0.0 --port=8080

# Terminal 2: Frontend
cd frontend && npm run dev

# Check health
curl http://localhost:8080/health

# Test API (after OAuth)
curl http://localhost:8080/api/databases/available \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

## Success! 🎉

Your frontend is now fully connected to the backend:

- ✅ Real OAuth authentication
- ✅ Database fetching from Notion
- ✅ Database registration
- ✅ Session management
- ✅ Complete user flow

Just run both servers and test it out!
