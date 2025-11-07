# Frontend Integration Checklist

## ✅ Completed

- [x] Updated task 4.4 in `.kiro/specs/social-video-processor/tasks.md`
- [x] Modified `app.py` to serve React frontend
- [x] Created `frontend/src/config.ts` for API endpoints
- [x] Updated `frontend/vite.config.ts` with proxy configuration
- [x] Updated `.gitignore` for frontend build artifacts
- [x] Created `scripts/dev.sh` for easy development
- [x] Created comprehensive documentation:
  - [x] FRONTEND_INTEGRATION_GUIDE.md
  - [x] frontend/INTEGRATION.md
  - [x] QUICK_START.md
  - [x] INTEGRATION_SUMMARY.md
  - [x] API_ENDPOINTS.md (already existed)

## 🔄 Next Steps (To Implement Task 4.4)

### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 2. Update React Components to Use API

Create or update these components:

#### a. OAuth Login Component

```typescript
// Example: src/components/Login.tsx
import { API_ENDPOINTS } from "../config";

export function Login() {
  const handleLogin = () => {
    window.location.href = API_ENDPOINTS.notionLogin;
  };

  return <button onClick={handleLogin}>Login with Notion</button>;
}
```

#### b. Database List Component

```typescript
// Example: src/components/DatabaseList.tsx
import { useState, useEffect } from "react";
import { API_ENDPOINTS } from "../config";

export function DatabaseList() {
  const [databases, setDatabases] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(API_ENDPOINTS.listAvailableDatabases, {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => {
        setDatabases(data.databases);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch databases:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>Available Databases</h2>
      <ul>
        {databases.map((db) => (
          <li key={db.id}>{db.title}</li>
        ))}
      </ul>
    </div>
  );
}
```

#### c. Database Registration Form

```typescript
// Example: src/components/RegisterDatabase.tsx
import { useState } from "react";
import { API_ENDPOINTS } from "../config";

export function RegisterDatabase() {
  const [dbId, setDbId] = useState("");
  const [tag, setTag] = useState("");
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(API_ENDPOINTS.registerContentDatabase, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ db_id: dbId, tag, prompt }),
      });

      if (!response.ok) {
        const error = await response.json();
        alert(error.error);
        return;
      }

      alert("Database registered successfully!");
      setDbId("");
      setTag("");
      setPrompt("");
    } catch (err) {
      alert("Failed to register database");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Database ID"
        value={dbId}
        onChange={(e) => setDbId(e.target.value)}
        required
      />
      <input
        type="text"
        placeholder="Tag (e.g., cooking)"
        value={tag}
        onChange={(e) => setTag(e.target.value)}
        required
      />
      <textarea
        placeholder="Custom prompt (optional)"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      />
      <button type="submit" disabled={loading}>
        {loading ? "Registering..." : "Register Database"}
      </button>
    </form>
  );
}
```

### 3. Test Development Setup

```bash
# Start both servers
./scripts/dev.sh

# Or manually:
# Terminal 1
flask run --host=0.0.0.0 --port=8080

# Terminal 2
cd frontend && npm run dev
```

Visit http://localhost:3000

### 4. Test OAuth Flow

1. Click "Login with Notion" button
2. Complete OAuth on Notion
3. Verify redirect back to app
4. Check session cookie in DevTools

### 5. Test API Integration

1. List available databases
2. Register a Content Database
3. List registered databases
4. Register Link Database

### 6. Build for Production

```bash
cd frontend
npm run build
cd ..
```

### 7. Test Production Build

```bash
flask run --host=0.0.0.0 --port=8080
```

Visit http://localhost:8080

### 8. Mark Task 4.4 as Complete

Once everything works:

```bash
# Update tasks.md to mark 4.4 as done
```

## 📝 Testing Checklist

- [ ] Frontend dependencies installed (`npm install`)
- [ ] Development servers start successfully
- [ ] Frontend loads at http://localhost:3000
- [ ] API proxy works (no CORS errors)
- [ ] Health check endpoint responds
- [ ] OAuth login redirects to Notion
- [ ] OAuth callback returns to app
- [ ] Session cookie is set
- [ ] Can list available databases
- [ ] Can register Content Database
- [ ] Can register Link Database
- [ ] Can list registered databases
- [ ] Production build completes
- [ ] Flask serves production build
- [ ] All features work in production mode

## 🐛 Common Issues & Solutions

### Issue: `npm install` fails

**Solution:**

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: Proxy not working

**Solution:** Check that Flask is running on port 8080 and Vite config has correct proxy settings.

### Issue: Session not persisting

**Solution:** Ensure `credentials: 'include'` in all fetch requests and `FLASK_SECRET_KEY` is set.

### Issue: Frontend not loading from Flask

**Solution:** Build the frontend first: `cd frontend && npm run build`

### Issue: CORS errors

**Solution:** Use the proxy in development or ensure Flask is serving the frontend in production.

## 📚 Documentation

- [Quick Start](QUICK_START.md) - Fast setup guide
- [Integration Guide](FRONTEND_INTEGRATION_GUIDE.md) - Detailed integration docs
- [Frontend Docs](frontend/INTEGRATION.md) - Frontend-specific guide
- [API Reference](API_ENDPOINTS.md) - Complete API documentation
- [Testing Guide](TESTING_GUIDE.md) - API testing with curl

## 🎯 Success Criteria for Task 4.4

Task 4.4 is complete when:

1. ✅ React frontend is built and integrated
2. ✅ Flask serves the frontend at `/`
3. ✅ OAuth flow works through the UI
4. ✅ Users can list available Notion databases
5. ✅ Users can register Content Databases
6. ✅ Users can register Link Database
7. ✅ All API endpoints are accessible from UI
8. ✅ Development and production modes both work
9. ✅ Documentation is complete

## 🚀 Ready to Start!

Everything is set up. You can now:

1. Run `./scripts/dev.sh` to start development
2. Update React components to use the API
3. Test the OAuth and database endpoints
4. Build for production when ready

Good luck! 🎉
