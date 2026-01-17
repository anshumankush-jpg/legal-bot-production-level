# Quick Start Guide - Profile System

## 🚀 Start the Application

### Backend (Terminal 1)
```bash
cd c:\Users\anshu\Downloads\production_level\backend
uvicorn app.main:app --reload --port 8000
```

### Frontend (Terminal 2)
```bash
cd c:\Users\anshu\Downloads\production_level\frontend
npm start
```

**Access**: http://localhost:4200

---

## 📋 Environment Setup (If Not Done)

### Backend `.env`
Create `backend/.env`:
```env
OPENAI_API_KEY=your_key
BIGQUERY_PROJECT_ID=your-project
BIGQUERY_DATASET=legalai
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
GCS_BUCKET=legalai-avatars
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-secret
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-secret
JWT_SECRET_KEY=min-32-character-secret-key
```

### Frontend Environment
Edit `frontend/src/environments/environment.ts`:
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000',
  googleClientId: 'your-google-client-id.apps.googleusercontent.com',
  microsoftClientId: 'your-microsoft-client-id'
};
```

---

## 🗄️ Database Setup

### Create BigQuery Tables
```bash
bq query --use_legacy_sql=false < backend/docs/bigquery_schema.sql
```

### Add Your First User
```sql
INSERT INTO `legalai.identity_users` 
(user_id, auth_provider, auth_uid, email, role, lawyer_status, is_provisioned, env)
VALUES (
  GENERATE_UUID(),
  'google',
  'your-oauth-id',
  'you@example.com',
  'admin',
  'not_applicable',
  TRUE,
  'dev'
);
```

---

## ✅ Test the Features

### 1. Profile Menu
- Click avatar in **bottom-left** sidebar
- Menu should open with:
  - Profile header (with camera icon)
  - Personalization
  - Settings  
  - Help (with submenu)
  - Log out
  - Account card at bottom

### 2. Edit Profile
- Click profile header in menu
- Modal opens with:
  - Avatar upload (click camera icon)
  - Display name input
  - Username input (validates uniqueness)
  - Email (read-only)
  - Phone + address fields
  - Cancel/Save buttons

### 3. Personalization
- Navigate to `/personalization`
- Change theme, font size, response style
- Changes save automatically (1-second delay)

### 4. Settings
- Navigate to `/settings`
- View account info
- Toggle cookie consent
- Test "Logout all devices"

### 5. Help
- Navigate to `/help`
- Test all tabs:
  - Help Center (FAQ)
  - Release Notes
  - Terms & Policies
  - Report Bug
  - Keyboard Shortcuts
  - Download Apps

---

## 📁 Key Files

### Frontend
- **Profile Menu**: `frontend/src/app/components/sidebar-profile-menu/`
- **Edit Modal**: `frontend/src/app/components/edit-profile-modal/`
- **Personalization**: `frontend/src/app/pages/personalization/`
- **Settings**: `frontend/src/app/pages/settings/`
- **Help**: `frontend/src/app/pages/help/`

### Backend
- **Profile API**: `backend/app/api/routes/profile.py`
- **DB Schema**: `backend/docs/bigquery_schema.sql`

### Documentation
- **Complete Guide**: `PROFILE_ACCOUNT_SYSTEM_COMPLETE.md`
- **Summary**: `IMPLEMENTATION_SUMMARY.md`
- **This File**: `QUICK_START_PROFILE_SYSTEM.md`

---

## 🔧 Troubleshooting

### "Not provisioned" error
Check BigQuery:
```sql
SELECT * FROM legalai.identity_users WHERE email='your@email.com';
```
Ensure `is_provisioned = TRUE`

### Avatar upload fails
- Check GCS bucket exists: `legalai-avatars`
- Verify service account permissions
- Check CORS configuration on bucket

### Username "already taken"
```sql
SELECT username FROM legalai.user_profiles WHERE LOWER(username) = LOWER('testuser');
```

### API errors
- Check backend logs: `backend/backend_detailed.log`
- Test endpoint: http://localhost:8000/docs
- Verify JWT token is valid

---

## 📞 Quick Commands

```bash
# View backend logs
tail -f backend/backend_detailed.log

# Query user in BigQuery
bq query "SELECT * FROM legalai.identity_users LIMIT 5"

# Test API endpoint
curl -X GET "http://localhost:8000/api/me" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Restart backend
cd backend && uvicorn app.main:app --reload --port 8000

# Restart frontend
cd frontend && npm start
```

---

## 🎯 What You Built

✅ Complete ChatGPT-style profile system  
✅ Full backend API (12 endpoints)  
✅ BigQuery database (6 tables)  
✅ Avatar upload to GCS  
✅ Username validation  
✅ Preferences auto-save  
✅ Multi-device logout  
✅ Role-based access control  
✅ Provisioning system  
✅ Help center with FAQs  
✅ Production-ready code  

**Ready to deploy!** 🚀

---

For complete documentation, see `PROFILE_ACCOUNT_SYSTEM_COMPLETE.md`
