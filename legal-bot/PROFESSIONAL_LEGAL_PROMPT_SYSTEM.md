# Professional Legal Prompt System

## Overview

The LeguBot system now includes a comprehensive, professional legal prompt system designed to provide formal, precise, and legally sound responses to user queries. This system ensures all responses follow legal professional standards with proper structure, citations, and disclaimers.

## Key Features

### 1. **Professional Tone and Structure**
- Formal, neutral, and respectful language
- Clear, organized responses with consistent formatting
- Appropriate legal terminology with definitions when needed
- Fact-based information without opinions or speculation

### 2. **Structured Response Format**

Every legal response follows this professional structure:

1. **Direct Answer**: Clear, concise answer to the specific question
2. **Legal Basis**: Relevant statutes, codes, sections, or precedents
3. **Detailed Explanation**: How the law applies to the situation
4. **Jurisdiction Context**: Which jurisdiction(s) the information applies to
5. **Key Information**: Important dates, sections, requirements, or deadlines (highlighted)
6. **Next Steps**: Guidance on procedures or actions (when applicable)
7. **Professional Disclaimer**: Mandatory legal disclaimer

### 3. **Citation Requirements**

All responses include proper legal citations:
- Specific legal sources: statutes, codes, acts, sections, articles
- Proper formatting: "Under Section X of the [Act Name]..."
- Jurisdiction information: "In [Province/State/Country]..."
- Case law references when relevant
- Explanation of relevance and application

### 4. **Jurisdiction Awareness**

The system is aware of different legal jurisdictions:

#### Supported Jurisdictions:
- **Canada** (Federal and Provincial)
  - Ontario (Common Law)
  - Quebec (Civil Law)
  - Other provinces and territories
- **United States** (Federal and State)
  - All 50 states
  - Federal law distinctions

#### Jurisdiction-Specific Features:
- Recognizes legal system differences (common law vs. civil law)
- Notes procedural variations by region
- Identifies federal vs. provincial/state jurisdiction
- Provides location-specific legal information

### 5. **Legal Category Support**

The system provides specialized guidance for different areas of law:

- **Criminal Law**: Offense classifications, penalties, defenses, rights
- **Traffic/Motor Vehicle Law**: Violations, fines, license consequences
- **Family Law**: Divorce, custody, support, property division
- **Civil Law**: Claims, litigation process, remedies, limitation periods
- **Immigration Law**: Applications, eligibility, procedures, appeals
- **Business/Commercial Law**
- **Employment Law**
- **Property Law**
- **Constitutional Law**
- And more...

### 6. **Multilingual Support**

Responses can be provided in multiple languages:
- English
- French (Français)
- Spanish (Español)
- Hindi (हिन्दी)
- Punjabi (ਪੰਜਾਬੀ)
- Chinese (中文)

All responses maintain professional legal standards in the target language.

### 7. **Document Integration**

The system seamlessly integrates with uploaded documents:
- Analyzes OCR-extracted text from images
- References specific document excerpts
- Cites document sources, pages, and sections
- Combines document content with legal knowledge
- Clearly indicates when documents are insufficient

## Example Responses

### Example 1: Criminal Law (Canada)

**Question:** What is the penalty for theft under Canadian Criminal Law?

**Response Structure:**

```
The penalty for theft in Canada is determined by the value of the stolen 
property and the Crown's election to proceed by summary conviction or indictment.

**Legal Basis:**
Under Section 334 of the Criminal Code of Canada, theft is categorized as follows:

1. Theft Under $5,000 (Section 334(b)):
   - If prosecuted by indictment: Maximum 2 years imprisonment
   - If prosecuted summarily: Maximum 6 months imprisonment and/or $5,000 fine

2. Theft Over $5,000 (Section 334(a)):
   - Indictable offense only
   - Maximum penalty: 10 years imprisonment

**Additional Considerations:**
- First-time offenders may receive conditional discharge, probation, or 
  suspended sentence depending on circumstances
- Aggravating factors can increase sentences
- Restitution to victims may be ordered
- A criminal record can result

**Next Steps:**
If charged with theft, you should:
1. Exercise your right to remain silent
2. Contact a criminal defense lawyer immediately
3. Do not discuss the case except with your lawyer
4. Attend all required court appearances

This is general legal information only, not legal advice. For advice specific 
to your situation, please consult a licensed criminal defense lawyer in your 
jurisdiction.
```

### Example 2: Family Law (USA)

**Question:** What are the grounds for divorce in the USA?

**Response Structure:**

```
Divorce grounds in the United States vary by state, but all states now allow 
some form of no-fault divorce, with many also permitting fault-based grounds.

**Legal Basis:**

**No-Fault Divorce** (Available in all 50 states):
- Irreconcilable differences or irretrievable breakdown of marriage
- No requirement to prove wrongdoing
- Some states require separation period

**Fault-Based Grounds** (Available in most states):
- Adultery
- Abandonment
- Cruelty
- Imprisonment
- Substance abuse

**State-Specific Examples:**
- California: No-fault only
- New York: No-fault or fault-based
- Texas: Both options available

[... continues with detailed explanation ...]

This is general legal information only, not legal advice. For advice specific 
to your situation, please consult a licensed family law attorney in your 
jurisdiction.
```

## Implementation

### Backend Integration

The professional prompt system is implemented in `backend/app/legal_prompts.py` and integrated into:

1. **Artillery Chat System** (`backend/app/main.py`)
   - Handles user-uploaded documents
   - OCR-extracted text integration
   - Real-time chat responses

