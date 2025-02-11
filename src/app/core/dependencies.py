from typing import Tuple
from fastapi import Depends

from src.app.services.claude_service import ClaudeService
from src.app.services.perplexity_service import PerplexityService
from src.app.services.docx_service import DocxService

def get_claude_service() -> ClaudeService:
    """Get Claude service instance."""
    return ClaudeService()

def get_perplexity_service() -> PerplexityService:
    """Get Perplexity service instance."""
    return PerplexityService()

def get_docx_service() -> DocxService:
    """Get DOCX service instance."""
    return DocxService()

def get_services(
    claude_service: ClaudeService = Depends(get_claude_service),
    perplexity_service: PerplexityService = Depends(get_perplexity_service),
    docx_service: DocxService = Depends(get_docx_service)
) -> Tuple[ClaudeService, PerplexityService, DocxService]:
    """Get all required services."""
    return claude_service, perplexity_service, docx_service 