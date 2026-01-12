# Soft Scope Approach - Be Helpful First! ✅

## Philosophy Change
The bot now uses a **SOFT SCOPE** approach - it answers questions helpfully and naturally, only redirecting to lawyers when questions become truly personal or require specific legal strategy.

## What Changed

### Before (Hard Scope)
- ❌ Heavy disclaimers on every response
- ❌ Overly cautious about providing information
- ❌ Frequent "consult a lawyer" warnings
- ❌ Made users feel like they couldn't get help

### After (Soft Scope)
- ✅ Helpful and informative by default
- ✅ Answers questions thoroughly
- ✅ Light disclaimers for general questions
- ✅ Only suggests lawyer consultation when truly needed

## When Bot ANSWERS Normally (No Redirect)

### ✅ General "How To" Questions
```
User: "How do I file a claim in small claims court?"
Bot: [Provides detailed step-by-step process]
Disclaimer: "This is general legal information to help you understand the process."
```

### ✅ Explanations of Laws
```
User: "What are the penalties for speeding in Ontario?"
Bot: [Explains fines, demerit points, consequences]
Disclaimer: Brief or none needed
```

### ✅ Typical Procedures
```
User: "What's the process for disputing a traffic ticket?"
Bot: [Explains the dispute process clearly]
Disclaimer: Light
```

### ✅ Documentation Requirements
```
User: "What documents do I need for small claims court?"
Bot: [Lists required documents and explains each]
Disclaimer: Minimal
```

### ✅ Common Outcomes
```
User: "What usually happens in a first DUI offense?"
Bot: [Explains typical penalties and process]
Disclaimer: "This is general information about typical outcomes."
```

## When Bot Suggests Lawyer (Redirect)

### 🔄 Personal Strategy Questions
```
User: "Should I personally plead guilty or fight my ticket?"
Bot: [Provides general info about both options]
Then: "For advice on which option is best for your specific situation, I recommend consulting with a licensed lawyer or paralegal who can review your circumstances."
```

### 🔄 Document Review Requests
```
User: "Can you review my contract and tell me if it's good?"
Bot: "While I can explain general contract principles, reviewing your specific contract requires a lawyer who can examine all the details and provide advice tailored to your situation."
```

### 🔄 Prediction About Personal Case
```
User: "Will I win my case if I go to court?"
Bot: [Explains factors courts consider]
Then: "Predicting outcomes for your specific case requires a lawyer who can review all your evidence and circumstances."
```

### 🔄 Acting as Personal Lawyer
```
User: "What should I do next in MY case?"
Bot: [Provides general information about typical next steps]
Then: "For guidance specific to your case, consider consulting with a licensed lawyer or paralegal."
```

## Disclaimer Levels

### Level 1: Brief (General Questions)
```
"This is general legal information to help you understand the process."
```
**Use for:** How-to questions, process explanations, general law information

### Level 2: Moderate (Some Personal Details)
```
"For advice specific to your situation, consider consulting with a licensed lawyer or paralegal."
```
**Use for:** Questions that mention personal circumstances but are still general

### Level 3: Full (Very Personal/Strategic)
```
"While I can provide general information, for advice tailored to your specific circumstances, I recommend consulting with a licensed lawyer or paralegal in your jurisdiction."
```
**Use for:** Strategy questions, personal predictions, document reviews

## Key Principles

### 1. **Be Helpful First**
- Answer the question thoroughly
- Provide useful, actionable information
- Don't hide behind disclaimers

### 2. **Use Common Sense**
- Not every question needs a heavy disclaimer
- General information is okay to provide
- Only redirect when truly necessary

### 3. **Natural Tone**
- Don't make every response feel like a legal warning
- Be conversational and supportive
- Users should feel helped, not blocked

### 4. **Clear Boundaries**
- Know the difference between general info and personal advice
- Redirect gracefully when needed
- Explain WHY you're suggesting a lawyer

## Examples

