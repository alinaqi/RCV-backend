from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any
from datetime import datetime

from src.app.schemas.legal_context import ContractLegalContext


class Location(BaseModel):
    """Location of an issue in the contract."""
    paragraph: int
    text: str


class Issue(BaseModel):
    """Contract issue with location and suggestion."""
    location: Location
    description: str
    severity: str  # 'high', 'medium', 'low'
    suggestion: str


class Suggestion(BaseModel):
    category: str
    description: str
    current: str
    suggested: str


class RedlineItem(BaseModel):
    """A single redline/tracked change in the contract."""
    paragraph_number: int
    original_text: str
    modified_text: str
    author: str
    date: str
    change_type: str  # 'insertion', 'deletion', 'modification'


class LegalReference(BaseModel):
    title: str
    description: str
    relevance: str
    source: str
    reference_type: Literal["law", "case"]


class ContractAnalysis(BaseModel):
    """Results of contract analysis."""
    issues: List[Issue]
    suggestions: List[str]
    risk_assessment: str
    legal_context: ContractLegalContext


class ContractAnalysisResponse(BaseModel):
    """API response for contract analysis."""
    analysis: ContractAnalysis
    legal_context: ContractLegalContext
    redlines: List[RedlineItem]


class ContractAnalysisError(BaseModel):
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime