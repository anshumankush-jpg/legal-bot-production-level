# LEGID REBUILD - IMPLEMENTATION GUIDE

## QUICK START (Development)

### 1. Set Up Database

```bash
# Install Google Cloud SDK
gcloud init

# Set project
export GCP_PROJECT_ID="your-project-id"

# Create BigQuery tables
cd database/bigquery
python create_tables.py --project=$GCP_PROJECT_ID --dataset=legid_dev

# Create GCS buckets
python setup_gcs_buckets.py --project=$GCP_PROJECT_ID --prefix=legid-dev
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
# App
DEBUG=True
HOST=0.0.0.0
PORT=8000

# JWT
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/google/callback

# BigQuery
GCP_PROJECT_ID=$GCP_PROJECT_ID
BIGQUERY_DATASET=legid_dev
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# GCS
GCS_UPLOADS_BUCKET=legid-dev-uploads-prod
GCS_LAWYER_VERIFICATION_BUCKET=legid-dev-lawyer-verification
GCS_BACKUPS_BUCKET=legid-dev-backups

# OpenAI
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4

# Optional: Firestore for session caching
USE_FIRESTORE=false
FIRESTORE_COLLECTION=legid_sessions
EOF

# Run backend
uvicorn app.main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-google-client-id
EOF

# Run frontend
npm run dev
```

## TYPING ANIMATION IMPLEMENTATION

### CSS for Typing Dots (ChatGPT-style)

```css
/* frontend/src/styles/animations.css */

@keyframes typingDots {
  0%, 20% {
    opacity: 0.2;
    transform: translateY(0);
  }
  40% {
    opacity: 1;
    transform: translateY(-5px);
  }
  60%, 100% {
    opacity: 0.2;
    transform: translateY(0);
  }
}

.typing-indicator {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
  background: #2a2a2a;
  border-radius: 18px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #666;
  border-radius: 50%;
  animation: typingDots 1.4s infinite;
}

.typing-indicator span:nth-child(1) {
  animation-delay: 0s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}
```

### Text Reveal Animation

```css
/* frontend/src/styles/animations.css */

@keyframes textReveal {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.message-content.reveal {
  animation: textReveal 0.3s ease-in;
}

/* Character-by-character reveal (optional, more ChatGPT-like) */
@keyframes charReveal {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.message-content .char {
  animation: charReveal 0.05s ease-in forwards;
  opacity: 0;
}
```

### React Hook for Text Animation

```javascript
// frontend/src/hooks/useTypingAnimation.js

import { useState, useEffect } from 'react';

export const useTypingAnimation = (text, speed = 30) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (!text) return;

    let currentIndex = 0;
    setDisplayedText('');
    setIsComplete(false);

    const interval = setInterval(() => {
      if (currentIndex < text.length) {
        setDisplayedText(text.slice(0, currentIndex + 1));
        currentIndex++;
      } else {
        setIsComplete(true);
        clearInterval(interval);
      }
    }, speed);

    return () => clearInterval(interval);
  }, [text, speed]);

  return { displayedText, isComplete };
};

// Usage:
// const { displayedText, isComplete } = useTypingAnimation(message.content, 30);
```

## DARK THEME IMPLEMENTATION

### CSS Variables (Theme)

```css
/* frontend/src/styles/theme.css */

:root {
  /* Dark Theme (Default) */
  --bg-primary: #1a1a1a;
  --bg-secondary: #2a2a2a;
  --bg-tertiary: #3a3a3a;
  --bg-hover: #404040;
  --bg-active: #4a4a4a;
  
  --text-primary: #e0e0e0;
  --text-secondary: #a0a0a0;
  --text-tertiary: #707070;
  
  --border-color: #3a3a3a;
  --border-hover: #4a4a4a;
  
  --accent-blue: #4a9eff;
  --accent-green: #10a37f;
  --accent-red: #ff6b6b;
  --accent-yellow: #ffd93d;
  
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);
  
  --radius-sm: 6px;
  --radius-md: 12px;
  --radius-lg: 18px;
  
  --transition: all 0.2s ease;
}

[data-theme="light"] {
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --bg-tertiary: #e0e0e0;
  --bg-hover: #d0d0d0;
  --bg-active: #c0c0c0;
  
  --text-primary: #1a1a1a;
  --text-secondary: #4a4a4a;
  --text-tertiary: #707070;
  
  --border-color: #e0e0e0;
  --border-hover: #d0d0d0;
  
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
}

body {
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
```