### ✅ GOOD - Helpful Response
```
User: "How do I dispute a parking ticket?"

Bot: "Thank you for reaching out. I can help you understand the process for disputing a parking ticket. Here's what you typically need to do:

**Step 1: Check the Ticket** - Review the ticket for the deadline to file a dispute (usually 15-30 days).

**Step 2: Gather Evidence** - Collect photos, receipts, or other evidence that supports your case.

**Step 3: File Your Dispute** - Submit your dispute online or by mail to the address on the ticket.

**Step 4: Attend the Hearing** - If required, attend the hearing and present your evidence.

This is general information to help you understand the process. For questions about your specific ticket, the contact information should be on the ticket itself."
```

### ✅ GOOD - Gentle Redirect When Needed
```
User: "Should I personally hire a lawyer for my DUI case?"

Bot: "Thank you for your question. I can explain the general considerations:

Many people facing DUI charges do consult with a lawyer because:
- DUI cases can have serious consequences (license suspension, fines, criminal record)
- A lawyer can review the specific evidence in your case
- They can identify potential defenses or procedural issues
- They can negotiate with prosecutors

However, whether you personally should hire a lawyer depends on:
- The specific facts of your case
- Your prior record
- The evidence against you
- Your financial situation
- The potential penalties you're facing

For advice on whether hiring a lawyer is right for YOUR specific situation, I recommend consulting with a licensed DUI lawyer who can review your case details and provide personalized guidance."
```

### ❌ BAD - Too Cautious (Old Approach)
```
User: "What is speeding?"

Bot: "Speeding is exceeding the posted speed limit. However, this is general legal information only, not legal advice. Laws vary by jurisdiction. For advice specific to your situation, please consult a licensed lawyer or paralegal. This does not create an attorney-client relationship."

[TOO MUCH DISCLAIMER FOR A SIMPLE QUESTION!]
```

## Implementation

### File Updated
`legal-bot/backend/app/legal_prompts.py`

### Key Changes

#### 1. Soft Scope Rules
```python
**CRITICAL RULES (SOFT SCOPE APPROACH):**
1. Be helpful and answer questions thoroughly - don't be overly cautious
2. Provide general legal information about processes, laws, and procedures
7. **Only redirect to lawyers when:**
   - Question asks "What should I personally do in my case?"
   - Question requires reviewing specific personal documents
   - Question asks for specific legal strategy or predictions
8. **Don't redirect for:**
   - General "how to" questions
   - Explanations of laws and processes
   - Typical steps and procedures
```

#### 2. Flexible Disclaimers
```python
**For General Questions:**
- Brief: "This is general legal information to help you understand the process."

**For Personal Details:**
- Moderate: "For advice specific to your situation, consider consulting..."

**For Very Personal Questions:**
- Full disclaimer with clear explanation
```

## Benefits

### For Users
1. **More Helpful**: Get actual answers to their questions
2. **Less Frustrating**: Not constantly told to "see a lawyer"
3. **More Informative**: Learn about legal processes
4. **Better Experience**: Feel supported, not blocked
5. **Clearer Guidance**: Know when they really do need a lawyer

### For Legal Safety
1. **Still Protected**: Appropriate disclaimers when needed
2. **Clear Boundaries**: Distinguishes general info from personal advice
3. **Proper Redirects**: Suggests lawyers for truly personal matters
4. **Responsible**: Doesn't overstep into personal legal advice

## Testing

### Test Question 1: General Process
```bash
"How do I file for divorce?"
```
**Expected:** Detailed process steps with brief disclaimer

### Test Question 2: Personal Strategy
```bash
"Should I personally get a divorce or try counseling?"
```
**Expected:** General info about both options + suggest consulting a family lawyer

### Test Question 3: Simple Definition
```bash
"What is a will?"
```
**Expected:** Clear explanation with minimal or no disclaimer

### Test Question 4: Personal Case
```bash
"Will I win my case against my landlord?"
```
**Expected:** Explain factors courts consider + redirect to lawyer for personal prediction

## Status: ✅ IMPLEMENTED

The bot now uses a soft scope approach:
- Answers questions helpfully and thoroughly
- Uses appropriate disclaimers based on question type
- Only redirects to lawyers when truly necessary
- Provides a better, more helpful user experience

## Date: January 9, 2026 - 10:30 AM

The system is now configured to be helpful first, with smart redirects only when needed!
