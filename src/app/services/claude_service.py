from typing import List, Optional
from openai import OpenAI
import logging

from src.app.core.config import settings
from src.app.schemas.contract import ContractAnalysis, Issue, Location
from src.app.schemas.legal_context import ContractLegalContext

logger = logging.getLogger(__name__)

class ClaudeService:
    """Service for contract analysis using Claude AI."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.ANTHROPIC_API_KEY)
        
    async def analyze_contract(
        self,
        contract_text: str,
        legal_context: ContractLegalContext
    ) -> ContractAnalysis:
        """
        Analyze a contract using Claude AI with legal context.
        
        Args:
            contract_text (str): The contract text to analyze
            legal_context (ContractLegalContext): Legal context including laws and cases
            
        Returns:
            ContractAnalysis: Analysis results including issues and suggestions
        """
        try:
            # Build prompt with legal context
            prompt = self._build_analysis_prompt(contract_text, legal_context)
            
            # Get analysis from Claude
            response = self.client.chat.completions.create(
                model=settings.CLAUDE_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a legal expert analyzing contracts. "
                            "Provide detailed analysis including issues, suggestions, and risk assessment. "
                            "Format your response as JSON with keys: issues (list), suggestions (list), risk_assessment (str)"
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse response
            analysis_data = eval(response.choices[0].message.content)
            
            # Convert issues to proper format
            issues = []
            for issue_data in analysis_data['issues']:
                issues.append(Issue(
                    location=Location(
                        paragraph=issue_data['location']['paragraph'],
                        text=issue_data['location']['text']
                    ),
                    description=issue_data['description'],
                    severity=issue_data['severity'],
                    suggestion=issue_data['suggestion']
                ))
            
            return ContractAnalysis(
                issues=issues,
                suggestions=analysis_data['suggestions'],
                risk_assessment=analysis_data['risk_assessment'],
                legal_context=legal_context
            )
            
        except Exception as e:
            logger.error(f"Error analyzing contract with Claude: {str(e)}", exc_info=True)
            raise
            
    def _build_analysis_prompt(self, contract_text: str, legal_context: ContractLegalContext) -> str:
        """Build the analysis prompt including legal context."""
        prompt = f"""
        Contract Text:
        {contract_text}
        
        Contract Topic: {legal_context.topic}
        Jurisdiction: {legal_context.jurisdiction}
        Summary: {legal_context.summary}
        
        Relevant Laws:
        """
        
        for law in legal_context.laws:
            prompt += f"""
            - {law.title}
              Description: {law.description}
              Relevance: {law.relevance}
              Source: {law.source}
            """
            
        prompt += "\nRelevant Cases:"
        
        for case in legal_context.cases:
            prompt += f"""
            - {case.title}
              Description: {case.description}
              Relevance: {case.relevance}
              Source: {case.source}
            """
            
        prompt += """
        Please analyze this contract considering the legal context provided. Focus on:
        1. Identifying potential issues and risks
        2. Suggesting improvements
        3. Assessing overall risk level
        4. Ensuring compliance with relevant laws
        5. Considering precedents from case law
        
        Format your response as JSON with:
        - issues: list of {location: {paragraph, text}, description, severity, suggestion}
        - suggestions: list of improvement suggestions
        - risk_assessment: overall risk assessment
        """
        
        return prompt 