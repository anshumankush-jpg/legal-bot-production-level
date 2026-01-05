# Paralegal Advice Case Study Dataset

## Overview

This dataset contains structured case studies with paralegal advice for traffic violations across Canada and the United States. Each case includes facts, applicable law, and multiple advice variants based on different risk tolerances and client goals.

## Structure

```
paralegal_advice_dataset/
├── schema/
│   └── case_schema.json          # JSON schema for case structure
├── canada/
│   ├── CAN-ON-TRAFFIC-0001.json   # Ontario speeding case
│   ├── CAN-BC-TRAFFIC-0002.json   # BC red light camera case
│   └── CAN-QC-TRAFFIC-0003.json   # Quebec excessive speeding case
├── usa/
│   ├── USA-CA-TRAFFIC-0001.json   # California unsafe speed case
│   ├── USA-NY-TRAFFIC-0002.json   # New York work zone case
│   └── USA-TX-TRAFFIC-0003.json   # Texas reckless driving case
└── README.md                       # This file
```

## Case ID Format

- **Canada**: `CAN-{PROVINCE_CODE}-{LAW_TYPE}-{NUMBER}`
  - Example: `CAN-ON-TRAFFIC-0001` (Ontario traffic case #1)
  
- **USA**: `USA-{STATE_CODE}-{LAW_TYPE}-{NUMBER}`
  - Example: `USA-CA-TRAFFIC-0001` (California traffic case #1)

## Schema Components

Each case includes:

1. **Case Identification**: Unique case ID and jurisdiction information
2. **Case Metadata**: Year, area of law, offence code and label
3. **Facts**: Detailed facts, aggravating/mitigating factors, defence issues
4. **Law**: Applicable statutes and guideline documents
5. **Outcome**: Real outcome if known (most are hypothetical)
6. **Paralegal Advice**: 
   - Client profile (goals, risk tolerance)
   - Multiple advice variants (conservative, moderate, aggressive)
   - Each variant includes risk level, benefits, and key reasons

## Usage

This dataset is designed for:
- Training legal AI models on paralegal reasoning patterns
- RAG (Retrieval Augmented Generation) systems for legal advice
- Understanding jurisdiction-specific approaches
- Generating synthetic training data for legal AI applications

## Legal Disclaimer

**IMPORTANT**: All cases in this dataset are either:
- Hypothetical examples for educational purposes
- Based on general legal principles
- Not actual legal advice

These examples are for training AI systems and understanding legal reasoning patterns. They should NOT be used as actual legal advice. Always consult with a licensed lawyer or paralegal for actual legal matters.

## Expansion

To add more cases:
1. Follow the schema in `schema/case_schema.json`
2. Use the case ID format appropriate for the jurisdiction
3. Include multiple advice variants reflecting different approaches
4. Ensure all disclaimers are included

## Jurisdictions Covered

### Canada
- Ontario (ON)
- British Columbia (BC)
- Quebec (QC)

### United States
- California (CA)
- New York (NY)
- Texas (TX)

## Next Steps

1. Expand to cover all provinces/states
2. Add more case types (DUI, distracted driving, etc.)
3. Include case law citations where applicable
4. Add outcome data from real cases (with proper attribution)
5. Create embeddings for RAG systems

