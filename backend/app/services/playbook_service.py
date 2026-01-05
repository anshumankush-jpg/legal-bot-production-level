"""Playbook service for generating structured legal advice options."""
import logging
import json
import re
from typing import List, Dict, Optional, Any
from pydantic import BaseModel

from app.models.matter import Matter, MatterType
from app.rag.rag_service import get_rag_service
from app.core.openai_client import get_openai_client
from app.core.config import settings

logger = logging.getLogger(__name__)


class PlaybookOption(BaseModel):
    """A playbook option for handling a matter."""
    id: str  # A1, A2, A3
    label: str
    description: str
    risk_level: str  # "low", "medium", "high"
    likely_outcomes: List[str]
    key_reasons: List[str]
    estimated_cost: Optional[str] = None
    estimated_time: Optional[str] = None
    recommended_for: Optional[str] = None


class PlaybookResponse(BaseModel):
    """Response containing playbook options."""
    matter_id: str
    matter_type: str
    jurisdiction: Dict[str, str]
    options: List[PlaybookOption]
    disclaimer: str


class PlaybookService:
    """Service for generating structured playbook advice."""
    
    def __init__(self):
        """Initialize playbook service."""
        self.rag_service = get_rag_service()
        self.openai_client = get_openai_client()
    
    def _get_language_prompt(self, language: str = "en") -> str:
        """Get language-specific prompt instructions."""
        language_map = {
            "en": "English",
            "fr": "French",
            "hi": "Hindi",
            "pa": "Punjabi",
            "es": "Spanish",
            "ta": "Tamil",
            "zh": "Chinese"
        }
        return language_map.get(language, "English")
    
    def generate_playbook(
        self,
        matter: Matter,
        language: str = "en"
    ) -> PlaybookResponse:
        """
        Generate playbook options for a matter.
        
        Args:
            matter: The matter to generate playbook for
            language: Language code (en, fr, hi, pa, es, ta, zh)
            
        Returns:
            Playbook response with structured options
        """
        # Build context query from matter
        jurisdiction_str = f"{matter.jurisdiction.get('country', '')} {matter.jurisdiction.get('region', '')}"
        matter_type_str = matter.matter_type.value.replace('_', ' ').title()
        
        # Extract key facts from structured data
        facts_summary = self._extract_facts_summary(matter.structured_data)
        
        # Build comprehensive query
        query = f"""
        I have a {matter_type_str} in {jurisdiction_str}.
        
        Key facts:
        {facts_summary}
        
        Please provide me with 2-3 structured options for how to proceed, including:
        1. A conservative option (plea/reduction/negotiation)
        2. A more aggressive option (defence/trial/technical challenge)
        3. Optionally, when to consult a full lawyer
        
        For each option, explain the risk level, likely outcomes, and key reasons.
        """
        
        # Get RAG context
        rag_result = self.rag_service.answer_question(
            query=query,
            top_k=10,
            hybrid_search=True,
            include_parent_context=True
        )
        
        # Generate structured playbook using LLM
        system_prompt = f"""You are a legal information assistant specializing in {matter_type_str} matters. 
You help users understand their options in {self._get_language_prompt(language)}.

Generate 2-3 structured options in JSON format. Each option should have:
- id: "A1", "A2", or "A3"
- label: Short descriptive label
- description: Detailed explanation
- risk_level: "low", "medium", or "high"
- likely_outcomes: List of possible outcomes
- key_reasons: List of reasons this option might be suitable
- estimated_cost: Rough cost estimate (if applicable)
- estimated_time: Time commitment estimate
- recommended_for: Who this option is best for

Respond ONLY with valid JSON in this format:
{{
  "options": [
    {{
      "id": "A1",
      "label": "...",
      "description": "...",
      "risk_level": "low",
      "likely_outcomes": ["..."],
      "key_reasons": ["..."],
      "estimated_cost": "...",
      "estimated_time": "...",
      "recommended_for": "..."
    }}
  ]
}}"""

        user_prompt = f"""Based on this context:

{rag_result['answer']}

And the retrieved sources:
{self._format_sources(rag_result['sources'])}

Generate structured playbook options for this {matter_type_str} matter in {jurisdiction_str}.
The user's situation: {facts_summary}

Provide 2-3 options (A1: conservative, A2: aggressive/defence, A3: lawyer consultation if needed).
Respond in {self._get_language_prompt(language)}."""

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
        
        try:
            response_text = self.openai_client.chat_completion(
                messages=messages,
                temperature=0.7
            )
            
            # Parse JSON from response
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                playbook_data = json.loads(json_match.group())
            else:
                # Fallback: try to parse entire response
                playbook_data = json.loads(response_text)
            
            # Convert to PlaybookOption objects
            options = [
                PlaybookOption(**opt) for opt in playbook_data.get('options', [])
            ]
            
            # Ensure we have at least 2 options
            if len(options) < 2:
                logger.warning(f"Only {len(options)} options generated, expected 2-3")
            
            disclaimer = self._get_disclaimer(language)
            
            return PlaybookResponse(
                matter_id=matter.matter_id,
                matter_type=matter.matter_type.value,
                jurisdiction=matter.jurisdiction,
                options=options,
                disclaimer=disclaimer
            )
            
        except Exception as e:
            logger.error(f"Error generating playbook: {e}")
            # Return fallback options
            return self._get_fallback_playbook(matter, language)
    
    def _extract_facts_summary(self, structured_data: Dict[str, Any]) -> str:
        """Extract key facts from structured data."""
        if not structured_data:
            return "No specific details extracted yet."
        
        facts = []
        if 'offence' in structured_data:
            facts.append(f"Offence: {structured_data['offence']}")
        if 'fine_amount' in structured_data:
            facts.append(f"Fine: {structured_data['fine_amount']}")
        if 'date' in structured_data:
            facts.append(f"Date: {structured_data['date']}")
        if 'location' in structured_data:
            facts.append(f"Location: {structured_data['location']}")
        if 'demerit_points' in structured_data:
            facts.append(f"Demerit Points: {structured_data['demerit_points']}")
        
        return "\n".join(facts) if facts else "Basic matter information available."
    
    def _format_sources(self, sources: List[Dict]) -> str:
        """Format sources for prompt."""
        if not sources:
            return "No specific sources retrieved."
        
        formatted = []
        for i, source in enumerate(sources[:5], 1):  # Top 5 sources
            formatted.append(
                f"{i}. {source.get('source_name', 'Unknown')} (Page {source.get('page', 'N/A')}): "
                f"{source.get('snippet', '')[:200]}..."
            )
        
        return "\n".join(formatted)
    
    def _get_disclaimer(self, language: str) -> str:
        """Get disclaimer in appropriate language."""
        disclaimers = {
            "en": "This is general information only, not legal advice. For advice about your specific case, consult a licensed lawyer or paralegal in your jurisdiction.",
            "fr": "Ceci est une information générale uniquement, pas un conseil juridique. Pour des conseils sur votre cas spécifique, consultez un avocat ou un parajuriste autorisé dans votre juridiction.",
            "hi": "यह केवल सामान्य जानकारी है, कानूनी सलाह नहीं है। अपने विशिष्ट मामले के बारे में सलाह के लिए, अपने अधिकार क्षेत्र में एक लाइसेंस प्राप्त वकील या पैरालीगल से परामर्श करें।",
            "pa": "ਇਹ ਸਿਰਫ਼ ਸਾਧਾਰਣ ਜਾਣਕਾਰੀ ਹੈ, ਕਾਨੂੰਨੀ ਸਲਾਹ ਨਹੀਂ ਹੈ। ਆਪਣੇ ਖਾਸ ਮਾਮਲੇ ਬਾਰੇ ਸਲਾਹ ਲਈ, ਆਪਣੇ ਅਧਿਕਾਰ ਖੇਤਰ ਵਿੱਚ ਇੱਕ ਲਾਇਸੰਸ ਪ੍ਰਾਪਤ ਵਕੀਲ ਜਾਂ ਪੈਰਾਲੀਗਲ ਨਾਲ ਸਲਾਹ ਮਸ਼ਵਰਾ ਕਰੋ।",
            "es": "Esta es solo información general, no asesoramiento legal. Para obtener asesoramiento sobre su caso específico, consulte con un abogado o parajurista con licencia en su jurisdicción.",
            "ta": "இது பொதுவான தகவல் மட்டுமே, சட்ட ஆலோசனை அல்ல. உங்கள் குறிப்பிட்ட வழக்கு பற்றிய ஆலோசனைக்கு, உங்கள் அதிகார வரம்பில் உள்ள உரிமம் பெற்ற வழக்கறிஞர் அல்லது பாராலீகலுடன் கலந்தாலோசிக்கவும்।",
            "zh": "这只是一般信息，不是法律建议。有关您具体案件的建议，请咨询您所在司法管辖区的持牌律师或法律助理。"
        }
        return disclaimers.get(language, disclaimers["en"])
    
    def _get_fallback_playbook(self, matter: Matter, language: str) -> PlaybookResponse:
        """Generate fallback playbook if LLM generation fails."""
        options = [
            PlaybookOption(
                id="A1",
                label="Conservative Option: Seek Reduction",
                description="Request a meeting with the prosecutor to negotiate a reduction in charges or penalties.",
                risk_level="low",
                likely_outcomes=["Reduced fine", "Fewer demerit points", "Faster resolution"],
                key_reasons=["Lower risk", "Faster process", "Predictable outcome"]
            ),
            PlaybookOption(
                id="A2",
                label="Defence Option: Challenge the Charge",
                description="Plead not guilty and proceed to trial, challenging the evidence and procedure.",
                risk_level="medium",
                likely_outcomes=["Possible acquittal", "Full penalty if unsuccessful", "More time required"],
                key_reasons=["Chance of full dismissal", "May reveal weaknesses in prosecution case"]
            )
        ]
        
        return PlaybookResponse(
            matter_id=matter.matter_id,
            matter_type=matter.matter_type.value,
            jurisdiction=matter.jurisdiction,
            options=options,
            disclaimer=self._get_disclaimer(language)
        )


# Global singleton instance
_playbook_service: Optional[PlaybookService] = None


def get_playbook_service() -> PlaybookService:
    """Get or create the global playbook service instance."""
    global _playbook_service
    if _playbook_service is None:
        _playbook_service = PlaybookService()
    return _playbook_service

