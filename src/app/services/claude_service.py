from typing import Dict, Any, Optional
import anthropic
from datetime import datetime
import json
import logging

from src.app.core.config import settings
from src.app.schemas.contract import ContractAnalysis

logger = logging.getLogger(__name__)

class ClaudeService:
    """Service for analyzing contracts using Claude AI."""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL
    
    def _build_analysis_prompt(
        self,
        contract_text: str,
        sections: Dict[str, str],
        description: str,
        contract_type: Optional[str] = None,
        jurisdiction: Optional[str] = None
    ) -> str:
        """Build the prompt for contract analysis."""
        context_parts = [f"Contract Description: {description}"]
        if contract_type:
            context_parts.append(f"Contract Type: {contract_type}")
        if jurisdiction:
            context_parts.append(f"Jurisdiction: {jurisdiction}")
        
        context = "\n".join(context_parts)
        
        jurisdiction_note = " (especially considering the specified jurisdiction)" if jurisdiction else ""
        improvement_note = " considering the jurisdiction's legal requirements" if jurisdiction else ""
        
        return f"""You are a legal contract analyzer. You will analyze the following contract based on this context:

{context}

Analyze the contract with these instructions:

1. Identify and assess key clauses:
   - Liability provisions
   - Payment terms
   - Notice periods
   - Termination conditions
   - Jurisdiction and governing law{jurisdiction_note}

2. For each identified issue:
   - Specify the type of issue
   - Assess severity (Critical/High/Medium/Low/Info)
   - Provide specific location in the text (using [P1], [P2], etc. references)
   - Explain the potential risk
   - Suggest improvements{improvement_note}

Contract text:
{contract_text}

Provide analysis in JSON format matching this structure:
{{
    "issues": [
        {{
            "type": "string",
            "severity": "critical|high|medium|low|info",
            "description": "string",
            "location": {{
                "paragraph": number,
                "text": "string"
            }},
            "suggestion": "string"
        }}
    ],
    "suggestions": [
        {{
            "category": "string",
            "description": "string",
            "current": "string",
            "suggested": "string"
        }}
    ],
    "risk_score": number (0-100)
}}"""

    async def analyze_contract(
        self,
        contract_text: str,
        sections: Dict[str, str],
        description: str,
        contract_type: Optional[str] = None,
        jurisdiction: Optional[str] = None
    ) -> ContractAnalysis:
        """
        Analyze contract using Claude AI.
        
        Args:
            contract_text (str): The parsed contract text
            sections (Dict[str, str]): Extracted contract sections
            description (str): Brief description of the contract's purpose
            contract_type (Optional[str]): Type of contract (e.g., service, employment)
            jurisdiction (Optional[str]): Country or region where the contract will be enforced
            
        Returns:
            ContractAnalysis: The analysis results
        """
        try:
            prompt = self._build_analysis_prompt(
                contract_text=contract_text,
                sections=sections,
                description=description,
                contract_type=contract_type,
                jurisdiction=jurisdiction
            )
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE,
                system="You are an expert legal contract analyzer. Provide analysis in the exact JSON format requested.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse Claude's response
            response_text = message.content[0].text
            analysis_dict = json.loads(response_text)
            
            # Add timestamp and initialize empty redlines list
            analysis_dict["analysis_timestamp"] = datetime.utcnow()
            analysis_dict["redlines"] = []  # Initialize empty redlines list
            
            return ContractAnalysis(**analysis_dict)
            
        except Exception as e:
            logger.error(f"Error analyzing contract with Claude: {str(e)}", exc_info=True)
            raise 