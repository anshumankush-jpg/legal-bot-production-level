# Preferences System Implementation Summary

## ✅ Implementation Complete

The complete end-to-end preferences system has been implemented for LEGID/LegalAI.

## 📁 Files Created/Modified

### Backend Files

1. **`backend/app/api/routes/preferences.py`** (NEW)
   - `GET /api/preferences` - Get user preferences
   - `PUT /api/preferences` - Update user preferences
   - Dev mode support with `x-dev-user-id` header

2. **`backend/app/api/dependencies/auth.py`** (NEW)
   - `get_current_user` dependency for JWT authentication
   - Supports Bearer tokens in Authorization header

3. **`backend/app/api/dependencies/__init__.py`** (NEW)
   - Module init file

4. **`backend/app/main.py`** (MODIFIED)
   - Added preferences router inclusion

### Frontend Files

1. **`frontend/src/app/services/preferences.service.ts`** (NEW)
   - `getPreferences()` - Load preferences from backend
   - `savePreferences()` - Save preferences to backend
   - `getCurrentPreferences()` - Get current preferences synchronously
   - `preferences$` - Observable for preference changes
   - Auto-applies theme and fontSize to document root
   - localStorage fallback

2. **`frontend/src/app/interceptors/api.interceptor.ts`** (NEW)
   - Adds base API URL from environment
   - Adds Authorization header with Bearer token
   - Adds `x-dev-user-id` header for local development
   - Handles relative and absolute URLs

3. **`frontend/src/app/pages/personalization/personalization.component.ts`** (MODIFIED)
   - Uses PreferencesService instead of direct HTTP calls
   - Proper error handling with MatSnackBar
   - Loading states
   - Field name mapping (fontSize, responseStyle, autoReadResponses)

4. **`frontend/src/app/app.component.ts`** (MODIFIED)
   - Loads preferences on app init
   - Applies theme/fontSize immediately

5. **`frontend/src/main.ts`** (MODIFIED)
   - Added API interceptor to HTTP client

6. **`frontend/src/styles/preferences.css`** (NEW)
   - Theme CSS variables (dark, light, system)
   - Font size classes (small, medium, large)

## 🎯 Features Implemented

### ✅ Backend
- [x] GET /api/preferences endpoint
- [x] PUT /api/preferences endpoint
- [x] Persistence to SQLite database (user_profiles.preferences_json)
- [x] Dev mode with x-dev-user-id header
- [x] JWT authentication support
- [x] Error handling and logging

### ✅ Frontend
- [x] PreferencesService with BehaviorSubject
- [x] HTTP interceptor for auth and base URL
- [x] Personalization component integration
- [x] Theme application (dark/light/system)
- [x] Font size application (small/medium/large)
- [x] Error handling with snackbars
- [x] Loading states
- [x] localStorage fallback

### ✅ Preferences Supported
- [x] theme: "dark" | "light" | "system"
- [x] fontSize: "small" | "medium" | "large"
- [x] responseStyle: "concise" | "detailed" | "legal_format"
- [x] language: string (e.g., "en", "fr", "es", "de")
- [x] autoReadResponses: boolean

## 🚀 How to Run

### 1. Start Backend

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start Frontend

```bash
cd frontend
ng serve --port 4200
```

### 3. Test the Feature

1. Open browser: `http://localhost:4200/personalization`
2. Change preferences (theme, fontSize, etc.)
3. Click outside or wait 1 second for auto-save
4. Verify success message appears
5. Reload page - preferences should persist

### 4. Test API Directly

```bash
# Get preferences (dev mode)
curl http://localhost:8000/api/preferences \
  -H "x-dev-user-id: test-user-123"

# Update preferences
curl -X PUT http://localhost:8000/api/preferences \
  -H "x-dev-user-id: test-user-123" \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "light",
    "fontSize": "large",
    "autoReadResponses": true
  }'
```

## 🔧 Configuration

### Environment Variables

**Frontend** (`frontend/src/environments/environment.ts`):
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000',  // Backend URL
  // ...
};
```

**Backend** (`.env` or system):
```bash
DATABASE_URL=sqlite:///./data/legal_bot.db
JWT_SECRET_KEY=your-secret-key
```

### Dev Mode

For local development without authentication:

1. **Set dev user ID** (optional):
   ```javascript
   // In browser console
   localStorage.setItem('dev_user_id', 'my-test-user');
   ```

2. **The interceptor automatically adds `x-dev-user-id` header** when:
   - Not in production
   - No auth token present
   - Uses `localStorage.getItem('dev_user_id')` or defaults to `'dev-user-001'`

## 🐛 Troubleshooting

### "Failed to save preferences"

**Check:**
1. Backend is running: `curl http://localhost:8000/health`
2. API URL is correct: Check `environment.apiUrl`
3. CORS is configured: Backend allows `localhost:4200`
4. Browser console for errors

**Solution:**
- Verify backend logs show request received
- Check network tab for failed requests
- Ensure interceptor is working (check request headers)

### Preferences Not Loading

**Check:**
1. Browser console for API errors
2. Network tab - is request sent?
3. Backend logs - is request received?
4. Database - does user_profile exist?

**Solution:**
- Check API URL in environment.ts
- Verify interceptor is registered in main.ts
- Test API directly with curl

### Theme/Font Size Not Applying

**Check:**
1. Preferences loaded: `console.log(preferencesService.getCurrentPreferences())`
2. CSS imported: Check `app.component.ts` imports preferences.css
3. Classes on HTML: `document.documentElement.className`

**Solution:**
- Ensure preferences.css is imported
- Check CSS variables are defined
- Verify classes are added to `<html>` element

### CORS Errors

**Backend CORS is configured for:**
- `http://localhost:4200` ✅
- `http://localhost:3000`
- `http://localhost:5173`

**If you see CORS errors:**
1. Verify frontend runs on port 4200
2. Check backend `main.py` CORS config
3. Ensure `allow_credentials=True`

## 📚 Documentation

Full documentation available at:
- **`docs/personalization.md`** - Complete setup and usage guide

## ✨ Key Features

1. **Automatic Persistence**: Preferences save automatically after 1 second of inactivity
2. **Real-time Application**: Theme and fontSize apply immediately
3. **Error Recovery**: Falls back to localStorage if API fails
4. **Dev Mode**: Works without full authentication for local testing
5. **Type Safety**: Full TypeScript interfaces for preferences

## 🎉 Summary

The preferences system is **fully implemented** and ready for use:
- ✅ Backend API endpoints
- ✅ Database persistence
- ✅ Frontend service and component
- ✅ HTTP interceptor
- ✅ Theme/fontSize application
- ✅ Error handling
- ✅ Documentation

Follow the setup instructions in `docs/personalization.md` to get started!
