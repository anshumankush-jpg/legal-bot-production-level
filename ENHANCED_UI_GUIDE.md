# Enhanced Legal Assistant UI - Complete Guide

## Overview

This guide covers the new enhanced UI features for the Legal Assistant application, including the modern navigation bar, sidebar with chat history, role-based access control, and integrated legal API features.

## New Features

### 1. **Modern Navigation Bar**

The new navigation bar provides quick access to all major features:

- **New Chat**: Start a fresh conversation
- **Search Chats**: Search through your chat history
- **Images**: View uploaded images and documents
- **Apps**: Access legal apps and tools
- **Codex**: Browse legal statutes and codes
- **Projects**: Manage your legal cases and projects

**Location**: `frontend/src/components/NavigationBar.jsx`

### 2. **Sidebar with Saved Chats**

A collapsible sidebar that shows all your saved conversations:

**Features**:
- Real-time search through chat titles and content
- Chat icons based on legal category (⚖️ Criminal, 🚗 Traffic, 👨‍👩‍👧 Family, etc.)
- Timestamp display (e.g., "2h ago", "3d ago")
- Message count for each chat
- Delete functionality with confirmation
- Collapse/expand toggle

**Location**: `frontend/src/components/ChatSidebar.jsx`

### 3. **Enhanced Chat History Search**

Advanced search functionality with:

**Features**:
- Full-text search across all messages
- Tabbed interface (Sessions vs Search Results)
- Highlighted search terms in results
- Filter by law category
- Session management (view, load, delete)
- Timestamp and metadata display

**Location**: `frontend/src/components/ChatHistorySearch.jsx`

### 4. **Role-Based Access Control (RBAC)**

Four user roles with different access levels:

| Role | Features | APIs Available |
|------|----------|----------------|
| **Guest** | Basic chat | None |
| **Standard** | Chat, Search, Translation | Translation, Statute Search |
| **Premium** | + Case Lookup, Amendments | + Case Lookup, Amendment Generator |
| **Enterprise** | All features | All APIs, Custom integrations |

**Components**:
- `RoleAccessBanner.jsx` - Shows upgrade prompts
- Backend RBAC service at `backend/app/services/rbac_service.py`

### 5. **Legal API Integrations**

#### **Case Lookup API**

Search for legal cases across multiple jurisdictions:

```javascript
// Example usage
const response = await fetch('http://localhost:8000/api/legal/case-lookup', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'Miranda v. Arizona',
    jurisdiction: 'US',
    year_from: 1960,
    year_to: 2024,
    limit: 10
  })
});
```

**Features**:
- Search by case name, citation, or keywords
- Filter by jurisdiction and date range
- Relevance scoring
- Direct links to full case text

**Location**: `frontend/src/components/CaseLookup.jsx`

#### **Amendment Generator API**

Generate legal document amendments:

```javascript
// Example usage
const response = await fetch('http://localhost:8000/api/legal/generate-amendment', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    document_type: 'contract',
    case_details: {
      amendment_text: 'Change payment terms from 30 to 45 days',
      party_a: 'Company A',
      party_b: 'Company B',
      effective_date: '2024-02-01'
    },
    jurisdiction: 'US-NY'
  })
});
```

**Features**:
- Multiple document types (contracts, wills, agreements, etc.)
- Jurisdiction-specific formatting
- Download and copy functionality
- Preview before finalizing

**Location**: `frontend/src/components/AmendmentGenerator.jsx`

### 6. **Translation API**

Multilingual support for legal documents:

```javascript
const response = await fetch('http://localhost:8000/api/translate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'Legal document text',
    target_language: 'es',
    source_language: 'en'
  })
});
```

**Supported Languages**:
- English (en)
- Spanish (es)
- French (fr)
- Hindi (hi)
- Punjabi (pa)
- Chinese (zh)

## Installation & Setup

### 1. Install Dependencies

```bash
cd legal-bot/frontend
npm install
```

### 2. Configure API Keys (Optional)

For real API integrations, add to your `.env` file:

```env
# Legal API Keys (Optional - mock data used if not provided)
CASETEXT_API_KEY=your_casetext_key
LEGALZOOM_API_KEY=your_legalzoom_key
LEXISNEXIS_API_KEY=your_lexisnexis_key
WESTLAW_API_KEY=your_westlaw_key

# OpenAI for LLM (Required)
OPENAI_API_KEY=your_openai_key
```

### 3. Start the Application

```bash
# Terminal 1: Start Backend
cd legal-bot/backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Start Frontend
cd legal-bot/frontend
npm run dev
```

## Usage Examples

### Example 1: Starting a New Chat with Case Lookup

1. Click **New Chat** in the navigation bar
2. Select your law type (e.g., Criminal Law)
3. Click **🔍 Case Lookup** in the header
4. Search for relevant cases
5. Click on a case to insert it into your chat

### Example 2: Searching Chat History

1. Click **Search Chats** in the navigation bar
2. Enter keywords in the search box
3. View results with highlighted matches
4. Click on a result to load that conversation

