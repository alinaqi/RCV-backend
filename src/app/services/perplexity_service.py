from typing import Dict, List, Optional
from openai import OpenAI
import logging
from datetime import datetime

from src.app.core.config import settings
from src.app.schemas.legal_context import LegalReference, ContractLegalContext

logger = logging.getLogger(__name__)

class PerplexityService:
    """Service for legal research using Perplexity AI."""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.PERPLEXITY_API_KEY,
            base_url="https://api.perplexity.ai"
        )
    
    async def analyze_contract_context(self, contract_text: str, jurisdiction: Optional[str] = None) -> ContractLegalContext:
        """
        Analyze contract to determine its topic and context.
        
        Args:
            contract_text (str): The contract text
            jurisdiction (Optional[str]): The specified jurisdiction
            
        Returns:
            ContractLegalContext: The contract's legal context
        """
        try:
            # First message to identify contract topic and create summary
            context_messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a legal expert. Analyze the contract to identify its main topic, "
                        "jurisdiction (if not specified), and provide a brief summary. "
                        "Format your response as JSON with keys: topic, jurisdiction, summary"
                    )
                },
                {
                    "role": "user",
                    "content": f"Contract text: {contract_text}\nSpecified jurisdiction: {jurisdiction if jurisdiction else 'Not specified'}"
                }
            ]
            
            context_response = self.client.chat.completions.create(
                model=settings.PERPLEXITY_MODEL,
                messages=context_messages,
            )
            
            context_data = eval(context_response.choices[0].message.content)
            
            # Second message to find relevant laws
            laws_messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a legal researcher. Find relevant laws and regulations for this contract. "
                        "Focus on the most important and recent laws. "
                        "Format each law as: {title, description, relevance, source}"
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
            )
            
            laws_data = eval(laws_response.choices[0].message.content)
            
            # Third message to find relevant cases
            cases_messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a legal researcher. Find relevant case law and precedents for this contract. "
                        "Focus on landmark cases and recent decisions. "
                        "Format each case as: {title, description, relevance, source}"
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
            )
            
            cases_data = eval(cases_response.choices[0].message.content)
            
            # Convert responses to objects
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
            
            return ContractLegalContext(
                topic=context_data['topic'],
                jurisdiction=context_data['jurisdiction'],
                summary=context_data['summary'],
                laws=laws,
                cases=cases
            )
            
        except Exception as e:
            logger.error(f"Error analyzing contract context with Perplexity: {str(e)}", exc_info=True)
            raise 