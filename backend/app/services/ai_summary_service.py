"""
AI-Powered Case Summary Service
Generates intelligent summaries of legal conversations using OpenAI
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class AISummaryService:
    """Service for generating AI-powered case summaries."""
    
    def __init__(self, openai_client=None):
        self.openai_client = openai_client
    
    async def generate_case_summary(
        self,
        messages: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive AI case summary from conversation.
        
        Args:
            messages: List of chat messages (user and assistant)
            metadata: Additional context (law type, jurisdiction, etc.)
            
        Returns:
            Dictionary with structured case summary
        """
        try:
            logger.info(f"[AI_SUMMARY] Starting summary generation for {len(messages)} messages")
            
            # Validate messages
            if not messages or len(messages) == 0:
                raise ValueError("No messages provided for summary generation")
            
            # Extract conversation
            conversation_text = self._format_conversation(messages)
            logger.info(f"[AI_SUMMARY] Formatted conversation: {len(conversation_text)} chars")
            
            # Generate summary using OpenAI or fallback
            if self.openai_client:
                logger.info("[AI_SUMMARY] Using OpenAI for summary generation")
                try:
                    # Build AI prompt for summary generation
                    summary_prompt = self._build_summary_prompt(conversation_text, metadata)
                    summary_content = await self._generate_with_openai(summary_prompt)
                    
                    # Structure the summary
                    structured_summary = self._structure_summary(summary_content, messages, metadata)
                    
                    return {
                        "success": True,
                        "summary": structured_summary,
                        "generated_at": datetime.now().isoformat(),
                        "message_count": len(messages)
                    }
                except Exception as openai_error:
                    logger.warning(f"[AI_SUMMARY] OpenAI failed, using fallback: {openai_error}")
                    # Fall through to basic summary
            
            # Use basic summary (fallback or no OpenAI)
            logger.info("[AI_SUMMARY] Using basic summary generation (fallback)")
            basic_summary = self._generate_basic_summary(messages, metadata)
            
            return {
                "success": True,
                "summary": basic_summary,
                "generated_at": datetime.now().isoformat(),
                "message_count": len(messages),
                "note": "Basic summary generated (OpenAI not available)"
            }
            
        except Exception as e:
            logger.error(f"Failed to generate case summary: {e}", exc_info=True)
            # Return error with basic fallback
            try:
                basic_summary = self._generate_basic_summary(messages, metadata)
                return {
                    "success": True,
                    "summary": basic_summary,
                    "generated_at": datetime.now().isoformat(),
                    "message_count": len(messages),
                    "note": f"Basic summary generated due to error: {str(e)}"
                }
            except:
                return {
                    "success": False,
                    "error": f"Failed to generate summary: {str(e)}. Please ensure you have messages in the conversation."
                }
    
    def _format_conversation(self, messages: List[Dict[str, Any]]) -> str:
        """Format conversation for AI analysis."""
        formatted = []
        
        for msg in messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content') or msg.get('message') or msg.get('response', '')
            timestamp = msg.get('timestamp', '')
            
            if role == 'user':
                formatted.append(f"CLIENT: {content}")
            elif role == 'assistant':
                formatted.append(f"ASSISTANT: {content}")
        
        return "\n\n".join(formatted)
    
    def _build_summary_prompt(self, conversation: str, metadata: Optional[Dict]) -> str:
        """Build prompt for AI summary generation."""
        
        law_type = metadata.get('law_category') or metadata.get('law_type', 'General Law') if metadata else 'General Law'
        jurisdiction = metadata.get('jurisdiction', 'Not specified') if metadata else 'Not specified'
        
        prompt = f"""You are a legal assistant analyzing a conversation between a client and a legal AI assistant.

CONVERSATION CONTEXT:
- Law Type: {law_type}
- Jurisdiction: {jurisdiction}
- Date: {datetime.now().strftime('%Y-%m-%d')}

CONVERSATION TRANSCRIPT:
{conversation}

Please generate a comprehensive LEGAL CASE SUMMARY with the following sections:

1. CLIENT SITUATION
   - What is the client's main legal issue?
   - What are the key facts and circumstances?
   - What happened and when?

2. LEGAL ISSUES IDENTIFIED
   - What specific legal matters are involved?
   - What laws or regulations apply?
   - What are the potential violations or claims?

3. ADVICE PROVIDED
   - What guidance was given to the client?
   - What options were discussed?
   - What actions were recommended?

4. KEY FACTS & EVIDENCE
   - Important dates, locations, parties
   - Documents mentioned
   - Evidence discussed

5. NEXT STEPS
   - What should the client do next?
   - What deadlines or timeframes apply?
   - What documents are needed?

6. RISK ASSESSMENT
   - What are the potential outcomes?
   - What are the strengths of the case?
   - What are the weaknesses or concerns?

7. PROFESSIONAL RECOMMENDATIONS
   - Should the client consult a lawyer?
   - What type of lawyer is needed?
   - How urgent is the matter?

Format the summary professionally, clearly, and concisely. Use bullet points where appropriate.
Be specific and reference actual details from the conversation.

IMPORTANT: This is a summary of general legal information provided, NOT legal advice."""

        return prompt
    
    async def _generate_with_openai(self, prompt: str) -> str:
        """Generate summary using OpenAI."""
        try:
            from app.core.openai_client_unified import chat_completion
            
            messages = [
                {
                    'role': 'system',
                    'content': 'You are an expert legal analyst creating case summaries. Be thorough, professional, and specific.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
            
            response = chat_completion(
                messages=messages,
                temperature=0.3,  # Lower temperature for consistent summaries
                max_tokens=2000
            )
            
            return response
            
        except Exception as e:
            logger.error(f"OpenAI summary generation failed: {e}")
            raise
    
    def _generate_basic_summary(
        self,
        messages: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate basic summary without AI (fallback)."""
        
        # Extract key information
        user_messages = [m for m in messages if m.get('role') == 'user']
        assistant_messages = [m for m in messages if m.get('role') == 'assistant']
        
        # Get first user message as situation
        situation = user_messages[0].get('content', 'Not provided') if user_messages else 'Not provided'
        
        # Extract keywords
        keywords = self._extract_keywords(messages)
        
        # Calculate duration
        duration = "N/A"
        if messages and len(messages) > 1:
            try:
                first_time = messages[0].get('timestamp')
                last_time = messages[-1].get('timestamp')
                if first_time and last_time:
                    duration = f"{len(messages)} messages"
            except:
                pass
        
        # Create formatted summary text
        summary_text = f"""1. CLIENT SITUATION
{situation[:500]}

2. LEGAL ISSUES IDENTIFIED
Based on the conversation, the client discussed matters related to {metadata.get('law_category', 'general law') if metadata else 'general law'}.

3. ADVICE PROVIDED
The assistant provided {len(assistant_messages)} detailed responses addressing the client's questions and concerns.

4. KEY FACTS & EVIDENCE
- Total conversation messages: {len(messages)}
- Client questions: {len(user_messages)}
- Assistant responses: {len(assistant_messages)}
- Keywords identified: {', '.join(keywords) if keywords else 'None'}

5. NEXT STEPS
- Review the full conversation for specific recommendations
- Consider consulting with a licensed attorney for personalized advice
- Gather any documents mentioned in the conversation

6. RISK ASSESSMENT
This basic summary cannot provide detailed risk assessment. For comprehensive analysis, please ensure OpenAI API is configured.

7. PROFESSIONAL RECOMMENDATIONS
- Consult with a licensed attorney in your jurisdiction
- Bring all relevant documents and evidence
- Act promptly on any time-sensitive matters discussed

NOTE: This is a basic summary. For AI-powered detailed analysis, please configure OpenAI API key."""
        
        return {
            "summary_text": summary_text,
            "metadata": {
                "law_type": metadata.get('law_category') if metadata else 'Not specified',
                "jurisdiction": metadata.get('jurisdiction') if metadata else 'Not specified'
            },
            "conversation_stats": {
                "total_messages": len(messages),
                "user_messages": len(user_messages),
                "assistant_messages": len(assistant_messages),
                "duration": duration
            },
            "generated_at": datetime.now().isoformat(),
            "note": "Basic summary generated (OpenAI not available)"
        }
    
    def _extract_keywords(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extract keywords from conversation."""
        keywords = set()
        legal_terms = [
            'penalty', 'fine', 'court', 'judge', 'lawyer', 'attorney',
            'charge', 'offense', 'violation', 'law', 'statute', 'regulation',
            'rights', 'defense', 'evidence', 'trial', 'hearing', 'appeal',
            'contract', 'agreement', 'liability', 'damages', 'settlement'
        ]
        
        for msg in messages:
            content = (msg.get('content') or msg.get('message') or '').lower()
            for term in legal_terms:
                if term in content:
                    keywords.add(term)
        
        return list(keywords)[:10]
    
    def _structure_summary(
        self,
        ai_content: str,
        messages: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Structure the AI-generated summary."""
        
        return {
            "summary_text": ai_content,
            "metadata": {
                "law_type": metadata.get('law_category') if metadata else 'Not specified',
                "jurisdiction": metadata.get('jurisdiction') if metadata else 'Not specified',
                "language": metadata.get('language') if metadata else 'en',
                "country": metadata.get('country') if metadata else 'Not specified',
                "province": metadata.get('province') if metadata else None
            },
            "conversation_stats": {
                "total_messages": len(messages),
                "user_messages": len([m for m in messages if m.get('role') == 'user']),
                "assistant_messages": len([m for m in messages if m.get('role') == 'assistant']),
                "duration": self._calculate_duration(messages)
            },
            "generated_at": datetime.now().isoformat(),
            "format": "ai_generated"
        }
    
    def _calculate_duration(self, messages: List[Dict[str, Any]]) -> str:
        """Calculate conversation duration."""
        if len(messages) < 2:
            return "N/A"
        
        try:
            first_time = messages[0].get('timestamp')
            last_time = messages[-1].get('timestamp')
            
            if isinstance(first_time, str):
                first_time = datetime.fromisoformat(first_time.replace('Z', '+00:00'))
            if isinstance(last_time, str):
                last_time = datetime.fromisoformat(last_time.replace('Z', '+00:00'))
            
            duration = last_time - first_time
            minutes = int(duration.total_seconds() / 60)
            
            if minutes < 1:
                return "Less than 1 minute"
            elif minutes < 60:
                return f"{minutes} minutes"
            else:
                hours = minutes // 60
                return f"{hours} hour{'s' if hours > 1 else ''}"
        except:
            return "N/A"


# Singleton instance
_ai_summary_service = None

def get_ai_summary_service():
    """Get or create AI summary service singleton."""
    global _ai_summary_service
    if _ai_summary_service is None:
        try:
            from app.core.config import settings
            import openai
            # Only pass api_key - proxies and other unsupported args are not allowed
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
            _ai_summary_service = AISummaryService(openai_client=client)
        except:
            _ai_summary_service = AISummaryService(openai_client=None)
    return _ai_summary_service
