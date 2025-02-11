from typing import List, Optional
from anthropic import Anthropic
import logging
import json
import re

from src.app.core.config import settings
from src.app.schemas.contract import ContractAnalysis, Issue, Location
from src.app.schemas.legal_context import ContractLegalContext

logger = logging.getLogger(__name__)

class ClaudeService:
    """Service for contract analysis using Claude AI."""
    
    def __init__(self):
        logger.info("Initializing Claude service...")
        # Configure Anthropic client
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        
        # Verify API key is set
        if not settings.ANTHROPIC_API_KEY:
            logger.error("ANTHROPIC_API_KEY not found in environment variables")
            raise ValueError("ANTHROPIC_API_KEY must be set in environment variables")
            
        logger.info("✅ Claude service initialized successfully")
        
    def _extract_json_from_text(self, text: str) -> dict:
        """Extract JSON from text that might contain additional content."""
        logger.debug(f"Attempting to extract JSON from text: {text[:200]}...")
        try:
            # First try direct JSON parsing
            return json.loads(text)
        except json.JSONDecodeError:
            logger.debug("Direct JSON parsing failed, attempting to find JSON structure in text")
            try:
                # Try to find JSON-like structure in the text
                json_match = re.search(r'\{[\s\S]*\}', text)
                if json_match:
                    logger.debug("Found JSON structure in text")
                    return json.loads(json_match.group(0))
                logger.error("No JSON structure found in text")
                raise ValueError("No JSON structure found in response")
            except Exception as e:
                logger.error(f"Error extracting JSON from text: {str(e)}")
                raise ValueError(f"Failed to parse response as JSON: {text}")
        
    async def analyze_contract(
        self,
        contract_text: str,
        legal_context: ContractLegalContext,
        description: str,
        contract_type: Optional[str] = None
    ) -> ContractAnalysis:
        """
        Analyze a contract using Claude AI with legal context.
        
        Args:
            contract_text (str): The contract text to analyze
            legal_context (ContractLegalContext): Legal context including laws and cases
            description (str): Brief description of contract's purpose
            contract_type (Optional[str]): Type of contract
            
        Returns:
            ContractAnalysis: Analysis results including issues and suggestions
        """
        try:
            logger.info("Starting contract analysis with Claude...")
            logger.info(f"Input parameters - Description: {description}, Type: {contract_type}")
            logger.info(f"Legal context - Topic: {legal_context.topic}, Jurisdiction: {legal_context.jurisdiction}")
            
            # Build prompt with legal context
            logger.info("Building analysis prompt...")
            prompt = self._build_analysis_prompt(
                contract_text=contract_text,
                legal_context=legal_context,
                description=description,
                contract_type=contract_type
            )
            logger.debug(f"Generated prompt: {prompt[:500]}...")
            
            # Get analysis from Claude
            logger.info("Sending request to Claude API...")
            response = self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=8096,
                messages=[
                    {
                        "role": "assistant",
                        "content": (
                            "You are a legal expert analyzing contracts. "
                            "Provide detailed analysis including issues, suggestions, and risk assessment. "
                            "Respond ONLY with a JSON object containing these keys: issues (list), suggestions (list), risk_assessment (str). "
                            "Each issue must have: location (with paragraph and text), description, severity, suggestion. "
                            "Do not include any other text in your response."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0
            )
            
            # Parse response
            logger.debug(f"Raw Claude response: {response.content[0].text}")
            analysis_data = self._extract_json_from_text(response.content[0].text)
            logger.info(f"✅ Received analysis with {len(analysis_data['issues'])} issues and {len(analysis_data['suggestions'])} suggestions")
            
            # Convert issues to proper format
            logger.info("Converting issues to proper format...")
            issues = []
            for i, issue_data in enumerate(analysis_data['issues'], 1):
                logger.debug(f"Processing issue {i}: {issue_data['description'][:100]}...")
                # Extract numeric part from paragraph reference (e.g., 'P50' -> 50)
                try:
                    paragraph_str = str(issue_data['location']['paragraph'])
                    paragraph_num = int(''.join(filter(str.isdigit, paragraph_str)))
                except (ValueError, KeyError) as e:
                    logger.warning(f"Failed to parse paragraph number from {paragraph_str}, using index as fallback")
                    paragraph_num = i

                issues.append(Issue(
                    location=Location(
                        paragraph=paragraph_num,
                        text=issue_data['location']['text']
                    ),
                    description=issue_data['description'],
                    severity=issue_data['severity'],
                    suggestion=issue_data['suggestion']
                ))
            
            logger.info("✅ Contract analysis completed successfully")
            return ContractAnalysis(
                issues=issues,
                suggestions=analysis_data['suggestions'],
                risk_assessment=analysis_data['risk_assessment'],
                legal_context=legal_context
            )
            
        except Exception as e:
            logger.error(f"❌ Error analyzing contract with Claude: {str(e)}", exc_info=True)
            raise
            
    def _build_analysis_prompt(
        self,
        contract_text: str,
        legal_context: ContractLegalContext,
        description: str,
        contract_type: Optional[str] = None
    ) -> str:
        """Build the analysis prompt including legal context."""
        prompt = f"""
        Contract Description: {description}
        Contract Type: {contract_type if contract_type else 'Not specified'}
        
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