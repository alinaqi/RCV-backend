from pydantic import BaseModel
from typing import List, Literal


class LegalReference(BaseModel):
    """A legal reference (law or case)."""
    title: str
    description: str
    relevance: str
    source: str
    reference_type: Literal["law", "case"]


class ContractLegalContext(BaseModel):
    """The legal context of a contract."""
    topic: str
    jurisdiction: str
    summary: str
    laws: List[LegalReference]
    cases: List[LegalReference] 