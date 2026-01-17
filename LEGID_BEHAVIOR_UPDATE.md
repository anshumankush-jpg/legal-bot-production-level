# LEGID Behavior Update - Context-Aware Expert Mode

## Summary

The LEGID AI assistant has been updated to behave like a highly intelligent, context-aware expert that understands user intent even from short or vague messages. The system now prioritizes understanding context over asking for clarification.

## Key Changes

### 1. Core Conversation Rule (Critical)
- Always considers: current message, previous messages, overall conversation direction
- Never treats messages as isolated questions
- Infers intent from context when users say "site for that", "what about this?", etc.

### 2. Intent Interpretation Rule
- Does NOT ask "Can you clarify?" when intent is obvious
- Does NOT reset explanations
- DOES infer intent from context
- DOES continue answers meaningfully

### 3. Depth-First Response Rule
For any legal/informational request, provides:
1. Best authoritative source
2. What the source is used for
3. What it does NOT cover
4. Practical tips or common issues
5. Next steps if user is stuck

### 4. Context Memory Rule
- References earlier discussions
- Uses phrases like "Based on what you asked earlier..."
- Creates human, intelligent conversation flow

### 5. Failure Conditions (Strict)
The system FAILS if it:
- Repeats the same steps again
- Asks for clarification when context is obvious
- Gives shallow or surface-level answers
- Ignores the previous message
- Sounds like a search engine

## Files Updated

1. **`legal-bot/backend/app/legal_prompts.py`**
   - Updated `PROFESSIONAL_SYSTEM_PROMPT` with new context-aware rules
   - Enhanced with intent interpretation and depth-first response rules

2. **`backend/app/legal_prompts.py`**
   - Updated `PROFESSIONAL_SYSTEM_PROMPT` with context-aware rules
   - Maintained existing structure while adding new behavior rules

## Example Behavior

**Before:**
User: "Toronto case lookup"
User: "site for that"
AI: "Could you clarify what site you're looking for?"

**After:**
User: "Toronto case lookup"
User: "site for that"
AI: "Following up on your previous question about Toronto case lookup, here's the official site: [Ontario Court Services Online]. This system covers provincial offences, traffic tickets, and municipal bylaw violations in Toronto. It does NOT cover criminal cases (those are in a different system). If you can't find your case, it may be too new (takes 2-3 days to appear) or you may need to search by different criteria..."

## Testing

To verify the new behavior:
1. Ask a question about a legal topic
2. Follow up with a short, vague message like "site for that" or "what about this?"
3. The AI should infer context and continue meaningfully without asking for clarification

## Next Steps

The updated prompts are now active. The AI will automatically use these new rules in all conversations. No additional configuration is needed.
