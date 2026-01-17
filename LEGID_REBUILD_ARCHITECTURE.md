# LEGID REBUILD - PRODUCTION ARCHITECTURE

## OVERVIEW
Complete rebuild of LEGID LegalAI to match ChatGPT-style UI with dark theme, resources sidebar, and full production functionality.

## FOLDER STRUCTURE

```
production_level/
├── frontend/                     # React 18 frontend
│   ├── src/
│   │   ├── app/                  # Main app structure
│   │   │   ├── App.jsx           # Root component
│   │   │   ├── App.css           # Global dark theme styles
│   │   │   └── router.jsx        # React Router setup
│   │   ├── pages/                # Page components
│   │   │   ├── auth/
│   │   │   │   ├── LoginPage.jsx
│   │   │   │   ├── RegisterPage.jsx
│   │   │   │   ├── RoleSelectPage.jsx
│   │   │   │   └── LawyerVerificationPage.jsx
│   │   │   ├── chat/
│   │   │   │   └── ChatPage.jsx  # Main chat interface
│   │   │   ├── resources/
│   │   │   │   ├── RecentUpdatesPage.jsx
│   │   │   │   ├── CaseLookupPage.jsx
│   │   │   │   ├── AmendmentsPage.jsx
│   │   │   │   ├── DocumentsPage.jsx
│   │   │   │   └── ... (other resources)
│   │   │   ├── PersonalizationPage.jsx
│   │   │   ├── SettingsPage.jsx
│   │   │   ├── HelpPage.jsx
│   │   │   └── ImagesPage.jsx
│   │   ├── components/           # Reusable components
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.jsx   # Left sidebar with resources grid
│   │   │   │   ├── TopBar.jsx    # Profile + controls
│   │   │   │   └── MainLayout.jsx
│   │   │   ├── chat/
│   │   │   │   ├── MessageList.jsx
│   │   │   │   ├── MessageBubble.jsx
│   │   │   │   ├── Composer.jsx
│   │   │   │   └── TypingIndicator.jsx
│   │   │   ├── profile/
│   │   │   │   ├── ProfileDropdown.jsx
│   │   │   │   └── EditProfileModal.jsx
│   │   │   ├── resources/
│   │   │   │   └── ResourceTile.jsx
│   │   │   └── common/
│   │   │       ├── Button.jsx
│   │   │       ├── Input.jsx
│   │   │       └── Modal.jsx
│   │   ├── services/             # API services
│   │   │   ├── api.js            # Axios config
│   │   │   ├── authService.js
│   │   │   ├── chatService.js
│   │   │   ├── userService.js
│   │   │   └── preferencesService.js
│   │   ├── store/                # State management (Context API or Redux)
│   │   │   ├── AuthContext.jsx
│   │   │   ├── ChatContext.jsx
│   │   │   └── PreferencesContext.jsx
│   │   ├── hooks/                # Custom hooks
│   │   │   ├── useAuth.js
│   │   │   ├── useChat.js
│   │   │   └── useTypingAnimation.js
│   │   ├── styles/               # Global styles
│   │   │   ├── theme.css         # Dark theme variables
│   │   │   ├── animations.css    # Typing dots, text reveal
│   │   │   └── global.css
│   │   └── utils/
│   │       ├── constants.js
│   │       └── helpers.js
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── backend/                      # Python FastAPI backend
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── auth.py       # Google OAuth + Email/Password
│   │   │   │   ├── users.py      # User profile CRUD
│   │   │   │   ├── conversations.py  # Conversation management
│   │   │   │   ├── messages.py   # Message CRUD
│   │   │   │   ├── preferences.py
│   │   │   │   ├── uploads.py
│   │   │   │   ├── voice.py
│   │   │   │   └── lawyer_verification.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── conversation.py
│   │   │   ├── message.py
│   │   │   └── preference.py
│   │   ├── services/
│   │   │   ├── auth_service.py   # JWT + OAuth logic
│   │   │   ├── bigquery_service.py
│   │   │   ├── gcs_service.py
│   │   │   ├── llm_service.py    # LLM brain with personalization
│   │   │   └── firestore_service.py (optional)
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── dependencies.py
│   │   └── main.py
│   ├── scripts/
│   │   ├── create_bigquery_tables.py
│   │   └── setup_gcs_buckets.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── database/                     # Database schemas
│   ├── bigquery/
│   │   ├── create_tables.sql
│   │   └── seed_data.sql
│   └── README.md
│
├── deployment/                   # GCP deployment configs
│   ├── backend/
│   │   ├── cloudbuild.yaml
│   │   └── service.yaml
│   ├── frontend/
│   │   ├── cloudbuild.yaml
│   │   └── nginx.conf
│   └── terraform/
│       └── main.tf (optional)
│
└── docs/
    ├── API.md
    ├── DEPLOYMENT.md
    └── TESTING.md
```

