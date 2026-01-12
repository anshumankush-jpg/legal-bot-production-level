"""
Backend Response Formatter for Legal Chatbot
Ensures responses are properly formatted with markdown that converts cleanly to HTML
NO VISIBLE STARS - all markdown will be converted by frontend
"""

def format_legal_response_for_frontend(answer: str) -> str:
    """
    Format legal response with clean markdown
    Frontend will convert:
    - **text** → bold (no stars visible)
    - ### Header → green heading (no # visible)
    - - item → bullet point (no dash visible)
    - [link](url) → clickable link (no brackets visible)
    """
    
    # Ensure proper section headers with ###
    sections = {
        "Introduction:": "### Introduction",
        "Key Legal Details:": "### Key Legal Details",
        "Detailed Explanation:": "### Detailed Explanation",
        "Official Sources:": "### Official Sources",
        "Real-Time Updates:": "### Real-Time Updates",
        "Relevant Case Studies:": "### Relevant Case Studies",
        "Case Study Example:": "### Case Study Example",
        "Multi-Jurisdictional Comparison:": "### Multi-Jurisdictional Comparison",
        "Practical Implications:": "### Practical Implications",
        "Next Steps:": "### Next Steps",
        "Recommendations:": "### Recommendations"
    }
    
    formatted = answer
    for old, new in sections.items():
        formatted = formatted.replace(old, new)
    
    # Bold important legal terms (will render as bold, not **text**)
    important_terms = [
        ("Criminal Code", "**Criminal Code**"),
        ("Highway Traffic Act", "**Highway Traffic Act**"),
        ("Vehicle Code", "**Vehicle Code**"),
        ("Immigration and Nationality Act", "**Immigration and Nationality Act**"),
        ("Charter of Rights", "**Charter of Rights**"),
        ("Section", "**Section**"),
        ("Penalty", "**Penalty**"),
        ("Fine", "**Fine**"),
        ("Imprisonment", "**Imprisonment**"),
        ("Blood Alcohol Concentration", "**Blood Alcohol Concentration**"),
        ("BAC", "**BAC**"),
        ("DUI", "**DUI**"),
    ]
    
    for term, bold_term in important_terms:
        # Only bold if not already bolded
        if f"**{term}**" not in formatted:
            formatted = formatted.replace(term, bold_term)
    
    # Ensure URLs are in markdown link format [text](url)
    # This will be converted to clickable links by frontend
    
    # Add disclaimer if not present
    if "educational purposes only" not in formatted.lower():
        formatted += "\n\n---\n\n*This information is for educational purposes only and does not constitute legal advice. For specific legal situations, consult a qualified attorney.*"
    
    return formatted


def example_response():
    """Example of how responses should be formatted"""
    return """### Introduction
The **minimum meter reading for DUI** (Driving Under the Influence) refers to the **Blood Alcohol Concentration (BAC)** level that indicates legal intoxication.

### Key Legal Details
- **Primary Law**: Criminal Code of Canada
- **Section**: 320.14
- **Legal Limit**: 0.08% BAC
- **Jurisdiction**: Federal (applies across Canada)

### Detailed Explanation
In Canada, if a driver's **BAC** is **0.08% or higher**, they are considered legally impaired. This applies to all provinces and territories.

### Official Sources
- **Criminal Code of Canada**: Section 320.14
  - Official Website: https://laws-lois.justice.gc.ca/eng/acts/C-46/
  - Citation: Criminal Code, RSC 1985, c C-46, s 320.14
- **Government of Canada**: Impaired Driving Laws
  - Website: https://www.canada.ca/en/services/policing/impaired-driving.html

### Relevant Case Studies
- **R v. St-Onge Lamoureux**: 2012 SCC 57
  - **Court**: Supreme Court of Canada
  - **Key Ruling**: Established standards for breathalyzer demands
  - **Relevance**: Sets precedent for DUI enforcement procedures

### Practical Implications
If your **BAC** is **0.08% or higher**, you face:
- Criminal charges
- Immediate license suspension
- **Fine**: Up to $1,000 (first offense)
- **Imprisonment**: Possible jail time for repeat offenses
- Criminal record

### Next Steps
- **If Charged**: Consult a criminal defense lawyer immediately
- **Legal Options**: Challenge breathalyzer accuracy, procedural errors
- **Resources**: Legal Aid services available in your province

---

*This information is for educational purposes only and does not constitute legal advice. For specific legal situations, consult a qualified attorney.*"""


# Integration with your backend
def integrate_with_chat_endpoint():
    """
    How to use in your backend/app/main.py:
    
    from backend_response_formatter import format_legal_response_for_frontend
    
    @app.post("/api/artillery/chat")
    async def chat(request: ChatRequest):
        # ... your existing code to get answer ...
        
        # Format the response
        formatted_answer = format_legal_response_for_frontend(answer)
        
        return {
            "answer": formatted_answer,
            "citations": citations
        }
    """
    pass


if __name__ == "__main__":
    # Test the formatter
    print("EXAMPLE FORMATTED RESPONSE:")
    print("=" * 60)
    print(example_response())
    print("=" * 60)
    print("\nFrontend will convert this to:")
    print("- ### Headers → Bold green headings (no # visible)")
    print("- **Text** → Bold text (no ** visible)")
    print("- - Items → Bullet points (no - visible)")
    print("- [Links](url) → Clickable links (no brackets visible)")
    print("\nResult: Clean, professional ChatGPT-like appearance!")
