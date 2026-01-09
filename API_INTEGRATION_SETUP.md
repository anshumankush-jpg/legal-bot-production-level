# Legal API Integration Setup Guide

## Overview

This guide explains how to integrate external legal APIs (LegalZoom, LexisNexis, CaseText, Westlaw) with the legal document generation system.

---

## Supported APIs

### 1. **LegalZoom API** - Amendment Generation
- **Purpose**: Generate and modify legal documents
- **Features**: Document templates, amendments, customization
- **Website**: https://www.legalzoom.com/developers
- **Pricing**: Contact LegalZoom for API pricing

### 2. **LexisNexis API** - Case Lookup
- **Purpose**: Search legal cases and precedents
- **Features**: Case law database, citations, summaries
- **Website**: https://www.lexisnexis.com/api
- **Pricing**: Enterprise pricing, contact sales

### 3. **CaseText API** - Advanced Case Search
- **Purpose**: AI-powered legal research
- **Features**: CARA AI, case analysis, precedent search
- **Website**: https://casetext.com/api
- **Pricing**: Subscription-based

### 4. **Westlaw API** - Legal Research
- **Purpose**: Comprehensive legal research
- **Features**: Case law, statutes, regulations
- **Website**: https://developer.thomsonreuters.com
- **Pricing**: Enterprise pricing

---

## Setup Instructions

### Step 1: Obtain API Keys

#### LegalZoom
1. Visit https://www.legalzoom.com/developers
2. Create developer account
3. Apply for API access
4. Generate API key
5. Note: May require business verification

#### LexisNexis
1. Visit https://www.lexisnexis.com/api
2. Contact sales team
3. Sign enterprise agreement
4. Receive API credentials
5. Complete onboarding

#### CaseText
1. Visit https://casetext.com
2. Sign up for account
3. Contact support for API access
4. Subscribe to API plan
5. Generate API key

#### Westlaw
1. Visit https://developer.thomsonreuters.com
2. Create developer account
3. Apply for Westlaw API access
4. Complete verification
5. Receive credentials

### Step 2: Configure Environment Variables

Create or edit `backend/.env` file:

```bash
# ============================================
# LEGAL API KEYS
# ============================================

# LegalZoom API (Document Generation)
LEGALZOOM_API_KEY=your_legalzoom_api_key_here
LEGALZOOM_API_SECRET=your_legalzoom_secret_here

# LexisNexis API (Case Lookup)
LEXISNEXIS_API_KEY=your_lexisnexis_api_key_here
LEXISNEXIS_CLIENT_ID=your_lexisnexis_client_id_here
LEXISNEXIS_CLIENT_SECRET=your_lexisnexis_secret_here

# CaseText API (Case Search)
CASETEXT_API_KEY=your_casetext_api_key_here

# Westlaw API (Legal Research)
WESTLAW_API_KEY=your_westlaw_api_key_here
WESTLAW_CLIENT_ID=your_westlaw_client_id_here
WESTLAW_CLIENT_SECRET=your_westlaw_secret_here

# ============================================
# API CONFIGURATION
# ============================================

# Enable/Disable APIs
ENABLE_LEGALZOOM=true
ENABLE_LEXISNEXIS=true
ENABLE_CASETEXT=true
ENABLE_WESTLAW=false

# API Timeouts (seconds)
API_TIMEOUT=30

# Rate Limiting
API_RATE_LIMIT_PER_MINUTE=60
```

### Step 3: Restart Backend Server

```bash
cd legal-bot/backend

# Stop the server (Ctrl+C if running)

# Start with new configuration
python -m uvicorn app.main:app --reload --port 8000
```

### Step 4: Verify Integration

Test each API:

```bash
# Test LegalZoom
curl -X POST http://localhost:8000/api/legal/generate-amendment \
  -H "Content-Type: application/json" \
  -d '{
    "document_type": "contract",
    "case_details": {
      "amendment_text": "Test amendment"
    }
  }'

# Test LexisNexis
curl -X POST http://localhost:8000/api/legal/case-lookup \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Miranda v. Arizona",
    "jurisdiction": "US"
  }'

# Test CaseText
curl -X POST http://localhost:8000/api/legal/case-lookup \
  -H "Content-Type: application/json" \
  -d '{
    "query": "contract breach",
    "limit": 10
  }'
```

---

## API Usage Examples

### LegalZoom - Generate Amendment

```python
# Backend usage
from app.services.legal_api_integrations import get_legal_api_service

legal_api = get_legal_api_service()

result = await legal_api.generate_amendment_legalzoom(
    document_type="contract",
    case_details={
        "amendment_text": "Change payment terms from quarterly to monthly",
        "party_a": "Company A",
        "party_b": "Company B",
        "effective_date": "2026-02-01"
    },
    jurisdiction="US-CA"
)

print(result["content"])
```

### LexisNexis - Case Lookup

```python
result = await legal_api.case_lookup_lexisnexis(
    query="breach of contract",
    jurisdiction="US-NY",
    limit=10
)

for case in result["results"]:
    print(f"{case['case_name']} - {case['citation']}")
```

### CaseText - Advanced Search

```python
result = await legal_api.case_lookup_casetext(
    query="employment discrimination",
    jurisdiction="US",
    year_from=2020,
    year_to=2025,
    limit=20
)
```

---

## Mock Mode vs. Production Mode

### Mock Mode (Default)

When API keys are not configured, the system uses mock data:

**Features:**
- ✅ Instant responses
- ✅ No API costs
- ✅ Good for testing
- ✅ Sample legal documents
- ⚠️ Not real legal data

**Use Cases:**
- Development and testing
- Demonstrations
- Training
- Proof of concept

### Production Mode (With API Keys)

When API keys are configured:

**Features:**
- ✅ Real legal data
- ✅ Up-to-date case law
- ✅ Professional documents
- ✅ Jurisdiction-specific
- ⚠️ API costs apply

**Use Cases:**
- Production deployment
- Client-facing applications
- Legal research
- Professional document generation

---

## API Rate Limits

### Recommended Limits

| API | Requests/Minute | Requests/Day | Cost Model |
|-----|----------------|--------------|------------|
| LegalZoom | 60 | 5,000 | Per request |
| LexisNexis | 120 | 10,000 | Subscription |
| CaseText | 100 | 8,000 | Subscription |
| Westlaw | 200 | 20,000 | Enterprise |

### Implementing Rate Limiting

```python
# In backend/app/services/legal_api_integrations.py

from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=60, period=60)  # 60 calls per minute
async def case_lookup_casetext(self, query: str, **kwargs):
    # API call implementation
    pass
```

---

## Error Handling

### Common Errors

#### 1. Authentication Error (401)
```json
{
  "error": "Invalid API key",
  "code": 401
}
```
**Solution:** Check API key is correct and active

#### 2. Rate Limit Exceeded (429)
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```
**Solution:** Implement rate limiting, wait before retry

#### 3. Invalid Request (400)
```json
{
  "error": "Invalid jurisdiction code",
  "code": 400
}
```
**Solution:** Validate input parameters

#### 4. Service Unavailable (503)
```json
{
  "error": "Service temporarily unavailable",
  "code": 503
}
```
**Solution:** Implement retry logic with exponential backoff

### Error Handling Implementation

```python
async def case_lookup_with_retry(self, query: str, max_retries: int = 3):
    """Case lookup with automatic retry on failure."""
    for attempt in range(max_retries):
        try:
            return await self.case_lookup_casetext(query)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                # Rate limit - wait and retry
                wait_time = 2 ** attempt  # Exponential backoff
                await asyncio.sleep(wait_time)
                continue
            elif e.response.status_code >= 500:
                # Server error - retry
                await asyncio.sleep(1)
                continue
            else:
                # Client error - don't retry
                raise
        except Exception as e:
            logger.error(f"API error: {e}")
            if attempt == max_retries - 1:
                # Last attempt - use mock data
                return self._mock_case_lookup(query)
```

---

## Cost Optimization

### Tips to Reduce API Costs

1. **Caching**
```python
from functools import lru_cache
from datetime import datetime, timedelta

# Cache results for 1 hour
@lru_cache(maxsize=1000)
async def cached_case_lookup(query: str, jurisdiction: str):
    return await legal_api.case_lookup_casetext(query, jurisdiction)
```

2. **Request Batching**
```python
# Batch multiple queries into one request
async def batch_case_lookup(queries: List[str]):
    return await legal_api.batch_search(queries)
```

3. **Smart Fallbacks**
```python
# Try cheaper API first, fallback to expensive one
async def smart_case_lookup(query: str):
    try:
        # Try free/cheaper API first
        return await free_case_search(query)
    except:
        # Fallback to premium API
        return await legal_api.case_lookup_lexisnexis(query)
```

4. **Usage Monitoring**
```python
# Track API usage
class APIUsageTracker:
    def __init__(self):
        self.usage = {}
    
    def track(self, api_name: str, cost: float):
        if api_name not in self.usage:
            self.usage[api_name] = {"calls": 0, "cost": 0}
        self.usage[api_name]["calls"] += 1
        self.usage[api_name]["cost"] += cost
```

---

## Security Best Practices

### 1. Secure API Key Storage

**❌ Bad:**
```python
# Hardcoded in code
API_KEY = "sk_live_abc123..."
```

**✅ Good:**
```python
# Environment variable
API_KEY = os.getenv("LEGALZOOM_API_KEY")
```

### 2. Key Rotation

```bash
# Rotate keys regularly (every 90 days)
# Old key
LEGALZOOM_API_KEY=old_key_here

# New key (after rotation)
LEGALZOOM_API_KEY=new_key_here
```

### 3. Access Control

```python
# Only allow authorized users
@require_role(UserRole.PREMIUM)
async def case_lookup(request: CaseLookupRequest):
    # Only PREMIUM users can access
    pass
```

### 4. Audit Logging

```python
# Log all API calls
logger.info(f"API Call: {api_name}, User: {user_id}, Query: {query}")
```

---

## Monitoring & Analytics

### Track API Performance

```python
import time
from prometheus_client import Counter, Histogram

# Metrics
api_calls = Counter('api_calls_total', 'Total API calls', ['api_name', 'status'])
api_latency = Histogram('api_latency_seconds', 'API latency', ['api_name'])

async def monitored_api_call(api_name: str, func, *args, **kwargs):
    start_time = time.time()
    try:
        result = await func(*args, **kwargs)
        api_calls.labels(api_name=api_name, status='success').inc()
        return result
    except Exception as e:
        api_calls.labels(api_name=api_name, status='error').inc()
        raise
    finally:
        latency = time.time() - start_time
        api_latency.labels(api_name=api_name).observe(latency)
```

---

## Testing

### Unit Tests

```python
import pytest
from unittest.mock import Mock, patch

@pytest.mark.asyncio
async def test_case_lookup_success():
    """Test successful case lookup."""
    legal_api = get_legal_api_service()
    
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value.json.return_value = {
            "results": [{"case_name": "Test v. Case"}]
        }
        
        result = await legal_api.case_lookup_casetext("test query")
        assert result["success"] == True
        assert len(result["results"]) > 0

@pytest.mark.asyncio
async def test_case_lookup_fallback():
    """Test fallback to mock data on API failure."""
    legal_api = get_legal_api_service()
    
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.side_effect = Exception("API Error")
        
        result = await legal_api.case_lookup_casetext("test query")
        assert result["source"] == "Mock Data (API not configured)"
```

### Integration Tests

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_api_call():
    """Test real API call (requires API key)."""
    if not os.getenv("CASETEXT_API_KEY"):
        pytest.skip("API key not configured")
    
    legal_api = get_legal_api_service()
    result = await legal_api.case_lookup_casetext("Miranda v. Arizona")
    
    assert result["success"] == True
    assert len(result["results"]) > 0
```

---

## Troubleshooting

### Issue: API Key Not Working

**Symptoms:**
- 401 Unauthorized errors
- "Invalid API key" messages

**Solutions:**
1. Verify API key is correct (no extra spaces)
2. Check key is active (not expired)
3. Verify key has correct permissions
4. Check API endpoint URL is correct

### Issue: Slow API Responses

**Symptoms:**
- Timeout errors
- Slow document generation

**Solutions:**
1. Increase timeout value
2. Implement caching
3. Use async/await properly
4. Check network connectivity

### Issue: Rate Limit Errors

**Symptoms:**
- 429 Too Many Requests
- "Rate limit exceeded" messages

**Solutions:**
1. Implement rate limiting
2. Add exponential backoff
3. Cache frequent queries
4. Upgrade API plan

---

## Support

### API Provider Support

- **LegalZoom**: support@legalzoom.com
- **LexisNexis**: api-support@lexisnexis.com
- **CaseText**: support@casetext.com
- **Westlaw**: developer.support@thomsonreuters.com

### System Support

- Check logs: `backend/backend_detailed.log`
- Enable debug mode: `LOG_LEVEL=DEBUG`
- Contact: support@plaza-ai.com

---

## Additional Resources

### Documentation Links

- LegalZoom API Docs: https://developers.legalzoom.com/docs
- LexisNexis API Docs: https://developer.lexisnexis.com
- CaseText API Docs: https://casetext.com/api/docs
- Westlaw API Docs: https://developer.thomsonreuters.com/westlaw

### Code Examples

- See `backend/app/services/legal_api_integrations.py`
- See `LEGAL_DOCUMENT_GENERATION_GUIDE.md`

---

## Version History

**v1.0.0** - Initial release
- LegalZoom integration
- LexisNexis integration
- CaseText integration
- Westlaw integration (planned)
- Mock mode support

---

**Last Updated:** January 9, 2026  
**Status:** Production Ready
