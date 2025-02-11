from typing import Dict, List, Optional
from openai import OpenAI
import logging
import json
import re
from datetime import datetime

from src.app.core.config import settings
from src.app.schemas.legal_context import LegalReference, ContractLegalContext

logger = logging.getLogger(__name__)

class PerplexityService:
    """Service for legal research using Perplexity AI."""
    
    def __init__(self):
        logger.info("Initializing Perplexity service...")
        # Configure OpenAI client for Perplexity API
        self.client = OpenAI(
            base_url="https://api.perplexity.ai",
            api_key=settings.PERPLEXITY_API_KEY
        )
        
        # Verify API key is set
        if not settings.PERPLEXITY_API_KEY:
            logger.error("PERPLEXITY_API_KEY not found in environment variables")
            raise ValueError("PERPLEXITY_API_KEY must be set in environment variables")
            
        logger.info("✅ Perplexity service initialized successfully")
    
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
    
    async def analyze_contract_context(
        self, 
        contract_text: str, 
        description: str,
        jurisdiction: Optional[str] = None,
        contract_type: Optional[str] = None
    ) -> ContractLegalContext:
        """
        Analyze contract to determine its topic and context.
        
        Args:
            contract_text (str): The contract text
            description (str): Brief description of contract's purpose
            jurisdiction (Optional[str]): The specified jurisdiction
            contract_type (Optional[str]): Type of contract
            
        Returns:
            ContractLegalContext: The contract's legal context
        """
        try:
            logger.info("Starting contract context analysis...")
            logger.info(f"Input parameters - Description: {description}, Type: {contract_type}, Jurisdiction: {jurisdiction}")
            
            # First message to identify contract topic and create summary
            logger.info("Step 1: Identifying contract topic and creating summary...")
            context_messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a legal expert. Analyze the contract to identify its main topic, "
                        "jurisdiction (if not specified), and provide a brief summary. "
                        "Respond ONLY with a JSON object containing these keys: topic, jurisdiction, summary. "
                        "Do not include any other text in your response."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Contract description: {description}\n"
                        f"Contract type: {contract_type if contract_type else 'Not specified'}\n"
                        f"Specified jurisdiction: {jurisdiction if jurisdiction else 'Not specified'}\n\n"
                        f"Contract text: {contract_text[:500]}..."  # Log first 500 chars
                    )
                }
            ]
            
            context_response = self.client.chat.completions.create(
                model=settings.PERPLEXITY_MODEL,
                messages=context_messages,
                temperature=0
            )
            
            logger.debug(f"Raw context response: {context_response.choices[0].message.content}")
            context_data = self._extract_json_from_text(context_response.choices[0].message.content)
            logger.info(f"✅ Contract context identified - Topic: {context_data['topic']}, Jurisdiction: {context_data['jurisdiction']}")
            
            # Second message to find relevant laws
            logger.info("Step 2: Finding relevant laws...")
            laws_messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a legal researcher. Find relevant laws and regulations for this contract. "
                        "Focus on the most important and recent laws. "
                        "Respond ONLY with a JSON array of laws, where each law has: title, description, relevance, source. "
                        "Do not include any other text in your response."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Find relevant laws for a {context_data['topic']} contract in {context_data['jurisdiction']}. "
                        f"Contract summary: {context_data['summary']}"
                    )
                }
            ]
            
            laws_response = self.client.chat.completions.create(
                model=settings.PERPLEXITY_MODEL,
                messages=laws_messages,
                temperature=0
            )
            
            logger.debug(f"Raw laws response: {laws_response.choices[0].message.content}")
            laws_data = self._extract_json_from_text(laws_response.choices[0].message.content)
            logger.info(f"✅ Found {len(laws_data)} relevant laws")
            
            # Third message to find relevant cases
            logger.info("Step 3: Finding relevant cases...")
            cases_messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a legal researcher. Find relevant case law and precedents for this contract. "
                        "Focus on landmark cases and recent decisions. "
                        "Respond ONLY with a JSON array of cases, where each case has: title, description, relevance, source. "
                        "Do not include any other text in your response."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Find relevant cases for a {context_data['topic']} contract in {context_data['jurisdiction']}. "
                        f"Contract summary: {context_data['summary']}"
                    )
                }
            ]
            
            cases_response = self.client.chat.completions.create(
                model=settings.PERPLEXITY_MODEL,
                messages=cases_messages,
                temperature=0
            )
            
            logger.debug(f"Raw cases response: {cases_response.choices[0].message.content}")
            cases_data = self._extract_json_from_text(cases_response.choices[0].message.content)
            logger.info(f"✅ Found {len(cases_data)} relevant cases")
            
            # Convert responses to objects
            logger.info("Converting responses to objects...")
            laws = [
                LegalReference(
                    title=law['title'],
                    description=law['description'],
                    relevance=law['relevance'],
                    source=law['source'],
                    reference_type='law'
                ) for law in laws_data
            ]
            
            cases = [
                LegalReference(
                    title=case['title'],
                    description=case['description'],
                    relevance=case['relevance'],
                    source=case['source'],
                    reference_type='case'
                ) for case in cases_data
            ]
            
            logger.info("✅ Contract context analysis completed successfully")
            return ContractLegalContext(
                topic=context_data['topic'],
                jurisdiction=context_data['jurisdiction'],
                summary=context_data['summary'],
                laws=laws,
                cases=cases
            )
            
        except Exception as e:
            logger.error(f"❌ Error analyzing contract context with Perplexity: {str(e)}", exc_info=True)
            raise 