2. **RAG System** (`backend/app/rag_prompt_builder.py`)
   - Legal document retrieval
   - Vector store integration
   - Citation management

### Usage in Code

#### Basic Usage:

```python
from app.legal_prompts import LegalPromptSystem

# Build a professional legal prompt
messages = LegalPromptSystem.build_professional_prompt(
    question="What is the penalty for speeding in Ontario?",
    jurisdiction="ontario",
    law_category="traffic",
    language="en"
)

# Use with LLM
response = llm_client.chat_completion(messages)
```

#### With Document Context:

```python
# Build prompt with uploaded documents
messages = LegalPromptSystem.build_artillery_prompt(
    question="What does this contract say about termination?",
    document_chunks=retrieved_chunks,
    jurisdiction="ontario",
    law_category="civil",
    language="en"
)
```

#### With Retrieved Legal Documents:

```python
# Build prompt with RAG-retrieved documents
messages = LegalPromptSystem.build_professional_prompt(
    question="What are the requirements for a valid will?",
    document_context=formatted_legal_documents,
    jurisdiction="canada",
    law_category="estate",
    language="en"
)
```

## Quality Standards

### Response Quality Criteria:

1. **Accuracy**: All information must be factually correct and based on actual law
2. **Clarity**: Explanations must be understandable to non-lawyers
3. **Completeness**: Cover all relevant aspects of the question
4. **Professionalism**: Maintain formal legal standards throughout
5. **Practicality**: Provide actionable information where appropriate

### Mandatory Elements:

- ✅ Formal, professional tone
- ✅ Specific legal citations
- ✅ Jurisdiction identification
- ✅ Structured formatting
- ✅ Key information highlighted
- ✅ Professional disclaimer
- ✅ Clear next steps (when applicable)

### Prohibited Elements:

- ❌ Personal opinions or speculation
- ❌ Oversimplified legal advice
- ❌ Information not grounded in law
- ❌ Casual or informal language
- ❌ Missing citations or sources
- ❌ Ambiguous jurisdiction references

## Benefits

### For Users:
- Professional, trustworthy legal information
- Clear, structured responses
- Proper legal citations and references
- Jurisdiction-specific information
- Actionable next steps
- Multilingual support

### For Developers:
- Centralized prompt management
- Consistent response quality
- Easy customization by jurisdiction/category
- Reusable prompt components
- Clear documentation and examples

### For Legal Professionals:
- Maintains professional standards
- Proper disclaimers and limitations
- Accurate legal citations
- Appropriate scope of information
- Encourages professional consultation

## Testing the System

### Test with Different Scenarios:

1. **Criminal Law Question**:
   ```
   "What is the penalty for DUI in California?"
   ```

2. **Traffic Law Question**:
   ```
   "What happens if I get caught speeding 30 km/h over the limit in Ontario?"
   ```

3. **Family Law Question**:
   ```
   "How is child custody determined in divorce cases?"
   ```

4. **With Uploaded Document**:
   ```
   Upload a legal document → Ask: "What are the key terms in this contract?"
   ```

5. **Multilingual**:
   ```
   Set language to French → Ask any legal question
   ```

### Expected Response Quality:

Each response should:
- Start with a clear, direct answer
- Include specific legal citations
- Explain the law in understandable terms
- Specify the jurisdiction
- Highlight key information
- Provide next steps (if applicable)
- End with a professional disclaimer

## Customization

### Adding New Jurisdictions:

Edit `backend/app/legal_prompts.py`:

```python
JURISDICTION_PROMPTS = {
    'new_jurisdiction': """
**NEW JURISDICTION LEGAL CONTEXT:**
- Specific legal system information
- Key statutes and codes
- Procedural notes
- Unique characteristics
"""
}
```

### Adding New Legal Categories:

```python
CATEGORY_PROMPTS = {
    'new_category': """
**NEW CATEGORY FOCUS:**
When answering [category] questions:
- Specific guidance for this area
- Key statutes to reference
- Important considerations
- Typical procedures
"""
}
```

### Adding Example Responses:

```python
EXAMPLE_RESPONSES = {
    'example_key': """[Full example response following the structure]"""
}
```

## Future Enhancements

Potential improvements to the system:

1. **Enhanced Citation Formatting**
   - Bluebook citation style
   - McGill Guide citation style
   - Jurisdiction-specific formats

2. **Case Law Integration**
   - Relevant case citations
   - Precedent explanations
   - Case law summaries

3. **Procedural Flowcharts**
   - Step-by-step legal processes
   - Timeline visualizations
   - Required forms and documents

4. **Interactive Clarifications**
   - Follow-up question suggestions
   - Jurisdiction disambiguation
   - Scope refinement prompts

5. **Legal Term Glossary**
   - Automatic term definitions
   - Plain language explanations
   - Jurisdiction-specific terminology

## Support and Feedback

For questions, issues, or suggestions regarding the professional legal prompt system:

1. Check this documentation first
2. Review example responses in `backend/app/legal_prompts.py`
3. Test with various scenarios
4. Consult the implementation code for technical details

## Conclusion

The Professional Legal Prompt System transforms LeguBot into a sophisticated legal information assistant that provides responses meeting professional legal standards. By ensuring proper structure, citations, disclaimers, and jurisdiction awareness, the system delivers reliable, trustworthy legal information to users while maintaining appropriate boundaries between information and advice.

---

**Last Updated**: January 2026  
**Version**: 1.0  
**System**: LeguBot Professional Legal Assistant
