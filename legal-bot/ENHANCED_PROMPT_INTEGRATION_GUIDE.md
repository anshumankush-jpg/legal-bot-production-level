# Enhanced Legal Prompt Integration Guide

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
    full_prompt = f"{enhanced_prompt}\n\nUser Question: {request.message}"
    
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
prompt = load_enhanced_prompt() + "\n\nUser Question: " + request.message

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
