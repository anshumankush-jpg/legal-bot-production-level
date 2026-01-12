"""
Integration Script: Enhanced Legal Prompts with Backend
Updates the backend to use the new enhanced prompt system
"""

import os
import shutil
from datetime import datetime

# Enhanced system prompt to add to backend
ENHANCED_BACKEND_PROMPT = '''
# ENHANCED LEGAL RESPONSE SYSTEM

You are an advanced legal information assistant. For EVERY legal question, follow this structure:

## 1. INTRODUCTION (2-3 sentences)
- Professional summary of the legal topic
- State relevant jurisdiction(s)
- Base responses on law, statutes, and cases only

## 2. KEY LEGAL DETAILS
- **Primary Law/Act**: [Full name]
- **Specific Section(s)**: [Numbers with description]
- **Jurisdiction**: [Federal/Provincial/State]
- **Effective Date**: [When enacted]

## 3. DETAILED EXPLANATION
- Clear explanation in accessible language
- Penalties, requirements, obligations
- Exceptions or special circumstances

## 4. OFFICIAL SOURCES (MANDATORY - ALWAYS INCLUDE)
Format each source as:
- **[Law Name]**: [Section numbers]
  - Official Website: [Full government URL]
  - Citation: [Proper legal citation]

Examples:
- **Criminal Code of Canada**: Sections 334, 322
  - Official Website: https://laws-lois.justice.gc.ca/eng/acts/C-46/
  - Citation: Criminal Code, RSC 1985, c C-46

- **18 U.S.C. § 1344**: Bank Fraud
  - Official Website: https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title18-section1344
  - Citation: 18 U.S.C. § 1344

## 5. REAL-TIME UPDATES (If within last 2 years)
- **Recent Changes**: [Amendments]
- **Proposed Legislation**: [Bills under consideration]
- **Effective Date**: [When changes take effect]
- **Source**: [Official URL]

## 6. RELEVANT CASE STUDIES (Provide 1-2 cases)
Format:
- **Case Name**: [Full citation]
- **Year**: [Year decided]
- **Court**: [Which court]
- **Key Ruling**: [Brief summary]
- **Relevance**: [How it applies]
- **Citation**: [Proper case citation]

Example:
- **R v. St-Onge Lamoureux**: 2012 SCC 57
  - **Court**: Supreme Court of Canada
  - **Key Ruling**: Established breathalyzer demand standards
  - **Relevance**: Sets precedent for DUI cases

## 7. MULTI-JURISDICTIONAL COMPARISON (If applicable)
- **Canada**: [Summary]
- **United States**: [Summary]
- **Key Differences**: [Variations]

## 8. PRACTICAL IMPLICATIONS
- Who is affected?
- What are the consequences?
- What should someone do?

## 9. NEXT STEPS
- **Immediate Actions**: [What to do now]
- **Legal Consultation**: [When to see lawyer]
- **Resources**: [Where to find info]
- **Monitoring**: [How to stay updated]

## CITATION REQUIREMENTS

### Canadian Laws:
- Format: [Act Name], [RSC/RSO], [year], c [chapter], s [section]
- Always include: laws-lois.justice.gc.ca or provincial .gov.ca URLs
- Example: "Criminal Code, RSC 1985, c C-46, s 334"

### US Laws:
- Format: [Title] U.S.C. § [Section]
- Always include: uscode.house.gov or official .gov URLs
- Example: "18 U.S.C. § 1344"

### Case Law:
- Format: [Case Name], [Year] [Court] [Number]
- Example: "R v. Grant, 2009 SCC 32"

## SPECIAL SCENARIOS

### Immigration (e.g., Venezuela policy changes):
- Cite: Immigration and Nationality Act (INA) sections
- Reference: Executive Orders by number
- Include: USCIS/IRCC announcements
- Provide: Official .gov/.gc.ca sources

### Traffic Accidents (e.g., California truck crash):
- Cite: Vehicle Code or Highway Traffic Act
- Reference: Recent bills and amendments
- Include: Safety regulations
- Provide: DMV or Ministry sources

### Border Regulations:
- Cite: Both US and Canadian laws
- Reference: CBP and CBSA regulations
- Include: Entry requirements
- Provide: Official border agency sources

## MANDATORY ELEMENTS
✅ ALWAYS cite specific section numbers
✅ ALWAYS provide official government URLs
✅ ALWAYS include at least 1 case study (if relevant)
✅ ALWAYS mention recent updates (if any in last 2 years)
✅ ALWAYS use the structure above
✅ NEVER provide opinions
✅ NEVER skip the sources section

## DISCLAIMER (Always include at end)
"This information is for educational purposes only and does not constitute legal advice. Laws change frequently. For specific legal situations, consult a qualified attorney in your jurisdiction."
'''


