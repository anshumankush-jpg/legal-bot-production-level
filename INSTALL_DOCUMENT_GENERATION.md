# Legal Document Generation - Installation Guide

## Quick Installation (5 minutes)

Follow these steps to install and configure the legal document generation feature.

---

## Prerequisites

✅ Node.js 14+ and npm installed  
✅ Python 3.8+ installed  
✅ Backend server configured  
✅ Frontend application configured  

---

## Step 1: Install Frontend Dependencies

### Install jsPDF for PDF Generation

```bash
cd legal-bot/frontend
npm install jspdf
```

**Expected Output:**
```
+ jspdf@2.5.1
added 1 package
```

---

## Step 2: Verify Files Are in Place

### Frontend Files

Check these files exist:
```bash
frontend/src/components/
├── DocumentGenerator.jsx     ✓
├── DocumentGenerator.css     ✓
└── ChatInterface.jsx         ✓ (modified)
```

### Backend Files

Check these files exist:
```bash
backend/app/services/
├── document_generation_service.py  ✓
└── rbac_service.py                 ✓ (modified)

backend/app/
└── main.py                         ✓ (modified)
```

---

## Step 3: Configure Backend (Optional)

### For Mock Mode (Default - No Setup Required)

The system works out of the box with mock data. No configuration needed!

### For Production Mode (Real APIs)

Edit `backend/.env`:

```bash
# Legal API Keys (Optional - for production use)
LEGALZOOM_API_KEY=your_key_here
LEXISNEXIS_API_KEY=your_key_here
CASETEXT_API_KEY=your_key_here
WESTLAW_API_KEY=your_key_here
```

**Note:** Without API keys, the system uses mock data for testing.

---

## Step 4: Restart Servers

### Restart Backend

```bash
cd legal-bot/backend

# Stop if running (Ctrl+C)

# Start backend
python -m uvicorn app.main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Restart Frontend

```bash
cd legal-bot/frontend

# Stop if running (Ctrl+C)

# Start frontend
npm start
```

**Expected Output:**
```
Compiled successfully!
Local:            http://localhost:3000
```

---

## Step 5: Verify Installation

### Test 1: Check Backend Endpoint

```bash
curl http://localhost:8000/api/legal/generate-document \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "document_type": "nda",
    "form_data": {
      "disclosing_party": "Test Company",
      "receiving_party": "Test Contractor",
      "purpose": "Testing",
      "confidential_info": "Test data",
      "term_years": "2",
      "effective_date": "2026-01-09"
    },
    "jurisdiction": "US"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "document_id": "doc_nda_...",
  "content": "NON-DISCLOSURE AGREEMENT...",
  "source": "AI-Powered Document Generator"
}
```

### Test 2: Check Frontend

1. Open http://localhost:3000
2. Complete onboarding
3. Look for "📄 Documents" button in toolbar
4. Click it - modal should open

---

## Step 6: Test Document Generation

### Quick Test (1 minute)

1. Click "📄 Documents" button
2. Select "🤐 Non-Disclosure Agreement"
3. Fill in the form:
   - Disclosing Party: Test Company
   - Receiving Party: Test Person
   - Purpose: Testing the system
   - Confidential Info: Test information
   - Term: 2 years
   - Effective Date: Today's date
4. Click "Generate Document"
5. Verify document appears
6. Try "Download PDF" button

**Success Indicators:**
- ✅ Modal opens smoothly
- ✅ Form displays correctly
- ✅ Document generates without errors
- ✅ PDF downloads successfully

---

## Troubleshooting

### Issue: "jsPDF is not defined"

**Solution:**
```bash
cd legal-bot/frontend
npm install jspdf
npm start
```

### Issue: "Module not found: document_generation_service"

**Solution:**
```bash
# Verify file exists
ls backend/app/services/document_generation_service.py

# Restart backend
cd backend
python -m uvicorn app.main:app --reload
```

### Issue: "Access Denied" Error

**Solution:**
Check user role has STANDARD permission or higher.

```python
# In backend, check RBAC configuration
# UserRole.STANDARD should have Permission.API_DOCUMENT_GENERATION
```

### Issue: Backend Not Starting

**Solution:**
```bash
# Check for errors
cd backend
python -m uvicorn app.main:app --reload

# Check logs
tail -f backend_detailed.log
```

### Issue: Frontend Not Showing Button

**Solution:**
1. Clear browser cache (Ctrl+Shift+R)
2. Check browser console for errors (F12)
3. Verify ChatInterface.jsx includes DocumentGenerator import

---

## Configuration Options

### Customize Document Templates

Edit `backend/app/services/document_generation_service.py`:

```python
async def _generate_nda(self, form_data, jurisdiction):
    # Customize template here
    content = f"""
    YOUR CUSTOM TEMPLATE
    """
    return content
