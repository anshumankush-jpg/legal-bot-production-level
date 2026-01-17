# Personalization Preferences System

## Overview

Complete end-to-end preferences system for LEGID/LegalAI that allows users to customize their experience. Preferences are persisted per user and automatically applied across the application.

## Features

- **Theme**: Dark, Light, or System (matches device)
- **Font Size**: Small, Medium, or Large
- **Response Style**: Concise, Detailed, or Legal Format
- **Language**: Interface language selection
- **Auto-Read Responses**: Toggle text-to-speech for AI responses

## Architecture

### Frontend (Angular)
- **PreferencesService**: Manages preferences state and API calls
- **API Interceptor**: Adds auth headers and base URL to all requests
- **PersonalizationComponent**: UI for editing preferences
- **AppComponent**: Loads preferences on app init to apply theme/fontSize

### Backend (FastAPI)
- **GET /api/preferences**: Retrieve user preferences
- **PUT /api/preferences**: Update user preferences
- **Database**: SQLite (dev) with `user_profiles.preferences_json` column
- **Auth**: JWT Bearer tokens or dev mode with `x-dev-user-id` header

## Setup Instructions

### 1. Backend Setup

```bash
cd backend

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Start backend server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies (if not already installed)
npm install

# Start Angular dev server
ng serve --port 4200
```

### 3. Environment Configuration

**Frontend** (`frontend/src/environments/environment.ts`):
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000',  // Backend API URL
  // ...
};
```

**Backend** (`.env` or environment variables):
```bash
# Database (SQLite for dev)
DATABASE_URL=sqlite:///./data/legal_bot.db

# JWT Secret (for production)
JWT_SECRET_KEY=your-secret-key-here
```

## API Endpoints

### GET /api/preferences

**Description**: Get current user's preferences.

**Authentication**: 
- Bearer token in `Authorization` header, OR
- `x-dev-user-id` header for local development

**Response**:
```json
{
  "theme": "dark",
  "fontSize": "medium",
  "responseStyle": "detailed",
  "language": "en",
  "autoReadResponses": false
}
```

**Example**:
```bash
# With auth token
curl -X GET http://localhost:8000/api/preferences \
  -H "Authorization: Bearer YOUR_TOKEN"

# Dev mode (no auth)
curl -X GET http://localhost:8000/api/preferences \
  -H "x-dev-user-id: dev-user-001"
```

### PUT /api/preferences

**Description**: Update user's preferences (partial update supported).

**Authentication**: Same as GET

**Request Body**:
```json
{
  "theme": "light",
  "fontSize": "large",
  "responseStyle": "concise",
  "language": "fr",
  "autoReadResponses": true
}
```

**Response**: Same format as GET, returns updated preferences

**Example**:
```bash
# With auth token
curl -X PUT http://localhost:8000/api/preferences \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "light",
    "fontSize": "large"
  }'

# Dev mode
curl -X PUT http://localhost:8000/api/preferences \
  -H "x-dev-user-id: dev-user-001" \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "light",
    "autoReadResponses": true
  }'
```

## Development Mode

For local development without full authentication:

1. **Set dev user ID** (optional):
   ```typescript
   // In browser console or localStorage
   localStorage.setItem('dev_user_id', 'my-test-user-123');
   ```

2. **The API interceptor automatically adds `x-dev-user-id` header** when:
   - Not in production mode
   - No auth token is present
   - Header value comes from `localStorage.getItem('dev_user_id')` or defaults to `'dev-user-001'`

3. **Backend accepts dev header** and uses it as `user_id` for preferences storage

## Data Model

### Database Schema

Preferences are stored in the `user_profiles` table:

```sql
CREATE TABLE user_profiles (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) UNIQUE NOT NULL,
    preferences_json JSON DEFAULT '{}',
    updated_at DATETIME NOT NULL,
    -- other fields...
);
```

### Preferences JSON Structure

```json
{
  "theme": "dark" | "light" | "system",
  "fontSize": "small" | "medium" | "large",
  "responseStyle": "concise" | "detailed" | "legal_format",
  "language": "en" | "fr" | "es" | "de",
  "autoReadResponses": true | false
}
```

## Frontend Usage

### Using PreferencesService

```typescript
import { PreferencesService } from './services/preferences.service';

constructor(private preferencesService: PreferencesService) {}

// Get preferences
this.preferencesService.getPreferences().subscribe(prefs => {
  console.log('Current preferences:', prefs);
});

// Save preferences
this.preferencesService.savePreferences({
  theme: 'light',
  fontSize: 'large'
}).subscribe(prefs => {
  console.log('Saved:', prefs);
});

