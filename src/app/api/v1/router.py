from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Optional
import logging
from datetime import datetime

from src.app.services.claude_service import ClaudeService
from src.app.services.perplexity_service import PerplexityService
from src.app.services.docx_service import DocxService
from src.app.schemas.contract import (
    ContractAnalysisResponse, 
    ContractAnalysisError, 
    RedlineItem,
    ContractAnalysis,
    ContractLegalContext
)
from src.app.core.config import settings
from src.app.core.dependencies import get_services

logger = logging.getLogger(__name__)

api_router = APIRouter()

@api_router.post("/analyze-contract", response_model=ContractAnalysisResponse)
async def analyze_contract(
    description: str,
    file: UploadFile = File(...),
    services: tuple[ClaudeService, PerplexityService, DocxService] = Depends(get_services),
    contract_type: Optional[str] = None,
    jurisdiction: Optional[str] = None
) -> ContractAnalysisResponse:
    """
    Analyze a contract document through a 4-step process:
    1. Validate the contract and extract text/redlines
    2. Identify contract topic, jurisdiction, and summary
    3. Find relevant laws and cases
    4. Analyze contract using legal context

    Args:
        description: Brief description of contract's purpose
        file: DOCX file containing the contract
        contract_type: Type of contract (e.g., employment, service, NDA)
        jurisdiction: Country or region where the contract will be enforced
    """
    try:
        claude_service, perplexity_service, docx_service = services
        
        # Step 1: Validate and parse contract
        logger.info("Step 1: Validating and parsing contract")
        contract_text, redlines = await docx_service.parse_contract(file)
        
        # Step 2 & 3: Get legal context
        logger.info("Step 2 & 3: Getting legal context")
        legal_context = await perplexity_service.analyze_contract_context(
            contract_text=contract_text,
            description=description,
            jurisdiction=jurisdiction,
            contract_type=contract_type
        )
        
        # Step 4: Analyze contract with context
        logger.info("Step 4: Analyzing contract with legal context")
        analysis = await claude_service.analyze_contract(
            contract_text=contract_text,
            legal_context=legal_context,
            description=description,
            contract_type=contract_type
        )
        
        return ContractAnalysisResponse(
            analysis=analysis,
            legal_context=legal_context,
            redlines=redlines
        )
        
    except Exception as e:
        logger.error(f"Error analyzing contract: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing contract: {str(e)}"
        )