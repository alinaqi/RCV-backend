from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Optional
import logging
from datetime import datetime

from src.app.services.contract_parser import ContractParser, ParsedDocument
from src.app.services.claude_service import ClaudeService
from src.app.schemas.contract import ContractAnalysisResponse, ContractAnalysisError, RedlineItem
from src.app.core.config import settings

logger = logging.getLogger(__name__)

api_router = APIRouter()

@api_router.post("/analyze-contract", response_model=ContractAnalysisResponse)
async def analyze_contract(
    description: str,
    file: UploadFile = File(...),
    contract_type: Optional[str] = None,
    jurisdiction: Optional[str] = None,
):
    """
    Analyze a contract document using Claude AI.
    
    Args:
        description: Brief description of the contract's purpose and context
        file: DOCX file containing the contract
        contract_type: Type of contract (e.g., service, employment, NDA, etc.)
        jurisdiction: Country or region where the contract will be enforced
        
    Returns:
        ContractAnalysisResponse: Analysis results or error details
    """
    try:
        # Validate file type
        if not file.filename.endswith('.docx'):
            raise HTTPException(
                status_code=400,
                detail="Only DOCX files are supported"
            )
            
        # Validate file size
        file_size = 0
        content = await file.read()
        file_size = len(content)
        await file.seek(0)
        
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Parse contract
        contract_parser = ContractParser()
        parsed_doc: ParsedDocument = await contract_parser.parse_docx(file)
        sections = contract_parser.extract_sections(parsed_doc.text)
        
        # Get tracked changes from document
        doc_redlines = [
            RedlineItem(
                paragraph_number=r.paragraph_number,
                original_text=r.original_text,
                modified_text=r.modified_text,
                author=r.author,
                date=r.date,
                change_type=r.change_type
            ) for r in parsed_doc.redlines
        ]
        
        # Validate if it's a legitimate contract
        if not await contract_parser.is_valid_contract(parsed_doc.text):
            return ContractAnalysisResponse(
                status="error",
                error={
                    "error_code": "INVALID_CONTRACT",
                    "message": "The provided document does not appear to be a valid contract",
                    "details": {
                        "reason": "Missing essential contract elements or structure",
                        "suggestion": "Please ensure the document is a proper legal contract",
                        "redlines": [r.model_dump() for r in doc_redlines]
                    },
                    "timestamp": datetime.utcnow()
                }
            )
        
        # Analyze with Claude
        claude_service = ClaudeService()
        analysis = await claude_service.analyze_contract(
            contract_text=parsed_doc.text,
            sections=sections,
            description=description,
            contract_type=contract_type,
            jurisdiction=jurisdiction
        )
        
        # Convert Claude's issues into redlines
        issue_redlines = []
        for issue in analysis.issues:
            # Create a redline for each identified issue
            issue_redlines.append(
                RedlineItem(
                    paragraph_number=issue.location.paragraph,
                    original_text=issue.location.text,
                    modified_text=issue.suggestion,
                    author="Claude AI",
                    date=datetime.utcnow().isoformat(),
                    change_type="modification"
                )
            )
            
        # Combine document tracked changes and AI-suggested changes
        all_redlines = doc_redlines + issue_redlines
        
        # Sort redlines by paragraph number for better organization
        all_redlines.sort(key=lambda x: x.paragraph_number)
        
        # Update analysis with combined redlines
        analysis.redlines = all_redlines
        
        return ContractAnalysisResponse(
            status="success",
            analysis=analysis
        )
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Error processing contract: {str(e)}", exc_info=True)
        error = ContractAnalysisError(
            error_code="PROCESSING_ERROR",
            message="Failed to process contract",
            details={"error": str(e)},
            timestamp=datetime.utcnow()
        )
        return ContractAnalysisResponse(
            status="error",
            error=error.model_dump()
        )