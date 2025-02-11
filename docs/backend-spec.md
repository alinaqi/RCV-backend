# Backend Technical Specification - Contract Validator

## 1. System Overview

### 1.1 Core Components
- FastAPI server
- Anthropic Claude API integration
- DOCX parser
- File handling system
- Response formatter

### 1.2 Technology Stack
- Python 3.11+
- FastAPI 0.100+
- python-docx for DOCX parsing
- anthropic Python client
- pydantic for data validation
- python-multipart for file uploads

## 2. API Endpoints

### 2.1 Contract Analysis Endpoint
```python
POST /api/v1/analyze-contract
Content-Type: multipart/form-data

Parameters:
- file: DOCX file (required)
- jurisdiction: string (optional)
- contract_type: string (optional)

Response:
{
    "status": "success",
    "analysis": {
        "issues": [
            {
                "type": "liability_clause",
                "severity": "high",
                "description": "Unlimited liability clause detected",
                "location": {
                    "paragraph": 12,
                    "text": "The actual text from contract"
                },
                "suggestion": "Consider adding liability cap"
            }
        ],
        "suggestions": [
            {
                "category": "payment_terms",
                "description": "Payment terms could be more specific",
                "current": "The actual payment clause",
                "suggested": "Suggested improvement"
            }
        ],
        "risk_score": 75,
        "analysis_timestamp": "2024-02-11T12:00:00Z"
    }
}
```

## 3. Core Functionalities

### 3.1 Contract Parsing
```python
class ContractParser:
    def parse_docx(file: UploadFile) -> str:
        """
        Parse DOCX file into plain text while maintaining structure
        Returns formatted text suitable for LLM analysis
        """

    def extract_sections(text: str) -> Dict[str, str]:
        """
        Extract key contract sections:
        - Liability clauses
        - Payment terms
        - Notice periods
        - Termination clauses
        - Governing law
        """
```

### 3.2 Analysis Types
1. Liability Analysis
   - Unlimited liability clauses
   - Indemnification provisions
   - Insurance requirements
   - Liability caps

2. Payment Terms Analysis
   - Payment schedules
   - Late payment penalties
   - Currency specifications
   - Payment conditions

3. Notice Period Analysis
   - Termination notice
   - Breach notification
   - Change request notices
   - Communication requirements

### 3.3 Severity Levels
- Critical: Immediate attention required, high risk
- High: Significant issues that need addressing
- Medium: Important but not urgent issues
- Low: Minor suggestions for improvement
- Info: Informational findings

## 4. Claude Integration

### 4.1 Prompt Engineering
```python
class PromptBuilder:
    def build_analysis_prompt(
        contract_text: str,
        sections: Dict[str, str],
        context: Dict[str, Any]
    ) -> str:
        """
        Create structured prompt for Claude including:
        1. Analysis instructions
        2. Contract text
        3. Specific areas to focus on
        4. Required output format
        5. Context-specific considerations
        """
```

### 4.2 Example Prompt Template
```text
You are a legal contract analyzer. Analyze the following contract with these instructions:

1. Identify and assess key clauses:
   - Liability provisions
   - Payment terms
   - Notice periods
   - Termination conditions

2. For each identified issue:
   - Specify the type of issue
   - Assess severity (Critical/High/Medium/Low/Info)
   - Provide specific location in the text
   - Explain the potential risk
   - Suggest improvements

Contract text:
{contract_text}

Provide analysis in the following JSON format:
{output_format_specification}
```

## 5. Response Processing

### 5.1 Response Structure
```python
class ContractAnalysis(BaseModel):
    issues: List[Issue]
    suggestions: List[Suggestion]
    risk_score: int
    analysis_timestamp: datetime

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

class Location(BaseModel):
    paragraph: int
    text: str
```

### 5.2 Error Handling
```python
class ContractAnalysisError(BaseModel):
    error_code: str
    message: str
    details: Optional[Dict[str, Any]]
    timestamp: datetime
```

## 6. File Handling

### 6.1 Upload Constraints
- Maximum file size: 10MB
- Allowed file types: DOCX only
- File validation before processing

### 6.2 File Processing
```python
async def process_contract_file(file: UploadFile) -> str:
    """
    1. Validate file type and size
    2. Scan for malware (future implementation)
    3. Parse DOCX to text
    4. Clean and format text
    5. Return processed text
    """
```

## 7. Error Scenarios

### 7.1 HTTP Error Codes
- 400: Bad Request (Invalid file format, size)
- 422: Validation Error (Invalid input data)
- 429: Too Many Requests (Rate limit exceeded)
- 500: Internal Server Error
- 503: Service Unavailable (Claude API unavailable)

### 7.2 Error Responses
```json
{
    "status": "error",
    "error": {
        "code": "INVALID_FILE_FORMAT",
        "message": "Only DOCX files are supported",
        "details": {
            "provided_format": "pdf",
            "allowed_formats": ["docx"]
        },
        "timestamp": "2024-02-11T12:00:00Z"
    }
}
```

## 8. Performance Considerations

### 8.1 Timeouts
- File upload timeout: 30 seconds
- Analysis timeout: 60 seconds
- Overall request timeout: 90 seconds

### 8.2 Rate Limiting
- Max 10 requests per minute per IP
- Max 5 concurrent analyses
- Max file size: 10MB

## 9. Testing Requirements

### 9.1 Test Cases
- File upload validation
- Contract parsing accuracy
- Analysis response format
- Error handling scenarios
- Timeout handling
- Rate limit enforcement

### 9.2 Test Data
- Sample contracts for each analysis type
- Invalid file formats
- Large files
- Malformed DOCX files
- Various contract structures