```

### Add New Document Type

1. **Add to Frontend** (`DocumentGenerator.jsx`):
```javascript
const documentTypes = {
  'your_new_type': {
    name: 'Your Document Name',
    icon: '📋',
    description: 'Description here',
    fields: [
      { name: 'field1', label: 'Field 1', type: 'text', required: true }
    ]
  }
}
```

2. **Add to Backend** (`document_generation_service.py`):
```python
self.templates = {
    'your_new_type': self._generate_your_new_type,
}

async def _generate_your_new_type(self, form_data, jurisdiction):
    # Your template here
    return content
```

### Customize Styling

Edit `frontend/src/components/DocumentGenerator.css`:

```css
/* Change colors */
.modal-header {
  background: linear-gradient(135deg, #your-color1, #your-color2);
}

/* Change button styles */
.btn-primary {
  background: #your-color;
}
```

---

## Verification Checklist

After installation, verify:

- [ ] Backend server running on port 8000
- [ ] Frontend application running on port 3000
- [ ] "📄 Documents" button visible in toolbar
- [ ] Modal opens when button clicked
- [ ] All 8 document types visible
- [ ] Form displays for selected type
- [ ] Document generates successfully
- [ ] PDF download works
- [ ] TXT download works
- [ ] Copy to clipboard works
- [ ] Edit functionality works
- [ ] No console errors

---

## Performance Optimization

### Enable Caching (Optional)

```python
# In backend/app/services/document_generation_service.py
from functools import lru_cache

@lru_cache(maxsize=100)
async def generate_document_cached(self, document_type, form_data_hash):
    # Cached document generation
    pass
```

### Enable Compression (Optional)

```python
# In backend/app/main.py
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

---

## Security Hardening

### Production Deployment

1. **Set Strong JWT Secret**
```bash
# In backend/.env
JWT_SECRET_KEY=your-very-long-random-secret-key-here
```

2. **Enable HTTPS**
```python
# In backend/app/main.py
# Configure SSL certificates
```

3. **Rate Limiting**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/legal/generate-document")
@limiter.limit("10/minute")
async def generate_document(...):
    pass
```

4. **Input Validation**
```python
from pydantic import validator

class DocumentGenerationRequest(BaseModel):
    document_type: str
    
    @validator('document_type')
    def validate_type(cls, v):
        allowed = ['sue_letter', 'amendment', 'nda', ...]
        if v not in allowed:
            raise ValueError('Invalid document type')
        return v
```

---

## Monitoring Setup

### Enable Logging

```python
# In backend/app/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('document_generation.log'),
        logging.StreamHandler()
    ]
)
```

### Track Metrics

```python
# Track document generation
from prometheus_client import Counter

doc_generated = Counter(
    'documents_generated_total',
    'Total documents generated',
    ['document_type']
)

@app.post("/api/legal/generate-document")
async def generate_document(request):
    doc_generated.labels(document_type=request.document_type).inc()
    # ... rest of code
```

---

## Backup & Recovery

### Backup Generated Documents

```python
# In backend/app/services/document_generation_service.py
import json
from datetime import datetime

async def save_document_backup(self, document_id, content):
    backup_dir = Path("./backups/documents")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    backup_file = backup_dir / f"{document_id}.json"
    with open(backup_file, 'w') as f:
        json.dump({
            'document_id': document_id,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }, f)
```

---

## Uninstallation (If Needed)

### Remove Frontend Components

```bash
cd legal-bot/frontend

# Remove files
rm src/components/DocumentGenerator.jsx
rm src/components/DocumentGenerator.css

# Uninstall dependency
npm uninstall jspdf

# Revert ChatInterface.jsx changes
git checkout src/components/ChatInterface.jsx
```

### Remove Backend Services

```bash
cd legal-bot/backend

# Remove files
rm app/services/document_generation_service.py

# Revert changes
git checkout app/main.py
git checkout app/services/rbac_service.py
```

---

## Support

### Getting Help

1. **Documentation**
   - Read: `LEGAL_DOCUMENT_GENERATION_GUIDE.md`
   - Read: `DOCUMENT_GENERATION_QUICK_START.md`
   - Read: `API_INTEGRATION_SETUP.md`

2. **Logs**
   - Backend: `backend/backend_detailed.log`
   - Frontend: Browser console (F12)

3. **Contact**
   - Email: support@plaza-ai.com
   - GitHub: Create an issue

---

## Next Steps

After successful installation:

1. ✅ Read the Quick Start Guide
2. ✅ Test all document types
3. ✅ Configure API keys (optional)
4. ✅ Customize templates (optional)
5. ✅ Train users
6. ✅ Deploy to production

---

## Version Information

**Version:** 1.0.0  
**Release Date:** January 9, 2026  
**Status:** Production Ready  
**Compatibility:**
- Node.js: 14+
- Python: 3.8+
- React: 17+
- FastAPI: 0.68+

---

## License

Copyright © 2026 PLAZA-AI. All rights reserved.

---

**Installation Complete! 🎉**

You're now ready to generate legal documents!

See `DOCUMENT_GENERATION_QUICK_START.md` for usage instructions.