def backup_file(filepath: str):
    """Create a backup of a file"""
    if os.path.exists(filepath):
        backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(filepath, backup_path)
        print(f"[OK] Backed up: {filepath} -> {backup_path}")
        return backup_path
    return None


def update_backend_prompt():
    """Update the backend with enhanced prompts"""
    
    backend_main = "backend/app/main.py"
    
    if not os.path.exists(backend_main):
        print(f"[X] Backend file not found: {backend_main}")
        print("[INFO] Please ensure backend is in the correct location")
        return False
    
    print("\n" + "="*80)
    print("INTEGRATING ENHANCED PROMPTS INTO BACKEND")
    print("="*80)
    
    # Backup the file
    backup_path = backup_file(backend_main)
    
    # Read current content
    with open(backend_main, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create enhanced prompt file
    prompt_file = "backend/app/enhanced_legal_prompt.txt"
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(ENHANCED_BACKEND_PROMPT)
    
    print(f"[OK] Created enhanced prompt file: {prompt_file}")
    
    # Instructions for manual integration
    print("\n" + "="*80)
    print("INTEGRATION INSTRUCTIONS")
    print("="*80)
    print("""
To integrate the enhanced prompts into your backend:

1. AUTOMATIC METHOD (Recommended):
   - The enhanced prompt has been saved to: backend/app/enhanced_legal_prompt.txt
   - Add this code to your backend/app/main.py in the chat endpoint:
   
   ```python
   # Load enhanced prompt
   with open('app/enhanced_legal_prompt.txt', 'r') as f:
       enhanced_prompt = f.read()
   
   # Prepend to user message
   full_prompt = enhanced_prompt + "\\n\\nUser Question: " + user_message
   ```

2. MANUAL METHOD:
   - Open: backend/app/main.py
   - Find the chat endpoint (usually /api/artillery/chat)
   - Add the enhanced prompt as a system message
   - Ensure it's sent before the user's question

3. VERIFICATION:
   - Restart the backend
   - Test with a question
   - Check if response includes all required sections

4. EXAMPLE INTEGRATION:
   ```python
   @app.post("/api/artillery/chat")
   async def chat(request: ChatRequest):
       # Load enhanced prompt
       enhanced_prompt = load_enhanced_prompt()
       
       # Combine with user question
       messages = [
           {"role": "system", "content": enhanced_prompt},
           {"role": "user", "content": request.message}
       ]
       
       # Send to LLM
       response = await llm.chat(messages)
       return response
   ```
""")
    
    print("\n[OK] Integration instructions provided")
    print(f"[OK] Backup created: {backup_path}")
    print(f"[OK] Enhanced prompt file: {prompt_file}")
    
    return True


def create_integration_guide():
    """Create a detailed integration guide"""
    
    guide = """# Enhanced Legal Prompt Integration Guide

## Overview
This guide explains how to integrate the enhanced legal prompt system into your backend to provide comprehensive, well-cited legal responses.

## What's New

The enhanced system provides:
- ✅ Structured responses with 9 mandatory sections
- ✅ Specific section and article citations
- ✅ Official government website URLs
- ✅ Case study references
- ✅ Real-time legal updates
- ✅ Multi-jurisdictional comparisons
- ✅ Practical implications and next steps

## Integration Steps

### Step 1: Add Enhanced Prompt to Backend

1. Copy `backend/app/enhanced_legal_prompt.txt` to your backend
2. Load it in your chat endpoint:

```python
# At the top of your file
ENHANCED_PROMPT_FILE = "app/enhanced_legal_prompt.txt"

def load_enhanced_prompt():
    with open(ENHANCED_PROMPT_FILE, 'r', encoding='utf-8') as f:
        return f.read()

# In your chat endpoint
@app.post("/api/artillery/chat")
async def chat(request: ChatRequest):
    enhanced_prompt = load_enhanced_prompt()
    
    # Combine with user question
    full_prompt = f"{enhanced_prompt}\\n\\nUser Question: {request.message}"
    
    # Send to your LLM
    response = await your_llm_function(full_prompt)
    return response
```

### Step 2: Update LLM Call

If using OpenAI:
```python
messages = [
    {"role": "system", "content": load_enhanced_prompt()},
    {"role": "user", "content": request.message}
]

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=messages,
    temperature=0.3  # Lower for more factual responses
)
```

If using Ollama:
```python
prompt = load_enhanced_prompt() + "\\n\\nUser Question: " + request.message

response = ollama.generate(
    model="llama2",
    prompt=prompt
)
```

### Step 3: Test the Integration

Run these test questions:

1. "What are the penalties for theft under $5000 in Canada?"
2. "What are the new immigration laws regarding Venezuela?"
3. "What are the penalties for DUI in California?"

Expected response format:
```
### Introduction
[2-3 sentence summary]

### Key Legal Details
- **Primary Law**: Criminal Code of Canada
- **Specific Sections**: Section 334
- **Jurisdiction**: Federal
- **Effective Date**: 1985

### Detailed Explanation
[Full explanation]

### Official Sources
- **Criminal Code of Canada**: Section 334
  - Official Website: https://laws-lois.justice.gc.ca/eng/acts/C-46/
  - Citation: Criminal Code, RSC 1985, c C-46, s 334

[... rest of sections ...]
```

### Step 4: Verify All Sections

Check that responses include:
- ✅ Introduction
- ✅ Key Legal Details
- ✅ Detailed Explanation
- ✅ Official Sources with URLs
- ✅ Real-Time Updates (if applicable)
- ✅ Case Studies
- ✅ Practical Implications
- ✅ Next Steps
- ✅ Disclaimer

## Troubleshooting

### Issue: Responses don't follow structure
**Solution**: Increase the system prompt weight or use temperature=0.3

### Issue: Missing URLs
**Solution**: Emphasize "MANDATORY" in the prompt for sources section

### Issue: No case studies
**Solution**: Add "ALWAYS include at least 1 case study" to prompt

### Issue: Responses too long
**Solution**: Adjust max_tokens parameter in LLM call

## Performance Optimization

1. **Cache the enhanced prompt**: Load once at startup
2. **Use streaming**: Stream responses for better UX
3. **Implement timeout**: Set 60s timeout for complex queries
4. **Add retry logic**: Retry failed requests with exponential backoff

## Example Implementation

See `backend/app/main.py` for a complete example.

## Testing

After integration, run:
```bash
python advanced_legal_source_test.py
```

Expected results:
- 90%+ source match rate
- 70%+ article match rate
- 50%+ website match rate
- All responses include case studies

## Support

For issues, check:
1. Backend logs: `backend_detailed.log`
2. Test results: `advanced_legal_test_results_*.json`
3. Integration guide: This file

---

**Last Updated**: January 8, 2026
**Version**: 2.0
**Status**: Ready for Integration
"""
    
    with open("ENHANCED_PROMPT_INTEGRATION_GUIDE.md", 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("[OK] Created integration guide: ENHANCED_PROMPT_INTEGRATION_GUIDE.md")


def main():
    """Main integration function"""
    
    print("\n" + "="*80)
    print("ENHANCED LEGAL PROMPT SYSTEM - INTEGRATION")
    print("="*80)
    
    # Update backend
    success = update_backend_prompt()
    
    # Create integration guide
    create_integration_guide()
    
    print("\n" + "="*80)
    print("INTEGRATION COMPLETE")
    print("="*80)
    print("""
Next Steps:
1. Review: ENHANCED_PROMPT_INTEGRATION_GUIDE.md
2. Integrate: Add enhanced prompt to backend/app/main.py
3. Test: Run python advanced_legal_source_test.py
4. Verify: Check that responses include all sections

Files Created:
- backend/app/enhanced_legal_prompt.txt
- ENHANCED_PROMPT_INTEGRATION_GUIDE.md
- backend/app/main.py.backup_* (if exists)
""")
    
    if success:
        print("\n[SUCCESS] Enhanced prompt system ready for integration!")
    else:
        print("\n[INFO] Manual integration required - see guide above")


if __name__ == "__main__":
    main()
