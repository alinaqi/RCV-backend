import pytest
from unittest.mock import Mock, patch
from app.services.claude_service import ClaudeService
from app.schemas.contract import ContractAnalysis
from datetime import datetime

@pytest.fixture
def mock_anthropic():
    """Mock the Anthropic client."""
    with patch('anthropic.Anthropic') as mock:
        yield mock

@pytest.fixture
def sample_contract_text():
    """Sample contract text for testing."""
    return """
    [P1] Liability Clause
    [P2] The contractor shall be liable for all damages.
    [P3] Payment Terms
    [P4] Payment shall be made within 30 days.
    [P5] Notice Period
    [P6] A notice period of 30 days is required.
    """

@pytest.fixture
def sample_sections():
    """Sample extracted sections for testing."""
    return {
        "liability_clauses": "The contractor shall be liable for all damages.",
        "payment_terms": "Payment shall be made within 30 days.",
        "notice_periods": "A notice period of 30 days is required.",
        "termination_clauses": "",
        "governing_law": ""
    }

@pytest.fixture
def sample_claude_response():
    """Sample Claude API response."""
    return Mock(
        content=[
            Mock(
                text='''{
                    "issues": [
                        {
                            "type": "liability_clause",
                            "severity": "high",
                            "description": "Unlimited liability clause detected",
                            "location": {
                                "paragraph": 2,
                                "text": "The contractor shall be liable for all damages."
                            },
                            "suggestion": "Consider adding liability cap"
                        }
                    ],
                    "suggestions": [
                        {
                            "category": "payment_terms",
                            "description": "Payment terms could be more specific",
                            "current": "Payment shall be made within 30 days.",
                            "suggested": "Payment shall be made within 30 days of invoice receipt"
                        }
                    ],
                    "risk_score": 75
                }'''
            )
        ]
    )

def test_build_analysis_prompt():
    """Test building the analysis prompt."""
    service = ClaudeService()
    prompt = service._build_analysis_prompt("Sample contract", {"section": "content"})
    
    assert "Sample contract" in prompt
    assert "Identify and assess key clauses" in prompt
    assert "JSON format" in prompt

@pytest.mark.asyncio
async def test_analyze_contract_success(
    mock_anthropic,
    sample_contract_text,
    sample_sections,
    sample_claude_response
):
    """Test successful contract analysis."""
    # Setup mock
    mock_client = Mock()
    mock_client.messages.create.return_value = sample_claude_response
    mock_anthropic.return_value = mock_client
    
    # Test
    service = ClaudeService()
    result = await service.analyze_contract(sample_contract_text, sample_sections)
    
    # Verify
    assert isinstance(result, ContractAnalysis)
    assert len(result.issues) == 1
    assert result.issues[0].type == "liability_clause"
    assert result.issues[0].severity == "high"
    assert len(result.suggestions) == 1
    assert result.suggestions[0].category == "payment_terms"
    assert result.risk_score == 75
    assert isinstance(result.analysis_timestamp, datetime)

@pytest.mark.asyncio
async def test_analyze_contract_api_error(mock_anthropic, sample_contract_text, sample_sections):
    """Test handling of API errors."""
    # Setup mock to raise an exception
    mock_client = Mock()
    mock_client.messages.create.side_effect = Exception("API Error")
    mock_anthropic.return_value = mock_client
    
    # Test
    service = ClaudeService()
    with pytest.raises(Exception) as exc_info:
        await service.analyze_contract(sample_contract_text, sample_sections)
    
    assert str(exc_info.value) == "API Error" 