### ChatGPT-style Layout

```css
/* frontend/src/components/layout/MainLayout.css */

.main-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--bg-primary);
}

.sidebar {
  width: 260px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: var(--transition);
}

.sidebar.collapsed {
  width: 0;
  overflow: hidden;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.new-chat-btn {
  width: 100%;
  padding: 12px 16px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 8px;
}

.new-chat-btn:hover {
  background: var(--bg-hover);
}

.search-chats-input {
  width: 100%;
  margin-top: 12px;
  padding: 10px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 13px;
}

.search-chats-input::placeholder {
  color: var(--text-tertiary);
}

.resources-section {
  padding: 16px;
  flex: 1;
  overflow-y: auto;
}

.resources-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

.resources-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.resource-tile {
  padding: 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition);
  text-align: center;
}

.resource-tile:hover {
  background: var(--bg-hover);
  border-color: var(--border-hover);
  transform: translateY(-1px);
}

.resource-tile-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.resource-tile-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.top-bar {
  height: 60px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.message-bubble {
  max-width: 700px;
  margin: 0 auto 16px auto;
  width: 100%;
}

.message-bubble.user {
  background: var(--bg-tertiary);
  padding: 12px 16px;
  border-radius: var(--radius-lg);
  margin-left: auto;
  max-width: 70%;
}

.message-bubble.assistant {
  background: transparent;
  padding: 12px 0;
}

.composer {
  padding: 16px 24px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
}

.composer-input-container {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  gap: 8px;
  align-items: center;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 4px;
}

.composer-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 15px;
  padding: 12px;
  resize: none;
  max-height: 200px;
}

.composer-btn {
  width: 36px;
  height: 36px;
  background: var(--bg-hover);
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
}

.composer-btn:hover {
  background: var(--bg-active);
}

.composer-btn.send {
  background: var(--accent-blue);
  color: white;
}

.composer-btn.send:disabled {
  background: var(--bg-hover);
  color: var(--text-tertiary);
  cursor: not-allowed;
}
```

## BACKEND AUTH STRUCTURE

### JWT Service

```python
# backend/app/services/auth_service.py

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

class AuthService:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_access_token(self, user_id: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)
        
        payload = {
            "user_id": user_id,
            "role": role,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    async def verify_google_token(self, id_token: str) -> Dict[str, Any]:
        """Verify Google OAuth ID token."""
        from google.oauth2 import id_token as google_id_token
        from google.auth.transport import requests
        
        try:
            # Verify token
            idinfo = google_id_token.verify_oauth2_token(
                id_token, 
                requests.Request(),
                os.getenv('GOOGLE_CLIENT_ID')
            )
            
            # Validate issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return {
                "google_id": idinfo['sub'],
                "email": idinfo['email'],
                "email_verified": idinfo.get('email_verified', False),
                "name": idinfo.get('name'),
                "picture": idinfo.get('picture')
            }
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google token: {str(e)}"
            )
```

### Auth Routes