## TECH STACK

### Frontend
- **Framework**: React 18 + Vite
- **Routing**: React Router v6
- **State Management**: Context API + useReducer
- **HTTP Client**: Axios
- **Styling**: CSS Modules + CSS Variables (dark theme)
- **Auth**: Google OAuth + JWT storage

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Auth**: PyJWT + Google OAuth2
- **Database**: BigQuery (main), Firestore (optional session cache)
- **Storage**: Google Cloud Storage
- **LLM**: OpenAI GPT-4
- **Voice**: Google Cloud Speech + TTS

### Database Schema (BigQuery)

#### 1. `users` table
```sql
user_id STRING NOT NULL
email STRING NOT NULL
display_name STRING
username STRING
role STRING (Client/Lawyer/Admin)
avatar_url STRING
created_at TIMESTAMP
updated_at TIMESTAMP
```

#### 2. `user_preferences` table
```sql
user_id STRING NOT NULL
theme STRING (dark/light/system)
font_size STRING (small/medium/large)
response_style STRING (concise/detailed/legal_format)
language STRING (en/fr/es/hi/pa/zh)
auto_read BOOL
updated_at TIMESTAMP
```

#### 3. `conversations` table
```sql
conversation_id STRING NOT NULL
user_id STRING NOT NULL
title STRING
law_type STRING
jurisdiction STRING
created_at TIMESTAMP
updated_at TIMESTAMP
```

#### 4. `messages` table
```sql
message_id STRING NOT NULL
conversation_id STRING NOT NULL
user_id STRING NOT NULL
role STRING (user/assistant/system)
content STRING
created_at TIMESTAMP
citations JSON
metadata JSON
```

#### 5. `uploads` table
```sql
upload_id STRING NOT NULL
user_id STRING NOT NULL
type STRING (image/doc/audio/lawyer_license)
gcs_url STRING
filename STRING
created_at TIMESTAMP
```

#### 6. `lawyer_verification` table
```sql
user_id STRING NOT NULL
status STRING (draft/submitted/approved/rejected)
bar_country STRING
bar_province_state STRING
bar_number STRING
license_upload_id STRING
id_upload_id STRING
notes STRING
updated_at TIMESTAMP
```

## DEPLOYMENT ARCHITECTURE (GCP)

### Option 1: Two Cloud Run Services
- **Frontend Service**: Serves static React build via nginx
- **Backend Service**: FastAPI on Cloud Run
- **IAM**: Private services, specific invoker permissions
- **Challenge**: CORS and cross-service auth

### Option 2: Single Cloud Run Service (RECOMMENDED)
- Serve React static files + API from same FastAPI app
- No CORS issues
- Simpler auth (same domain)
- Easier IAM management

### GCS Buckets
- `legid-uploads-prod`: User uploads (images, docs, audio)
- `legid-lawyer-verification`: License documents
- `legid-backups`: Database backups

### IAP Configuration
- Org policy blocks `allUsers`
- Add specific invoker: `anshuman.kush@predictivetechlabs.com`
- Use Cloud IAP for additional security layer

## KEY FEATURES TO IMPLEMENT

### 1. Authentication
- [x] Google OAuth (primary)
- [x] Email/Password (secondary)
- [x] JWT session (httpOnly cookie)
- [x] Role-based access (Client/Lawyer/Admin)
- [x] Lawyer verification flow

### 2. Chat System
- [x] Conversation-based (not single chat)
- [x] Message persistence to BigQuery
- [x] Search across conversations
- [x] New chat creates new conversation
- [x] Typing dots animation (3 dot blink)
- [x] Text reveal animation for responses
- [x] Voice input/output

### 3. Profile & Preferences
- [x] Avatar upload
- [x] Display name + username
- [x] Theme selection (dark/light/system)
- [x] Font size (small/medium/large)
- [x] Response style (concise/detailed/legal_format)
- [x] Auto-read toggle

### 4. Resources Grid
- [x] Recent Updates
- [x] Case Lookup
- [x] Amendments
- [x] Documents
- [x] History
- [x] Change Law Type
- [x] Settings
- [x] AI Summary
- [x] Quick Summary

### 5. LLM "Brain" Behavior
- [x] Role-aware (Client vs Lawyer)
- [x] Personalization-aware formatting
- [x] Context linking (references prior messages)
- [x] Multi-path options
- [x] Citations (only real sources)
- [x] Deep answers (not shallow Google steps)

## NEXT STEPS
1. Create BigQuery tables
2. Build backend auth system
3. Build backend conversation APIs
4. Build React UI components
5. Implement typing animations
6. Deploy to Cloud Run
7. Configure IAM and IAP
