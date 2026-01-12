# Matters & Workflows System

## Overview

The backend now includes a **Matters/Cases** system with workflow engines and playbook advice, designed like a focused version of Harvey.ai for traffic and small legal issues.

## Key Features

### 1. Matters Management
- Track individual legal matters (tickets, summons, fines)
- Associate documents with matters
- Store structured data (parsed ticket fields)
- Support for anonymous users (session_id) and authenticated users (user_id)

### 2. Workflow Engine
- State machines for each matter type
- Automatic next-step suggestions
- Event-driven state transitions
- Opinionated workflows for traffic tickets, parking tickets, bylaw fines

### 3. Playbook Advice
- Generate 2-3 structured options per matter
- A1: Conservative (plea/reduction)
- A2: Aggressive (defence/trial)
- A3: Lawyer consultation (when needed)
- **Multilingual support**: English, French, Hindi, Punjabi, Spanish, Tamil, Chinese

## API Endpoints

### Matters

#### Create Matter
```bash
POST /api/matters
{
  "user_id": "user123",
  "session_id": "session456",
  "jurisdiction": {
    "country": "Canada",
    "region": "Ontario",
    "region_code": "ON"
  },
  "matter_type": "traffic_ticket",
  "structured_data": {
    "offence": "Speeding 30 km/h over",
    "fine_amount": "$150",
    "date": "2024-01-15"
  }
}
```

#### Get Matter
```bash
GET /api/matters/{matter_id}
```

#### List Matters
```bash
GET /api/matters?user_id=user123&matter_type=traffic_ticket&status=new
```

#### Update Matter
```bash
PUT /api/matters/{matter_id}
{
  "status": "parsed",
  "structured_data": {
    "demerit_points": 4
  }
}
```

### Workflow

#### Get Next Steps
```bash
GET /api/matters/{matter_id}/next-steps

Response:
{
  "matter_id": "...",
  "current_status": "parsed",
  "next_steps": [
    {
      "step_id": "explain_options",
      "label": "Explain Your Options",
      "description": "Get personalized advice...",
      "action_type": "explain_options",
      "priority": 1,
      "required": true
    }
  ]
}
```

#### Process Workflow Event
```bash
POST /api/matters/{matter_id}/events/ticket_parsed

Response:
{
  "matter_id": "...",
  "previous_status": "new",
  "new_status": "parsed",
  "event": "ticket_parsed",
  "success": true
}
```

### Playbook

#### Get Playbook Options
```bash
POST /api/matters/{matter_id}/playbook?language=en

Response:
{
  "matter_id": "...",
  "matter_type": "traffic_ticket",
  "jurisdiction": {...},
  "options": [
    {
      "id": "A1",
      "label": "Conservative Option: Seek Reduction",
      "description": "Request a meeting with the prosecutor...",
      "risk_level": "low",
      "likely_outcomes": ["Reduced fine", "Fewer demerit points"],
      "key_reasons": ["Lower risk", "Faster process"],
      "estimated_cost": "$200-500",
      "estimated_time": "2-4 weeks",
      "recommended_for": "First-time offenders with clean records"
    },
    {
      "id": "A2",
      "label": "Defence Option: Challenge the Charge",
      "description": "Plead not guilty and proceed to trial...",
      "risk_level": "medium",
      "likely_outcomes": ["Possible acquittal", "Full penalty if unsuccessful"],
      "key_reasons": ["Chance of full dismissal", "May reveal weaknesses"]
    }
  ],
  "disclaimer": "This is general information only..."
}
```

**Supported Languages:**
- `en` - English
- `fr` - French
- `hi` - Hindi
- `pa` - Punjabi
- `es` - Spanish
- `ta` - Tamil
- `zh` - Chinese

## Workflow States

### Traffic Ticket Workflow
1. **new** → Parse ticket
2. **parsed** → Explain options
3. **options_explained** → Request disclosure OR Generate documents
4. **waiting_for_disclosure** → Review disclosure
5. **documents_generated** → Set reminder OR Schedule court
6. **reminder_set** → Schedule court
7. **court_scheduled** → Close matter
8. **closed** → End

### Parking Ticket Workflow
1. **new** → Parse ticket
2. **parsed** → Explain options
3. **options_explained** → Generate documents
4. **documents_generated** → Close matter
5. **closed** → End

## Integration with Ingestion

When ingesting documents, you can associate them with a matter:

```bash
POST /api/ingest/file?matter_id={matter_id}&subject=Traffic%20Violation
```

The document will be:
1. Ingested into Azure AI Search
2. Associated with the matter
3. Available for playbook generation

## Example Complete Flow

```bash
# 1. Create a matter
MATTER_ID=$(curl -X POST "http://localhost:8000/api/matters" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session123",
    "jurisdiction": {"country": "Canada", "region": "Ontario", "region_code": "ON"},
    "matter_type": "traffic_ticket"
  }' | jq -r '.matter_id')

# 2. Upload ticket image
curl -X POST "http://localhost:8000/api/ingest/image?matter_id=$MATTER_ID" \
  -F "file=@ticket.jpg"

# 3. Update matter with parsed data
curl -X PUT "http://localhost:8000/api/matters/$MATTER_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "parsed",
    "structured_data": {
      "offence": "Speeding 30 km/h over",
      "fine": "$150",
      "demerit_points": 4
    }
  }'

# 4. Get playbook options (in Hindi)
curl -X POST "http://localhost:8000/api/matters/$MATTER_ID/playbook?language=hi"

# 5. Get next steps
curl "http://localhost:8000/api/matters/$MATTER_ID/next-steps"

# 6. Process workflow event
curl -X POST "http://localhost:8000/api/matters/$MATTER_ID/events/user_chose_option_A"
```

## Storage

### Current Implementation
- Matters stored in JSON file: `./data/docs/matters.json`
- Suitable for development and small deployments

### GCP Production Options
1. **Firestore** (Recommended)
   - Replace JSON file with Firestore collection
   - Automatic scaling
   - Real-time updates

2. **Cloud SQL**
   - PostgreSQL or MySQL
   - Relational queries
   - ACID transactions

3. **Cloud Storage**
   - JSON files in GCS bucket
   - Simple migration from current implementation

## Multilingual Support

The playbook service generates advice in multiple languages:

- **English (en)**: Default
- **French (fr)**: For Quebec, France
- **Hindi (hi)**: For Indian communities
- **Punjabi (pa)**: For Punjabi-speaking communities
- **Spanish (es)**: For Spanish-speaking communities
- **Tamil (ta)**: For Tamil-speaking communities
- **Chinese (zh)**: For Chinese-speaking communities

The system prompt and disclaimers are automatically translated based on the `language` parameter.

## GCP Deployment

See `DEPLOYMENT_GCP.md` for complete GCP deployment instructions.

Key points:
- Deploy to Cloud Run or GKE
- Use Secret Manager for Azure credentials
- Optionally use Firestore for matters storage
- Use Cloud Storage for document storage
- Enable Cloud Logging and Monitoring

## Next Enhancements

1. **Document Generation**: Generate disclosure requests, response letters
2. **Calendar Integration**: Set reminders for court dates
3. **Multi-user Support**: User authentication and authorization
4. **Analytics**: Track matter outcomes and success rates
5. **Template Library**: Pre-built document templates
6. **Notification System**: Email/SMS reminders