### Example 3: Generating an Amendment

1. In an active chat, click **📝 Amendments**
2. Select document type (e.g., Contract)
3. Fill in amendment details
4. Click **Generate Amendment**
5. Download or copy the generated document

### Example 4: Role-Based Access

If you try to access a premium feature:

1. A banner will appear showing:
   - Required role for the feature
   - Your current role
   - Upgrade benefits
   - Pricing information
2. Click **Upgrade Now** to proceed with upgrade

## Component Architecture

```
EnhancedApp (Main Container)
├── NavigationBar (Top navigation)
├── ChatSidebar (Left sidebar with chat list)
│   ├── Search functionality
│   └── Chat items with metadata
├── ChatInterface (Main chat area)
│   ├── ChatHistorySearch (Search modal)
│   ├── CaseLookup (Case search modal)
│   ├── AmendmentGenerator (Amendment modal)
│   └── VoiceChat (Voice interface)
└── RoleAccessBanner (Access control overlay)
```

## API Endpoints

### Chat & History

- `POST /api/artillery/chat` - Send chat message
- `POST /api/chat-history/save` - Save message to history
- `GET /api/chat-history/sessions/{user_id}` - Get user sessions
- `POST /api/chat-history/search` - Search chat history
- `DELETE /api/chat-history/session/{user_id}/{session_id}` - Delete session

### Legal APIs

- `POST /api/legal/case-lookup` - Search legal cases
- `POST /api/legal/generate-amendment` - Generate amendments
- `POST /api/legal/search-statutes` - Search statutes
- `POST /api/translate` - Translate text
- `GET /api/translate/languages` - Get supported languages

### Authentication & RBAC

- `POST /api/auth/token` - Generate auth token
- `GET /api/auth/verify` - Verify token
- `GET /api/auth/check-access` - Check API access

## Styling & Theming

All components use a consistent dark theme with:

- **Primary Color**: `#667eea` (Purple-blue gradient)
- **Background**: `#1a1a2e` to `#16213e` gradient
- **Text**: White with various opacity levels
- **Accent**: `#764ba2` (Purple)

### CSS Files

- `NavigationBar.css` - Top navigation styling
- `ChatSidebar.css` - Sidebar and chat list styling
- `ChatHistorySearch.css` - Search modal styling
- `RoleAccessBanner.css` - Access control banner styling
- `EnhancedApp.css` - Main app container styling

## Customization

### Adding a New Navigation Item

1. Edit `NavigationBar.jsx`:

```javascript
<button 
  className={`nav-btn ${activeView === 'mynew' ? 'active' : ''}`}
  onClick={() => handleViewChange('mynew', onShowMyNew)}
>
  <svg>...</svg>
  <span>My New Feature</span>
</button>
```

2. Add handler in `EnhancedApp.jsx`:

```javascript
const handleShowMyNew = () => {
  setCurrentView('mynew');
};
```

### Adding a New Role

1. Edit `backend/app/services/rbac_service.py`:

```python
class UserRole(Enum):
    GUEST = "guest"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    MYNEWROLE = "mynewrole"  # Add here
```

2. Define permissions:

```python
UserRole.MYNEWROLE: {
    Permission.CHAT,
    Permission.SEARCH,
    # Add permissions
}
```

## Troubleshooting

### Issue: Sidebar not showing chats

**Solution**: Check localStorage:
```javascript
console.log(localStorage.getItem('legubot_chats'));
```

### Issue: API access denied

**Solution**: Check your role and API configuration:
```bash
curl http://localhost:8000/api/auth/check-access?api_name=case_lookup
```

### Issue: Styling not applied

**Solution**: Ensure CSS files are imported:
```javascript
import './NavigationBar.css';
import './ChatSidebar.css';
```

## Performance Optimization

### Lazy Loading

Components are loaded only when needed:

```javascript
const CaseLookup = React.lazy(() => import('./CaseLookup'));
```

### Memoization

Use React.memo for expensive components:

```javascript
export default React.memo(ChatSidebar);
```

### Virtual Scrolling

For large chat lists, consider implementing virtual scrolling:

```bash
npm install react-window
```

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Authentication**: Always verify tokens on the backend
3. **Input Validation**: Sanitize all user inputs
4. **CORS**: Configure CORS properly in production
5. **Rate Limiting**: Implement rate limiting for API calls

## Future Enhancements

- [ ] Real-time collaboration features
- [ ] Advanced analytics dashboard
- [ ] Custom law category creation
- [ ] Document version control
- [ ] Team workspace features
- [ ] Mobile app version
- [ ] Offline mode support
- [ ] Advanced search filters

## Support & Documentation

- **Backend API Docs**: http://localhost:8000/docs
- **GitHub Issues**: Report bugs and feature requests
- **Community Forum**: Join discussions with other users

## License

This project is part of the LEGID Legal Assistant platform.

---

**Last Updated**: January 2026
**Version**: 2.0.0
