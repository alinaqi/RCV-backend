from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any
from datetime import datetime


class Location(BaseModel):
    paragraph: int
    text: str


class Issue(BaseModel):
    type: str
    severity: Literal["critical", "high", "medium", "low", "info"]
    description: str
    location: Location
    suggestion: str


class Suggestion(BaseModel):
    category: str
    description: str
    current: str
    suggested: str


class RedlineItem(BaseModel):
    paragraph_number: int
    original_text: str
    modified_text: str
    author: str
    date: str
    change_type: Literal["insertion", "deletion", "modification"]


class ContractAnalysis(BaseModel):
    issues: List[Issue]
    suggestions: List[Suggestion]
    risk_score: int = Field(ge=0, le=100)
    analysis_timestamp: datetime
    redlines: List[RedlineItem]


class ContractAnalysisResponse(BaseModel):
    status: Literal["success", "error"]
    analysis: Optional[ContractAnalysis] = None
    error: Optional[Dict[str, Any]] = None


class ContractAnalysisError(BaseModel):
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime