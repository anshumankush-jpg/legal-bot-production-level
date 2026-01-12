# Monitoring & Logging Setup

## Overview

This document outlines monitoring, logging, and analytics setup for the legal assistant system.

## 📊 Metrics to Track

### 1. Query Metrics
- Total queries per day
- Queries per user
- Average response time
- Queries with no relevant results (empty retrieval)
- Queries by language
- Queries by jurisdiction

### 2. User Metrics
- Active users per day/week/month
- New user registrations
- User retention
- Average queries per user

### 3. System Metrics
- API response times
- Error rates
- OCR success rate
- Document ingestion success rate
- Vector search performance

### 4. Quality Metrics
- Average retrieval score
- User feedback (thumbs up/down)
- Queries that returned "I don't have information"
- Parsed ticket accuracy

## 🔍 Logging Strategy

### What to Log

**User Actions:**
```python
logger.info("user_query", extra={
    "user_id": user_id,
    "question": question[:100],  # Truncate for privacy
    "language": language,
    "jurisdiction": jurisdiction,
    "timestamp": datetime.now()
})
```

**System Events:**
```python
logger.info("query_processed", extra={
    "query_id": query_id,
    "retrieval_count": len(results),
    "response_time_ms": response_time,
    "tokens_used": tokens,
    "model": "gpt-4o"
})
```

**Errors:**
```python
logger.error("query_failed", extra={
    "user_id": user_id,
    "error_type": type(e).__name__,
    "error_message": str(e),
    "stack_trace": traceback.format_exc()
})
```

### PII Safety

**Never Log:**
- Full user questions (truncate to 100 chars)
- Email addresses
- Phone numbers
- Full ticket images
- Personal identifying information

**Safe to Log:**
- User IDs (hashed)
- Jurisdiction
- Language
- Offence codes (anonymized)
- Aggregated statistics

## 📈 Analytics Endpoints

### Current Endpoints

```python
# GET /api/analytics/summary
# Returns aggregated statistics

# POST /api/analytics/feedback
# Submit user feedback
```

### Recommended Additions

```python
# GET /api/analytics/queries
# Query-level analytics with filters

# GET /api/analytics/users
# User-level analytics

# GET /api/analytics/performance
# System performance metrics
```

## 🛠️ Implementation Options

### Option 1: Simple Logging (MVP)
- Use Python `logging` module
- Write to files
- Basic aggregation scripts

### Option 2: Structured Logging
- Use `structlog` or similar
- JSON format logs
- Easy to parse and analyze

### Option 3: Full Monitoring Stack
- **Logging:** ELK Stack (Elasticsearch, Logstash, Kibana)
- **Metrics:** Prometheus + Grafana
- **APM:** Sentry for error tracking
- **Analytics:** Custom dashboard

## 📝 Log Format Example

```json
{
  "timestamp": "2024-03-15T14:30:00Z",
  "level": "INFO",
  "event": "query_processed",
  "user_id": "user_abc123",
  "query_id": "query_xyz789",
  "language": "en",
  "jurisdiction": "CA-ON",
  "question_preview": "What are my options...",
  "retrieval": {
    "chunks_found": 8,
    "avg_score": 0.82,
    "sources": ["pei_highway_traffic_act.pdf"]
  },
  "response": {
    "tokens_used": 450,
    "response_time_ms": 1250,
    "model": "gpt-4o"
  },
  "feedback": null
}
```

## 🚨 Alerting

### Critical Alerts
- API errors > 5% in 5 minutes
- Response time > 10 seconds
- OCR failure rate > 20%

### Warning Alerts
- Empty retrieval rate > 30%
- User feedback negative > 40%
- High token usage

## 📊 Dashboard Ideas

### Admin Dashboard
1. **Overview**
   - Total queries today
   - Active users
   - Average response time
   - Error rate

2. **Query Analysis**
   - Top questions
   - Queries by language
   - Queries by jurisdiction
   - Empty retrieval rate

3. **User Analytics**
   - New users
   - Active users
   - User retention
   - Queries per user

4. **System Health**
   - API uptime
   - Response times
   - Error rates
   - OCR success rate

## 🔐 Privacy Considerations

- Anonymize user data in logs
- Truncate questions
- Hash user IDs
- Comply with privacy regulations
- Regular log rotation and deletion

## 🚀 Quick Start

### Basic Logging Setup

```python
# backend/app/core/logging_config.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            **getattr(record, "extra", {})
        }
        return json.dumps(log_data)

# Configure logger
logger = logging.getLogger("weknowrights")
handler = logging.FileHandler("logs/app.log")
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Usage

```python
from app.core.logging_config import logger

logger.info("query_processed", extra={
    "user_id": user_id,
    "query_id": query_id,
    "response_time_ms": response_time
})
```

## 📚 Next Steps

1. **Phase 1 (MVP):** Basic file logging with JSON format
2. **Phase 2:** Add analytics aggregation
3. **Phase 3:** Set up monitoring dashboard
4. **Phase 4:** Add alerting

---

**Start simple, scale as needed.**