// Get current preferences synchronously
const current = this.preferencesService.getCurrentPreferences();
```

### Subscribing to Changes

```typescript
this.preferencesService.preferences$.subscribe(prefs => {
  if (prefs) {
    // Preferences changed, update UI
    console.log('New preferences:', prefs);
  }
});
```

## Theme and Font Size Application

Preferences are automatically applied to the document root:

- **Theme**: Adds class `theme-dark`, `theme-light`, or `theme-system` to `<html>`
- **Font Size**: Adds class `font-small`, `font-medium`, or `font-large` to `<html>`

CSS variables are used for theming:
```css
.theme-dark {
  --bg-primary: #212121;
  --text-primary: #ececec;
  /* ... */
}
```

## Troubleshooting

### "Failed to save preferences" Error

**Possible causes:**
1. Backend not running
2. Wrong API URL in environment
3. CORS error
4. Authentication failure

**Solutions:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Verify `environment.apiUrl` is `http://localhost:8000`
3. Check browser console for CORS errors
4. Verify auth token or use dev mode with `x-dev-user-id` header

### Preferences Not Loading

**Check:**
1. Browser console for API errors
2. Network tab for failed requests
3. Backend logs for errors
4. Database connection

**Fallback:**
- Preferences service loads from `localStorage` if API fails
- Default preferences are used if nothing is stored

### Theme/Font Size Not Applying

**Check:**
1. Preferences are loaded: `console.log(preferencesService.getCurrentPreferences())`
2. CSS file is imported: `frontend/src/styles/preferences.css`
3. Classes are on `<html>` element: `document.documentElement.className`

### CORS Errors

**Backend CORS is configured for:**
- `http://localhost:4200` (Angular)
- `http://localhost:3000` (React)
- `http://localhost:5173` (Vite)

If you see CORS errors:
1. Verify frontend is running on one of these ports
2. Check backend `main.py` CORS configuration
3. Ensure `allow_credentials=True` is set

### Authentication Issues

**For local development:**
- Use dev mode with `x-dev-user-id` header
- Set `localStorage.setItem('dev_user_id', 'your-user-id')`
- Or use default `dev-user-001`

**For production:**
- Implement proper JWT authentication
- Store tokens securely (not in localStorage - use HttpOnly cookies)
- Remove dev mode header support

## Testing

### Manual Testing

1. **Start servers:**
   ```bash
   # Terminal 1: Backend
   cd backend && python -m uvicorn app.main:app --port 8000
   
   # Terminal 2: Frontend
   cd frontend && ng serve --port 4200
   ```

2. **Open browser:**
   - Navigate to `http://localhost:4200/personalization`
   - Change preferences
   - Verify save success message
   - Reload page - preferences should persist

3. **Test API directly:**
   ```bash
   # Get preferences
   curl http://localhost:8000/api/preferences -H "x-dev-user-id: test-user"
   
   # Update preferences
   curl -X PUT http://localhost:8000/api/preferences \
     -H "x-dev-user-id: test-user" \
     -H "Content-Type: application/json" \
     -d '{"theme":"light"}'
   ```

### Automated Testing

```bash
# Backend tests
cd backend
pytest tests/test_preferences.py

# Frontend tests
cd frontend
ng test
```

## Production Considerations

1. **Remove Dev Mode:**
   - Remove `x-dev-user-id` header support
   - Require proper JWT authentication
   - Remove dev user fallback

2. **Security:**
   - Use HttpOnly cookies for tokens (not localStorage)
   - Implement CSRF protection
   - Validate all input on backend

3. **Database:**
   - Use production database (PostgreSQL, MySQL, etc.)
   - Add indexes on `user_id`
   - Implement connection pooling

4. **Error Handling:**
   - Log errors to monitoring service
   - Return user-friendly error messages
   - Implement retry logic for network failures

## Files Changed

### Backend
- `backend/app/api/routes/preferences.py` (NEW)
- `backend/app/api/dependencies/auth.py` (NEW)
- `backend/app/main.py` (MODIFIED - added preferences router)

### Frontend
- `frontend/src/app/services/preferences.service.ts` (NEW)
- `frontend/src/app/interceptors/api.interceptor.ts` (NEW)
- `frontend/src/app/pages/personalization/personalization.component.ts` (MODIFIED)
- `frontend/src/app/app.component.ts` (MODIFIED - loads preferences on init)
- `frontend/src/main.ts` (MODIFIED - added interceptor)
- `frontend/src/styles/preferences.css` (NEW)

## Commands to Run

```bash
# 1. Start backend
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 2. Start frontend (in another terminal)
cd frontend
ng serve --port 4200

# 3. Test API
curl http://localhost:8000/api/preferences -H "x-dev-user-id: test-user"

# 4. Open browser
# Navigate to: http://localhost:4200/personalization
```

## Support

For issues:
1. Check browser console for errors
2. Check backend logs: `backend/logs/app.log`
3. Verify database connection
4. Test API endpoints with curl
5. Check CORS configuration