```python
# backend/app/api/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Response
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from datetime import datetime

from app.services.auth_service import AuthService
from app.services.bigquery_service import BigQueryService
from app.core.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

auth_service = AuthService(
    secret_key=settings.JWT_SECRET_KEY,
    algorithm=settings.JWT_ALGORITHM
)
bq_service = BigQueryService()

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str
    role: str = "Client"  # Client or Lawyer

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class GoogleAuthRequest(BaseModel):
    id_token: str
    role: str = "Client"

@router.post("/register")
async def register(request: RegisterRequest):
    """Register new user with email/password."""
    
    # Check if email exists
    existing_user = await bq_service.query_one(
        f"SELECT user_id FROM `{settings.BIGQUERY_DATASET}.users` WHERE email = @email",
        {"email": request.email}
    )
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user_id = f"user_{uuid.uuid4().hex}"
    password_hash = auth_service.hash_password(request.password)
    
    await bq_service.insert(
        f"{settings.BIGQUERY_DATASET}.users",
        {
            "user_id": user_id,
            "email": request.email,
            "password_hash": password_hash,
            "display_name": request.display_name,
            "role": request.role,
            "auth_provider": "email",
            "email_verified": False,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    )
    
    # Create default preferences
    await bq_service.insert(
        f"{settings.BIGQUERY_DATASET}.user_preferences",
        {
            "user_id": user_id,
            "theme": "dark",
            "font_size": "medium",
            "response_style": "detailed",
            "language": "en",
            "auto_read": False,
            "updated_at": datetime.utcnow().isoformat()
        }
    )
    
    # Generate token
    token = auth_service.create_access_token(user_id, request.role)
    
    return {
        "success": True,
        "user_id": user_id,
        "token": token,
        "role": request.role
    }

@router.post("/login")
async def login(request: LoginRequest, response: Response):
    """Login with email/password."""
    
    # Get user
    user = await bq_service.query_one(
        f"SELECT * FROM `{settings.BIGQUERY_DATASET}.users` WHERE email = @email",
        {"email": request.email}
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not auth_service.verify_password(request.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Update last login
    await bq_service.update(
        f"{settings.BIGQUERY_DATASET}.users",
        {"last_login": datetime.utcnow().isoformat()},
        f"user_id = '{user['user_id']}'"
    )
    
    # Generate token
    token = auth_service.create_access_token(user['user_id'], user['role'])
    
    # Set httpOnly cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=86400  # 24 hours
    )
    
    return {
        "success": True,
        "user_id": user['user_id'],
        "token": token,
        "role": user['role'],
        "display_name": user['display_name']
    }

@router.post("/google")
async def google_auth(request: GoogleAuthRequest, response: Response):
    """Authenticate with Google OAuth."""
    
    # Verify Google token
    google_user = await auth_service.verify_google_token(request.id_token)
    
    # Check if user exists
    user = await bq_service.query_one(
        f"SELECT * FROM `{settings.BIGQUERY_DATASET}.users` WHERE google_id = @google_id OR email = @email",
        {"google_id": google_user['google_id'], "email": google_user['email']}
    )
    
    if not user:
        # Create new user
        user_id = f"user_{uuid.uuid4().hex}"
        
        await bq_service.insert(
            f"{settings.BIGQUERY_DATASET}.users",
            {
                "user_id": user_id,
                "email": google_user['email'],
                "google_id": google_user['google_id'],
                "display_name": google_user['name'],
                "avatar_url": google_user['picture'],
                "role": request.role,
                "auth_provider": "google",
                "email_verified": google_user['email_verified'],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        )
        
        # Create default preferences
        await bq_service.insert(
            f"{settings.BIGQUERY_DATASET}.user_preferences",
            {
                "user_id": user_id,
                "theme": "dark",
                "font_size": "medium",
                "response_style": "detailed",
                "language": "en",
                "auto_read": False,
                "updated_at": datetime.utcnow().isoformat()
            }
        )
        
        user = {"user_id": user_id, "role": request.role, "display_name": google_user['name']}
    else:
        # Update last login
        await bq_service.update(
            f"{settings.BIGQUERY_DATASET}.users",
            {"last_login": datetime.utcnow().isoformat()},
            f"user_id = '{user['user_id']}'"
        )
    
    # Generate token
    token = auth_service.create_access_token(user['user_id'], user['role'])
    
    # Set httpOnly cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=86400
    )
    
    return {
        "success": True,
        "user_id": user['user_id'],
        "token": token,
        "role": user['role'],
        "display_name": user['display_name']
    }

@router.post("/logout")
async def logout(response: Response):
    """Logout user."""
    response.delete_cookie("access_token")
    return {"success": True, "message": "Logged out successfully"}

@router.get("/me")
async def get_current_user(token: str = Depends(auth_service.verify_token)):
    """Get current user info from token."""
    
    user = await bq_service.query_one(
        f"SELECT * FROM `{settings.BIGQUERY_DATASET}.users` WHERE user_id = @user_id",
        {"user_id": token['user_id']}
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Remove sensitive data
    user.pop('password_hash', None)
    user.pop('google_id', None)
    
    return {"success": True, "user": user}
```

---

**Due to the massive scope, I'm creating this in phases. This guide provides:**

1. ✅ Database setup (BigQuery + GCS)
2. ✅ Typing animation (dots + text reveal)
3. ✅ Dark theme CSS
4. ✅ Backend auth system (JWT + Google OAuth)

**Continuing in next message with:**
- Conversation management APIs
- React frontend components
- Profile dropdown & edit modal
- Deployment configs

Let me know if you want me to continue with the full implementation!
