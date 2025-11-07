# Testing Guide for Social Video Processor

## Prerequisites

1. **Environment Variables**: Ensure `.env` file is configured with:

   - `NOTION_CLIENT_ID`
   - `NOTION_CLIENT_SECRET`
   - `NOTION_REDIRECT_URI=http://localhost:8080/auth/notion/callback`
   - `DATABASE_URL` (PostgreSQL connection string)
   - `FLASK_SECRET_KEY` (any random string for session management)

2. **Database**: Run Prisma migrations:

   ```bash
   prisma generate
   prisma db push
   ```

3. **Dependencies**: Install all requirements:
   ```bash
   pip install -r requirements.txt
   cd frontend && npm install
   ```

## Running the Application

### 1. Build the Frontend

```bash
cd frontend
npm run build
cd ..
```

### 2. Start the Flask Server

```bash
python app.py
```

The server will start on `http://localhost:8080`

## Testing the OAuth Flow

### Step 1: Access the Landing Page

1. Open your browser and navigate to `http://localhost:8080`
2. You should see the landing page with "Continue with Notion" button

### Step 2: Initiate OAuth

1. Click the "Continue with Notion" button
2. You will be redirected to Notion's OAuth authorization page
3. Log in to your Notion account if not already logged in
4. Grant permissions to the application

### Step 3: OAuth Callback

1. After authorization, you'll be redirected back to `http://localhost:8080/?success=true&user_id=<id>`
2. The app should automatically detect the successful OAuth and show the Database Selection page

## Testing Database Registration

### Step 1: View Available Databases

1. After successful OAuth, you should see a list of your Notion databases
2. Each database will show its icon (emoji) and title

### Step 2: Select Databases

1. Check the boxes next to databases you want to register
2. For each selected database, a tag input field will appear
3. Enter a unique tag for each database (e.g., "places", "restaurants", "cooking")

### Step 3: Register Databases

1. Click the "Continue" button
2. The app will register each selected database with the backend
3. On success, you'll see a confirmation message: "You're all set"

## Testing API Endpoints Manually

### Health Check

```bash
curl http://localhost:8080/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2025-11-06T..."
}
```

### List Available Databases (requires authentication)

```bash
curl -b cookies.txt http://localhost:8080/api/databases/available
```

### Register Content Database (requires authentication)

```bash
curl -X POST http://localhost:8080/api/databases/register \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "db_id": "your-database-id",
    "tag": "places"
  }'
```

### List Registered Databases (requires authentication)

```bash
curl -b cookies.txt http://localhost:8080/api/databases
```

## Troubleshooting

### Frontend Not Loading

- Ensure `frontend/build` directory exists with `index.html` and `assets/` folder
- Rebuild frontend: `cd frontend && npm run build`

### OAuth Errors

- Verify `NOTION_CLIENT_ID` and `NOTION_CLIENT_SECRET` are correct
- Ensure `NOTION_REDIRECT_URI` matches exactly what's configured in Notion OAuth settings
- Check that Redis or in-memory state storage is working (check logs)

### Database Connection Errors

- Verify PostgreSQL is running
- Check `DATABASE_URL` is correct
- Run `prisma db push` to ensure schema is up to date

### CORS Errors

- The app is configured to allow CORS from `http://localhost:8080` and `http://127.0.0.1:8080`
- If accessing from a different origin, update the CORS configuration in `app.py`

## Expected Behavior

1. **Landing Page**: Shows marketing content and OAuth button
2. **OAuth Flow**: Redirects to Notion, then back to app with success parameters
3. **Database Selection**: Fetches and displays user's Notion databases
4. **Registration**: Saves selected databases with tags to PostgreSQL
5. **Completion**: Shows success message

## Next Steps After Testing

Once OAuth and database registration are working:

1. Create a Link Database in Notion with required fields (url, tag, processing_type, status, updated_time)
2. Register the Link Database using the `/api/link-database/register` endpoint
3. Add video URLs to the Link Database
4. The background monitor will detect and process them (to be implemented in future tasks)
