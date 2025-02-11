# Contract Validator API

An advanced FastAPI-based backend service that analyzes legal contracts using AI to identify potential issues, risks, and suggest improvements. The service combines Claude AI and Perplexity AI for comprehensive contract analysis and legal research.

## Features

### Multi-Stage Contract Analysis
1. **Document Processing**
   - DOCX file parsing and validation
   - Extraction of contract text and structure
   - Tracking of document redlines and changes
   - Support for tracked changes and modifications

2. **Legal Context Analysis (Perplexity AI)**
   - Automatic topic and jurisdiction detection
   - Identification of relevant laws and regulations
   - Finding applicable case law and precedents
   - Legal context summarization
   - Real-time legal research capabilities

3. **Contract Analysis (Claude AI)**
   - Deep semantic analysis of contract terms
   - Issue identification and risk assessment
   - Compliance verification with relevant laws
   - Improvement suggestions
   - Risk scoring and evaluation

4. **Comprehensive Reporting**
   - Detailed issue descriptions with locations
   - Severity-based categorization
   - Specific improvement suggestions
   - Overall risk assessment
   - Legal context integration

### Analysis Components

#### Legal Context Analysis
- **Topic Detection**: Automatically identifies contract type and subject matter
- **Jurisdiction Analysis**: Determines applicable legal framework
- **Legal Research**: 
  - Relevant laws and regulations
  - Applicable case law
  - Legal precedents
  - Regulatory requirements

#### Contract Analysis
- **Issue Detection**:
  - Legal compliance issues
  - Risk factors
  - Ambiguous terms
  - Missing clauses
  - Potential conflicts
- **Risk Assessment**:
  - Severity classification
  - Impact analysis
  - Compliance evaluation
  - Risk scoring

#### Improvement Suggestions
- Clause-specific recommendations
- Alternative wording proposals
- Best practice alignments
- Compliance improvements
- Risk mitigation strategies

### Redline Management
- **Document Tracked Changes**:
  - Captures existing redlines
  - Author attribution
  - Timestamp tracking
  - Change type classification
- **AI-Suggested Changes**:
  - Improvement markers
  - Risk highlights
  - Compliance suggestions

## API Endpoints

### Contract Analysis
`POST /api/v1/analyze-contract`

Analyzes a contract document through the multi-stage process.

**Request:**
```http
POST /api/v1/analyze-contract
Content-Type: multipart/form-data

Parameters:
- file: DOCX file (required)
- description: Brief description of contract purpose (required)
- contract_type: Type of contract (optional)
- jurisdiction: Country/region for legal context (optional)
```

**Response:**
```json
{
    "status": "success",
    "analysis": {
        "issues": [
            {
                "location": {
                    "paragraph": 1,
                    "text": "string"
                },
                "description": "string",
                "severity": "high|medium|low",
                "suggestion": "string"
            }
        ],
        "suggestions": [
            "string"
        ],
        "risk_assessment": "string",
        "legal_context": {
            "topic": "string",
            "jurisdiction": "string",
            "summary": "string",
            "laws": [
                {
                    "title": "string",
                    "description": "string",
                    "relevance": "string",
                    "source": "string"
                }
            ],
            "cases": [
                {
                    "title": "string",
                    "description": "string",
                    "relevance": "string",
                    "source": "string"
                }
            ]
        }
    }
}
```

## Setup

### Prerequisites
- Python 3.11+
- Virtual Environment (recommended)
- Anthropic API Key (for Claude AI)
- Perplexity API Key (for legal research)

### Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```env
ANTHROPIC_API_KEY=your_api_key_here
PERPLEXITY_API_KEY=your_perplexity_api_key_here
DEBUG=True
MAX_FILE_SIZE=10485760
RATE_LIMIT_PER_MINUTE=10
MAX_CONCURRENT_ANALYSES=5
UPLOAD_TIMEOUT=30
ANALYSIS_TIMEOUT=60
REQUEST_TIMEOUT=90
```

## Usage

### Starting the Server
```bash
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8010
```

### Example Usage with cURL
```bash
curl -X POST "http://localhost:8010/api/v1/analyze-contract" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@contract.docx" \
  -F "description=Employment contract for senior software developer" \
  -F "contract_type=employment" \
  -F "jurisdiction=Germany"
```

## Error Handling

The API uses standard HTTP status codes and returns detailed error messages:

- 400: Bad Request (Invalid file format, size)
- 422: Validation Error (Invalid input data)
- 429: Too Many Requests (Rate limit exceeded)
- 500: Internal Server Error

### Rate Limiting
- Maximum 10 requests per minute per IP
- Maximum file size: 10MB
- Only DOCX files are supported

## Development

### Project Structure
```
src/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── router.py
│   ├── core/
│   │   └── config.py
│   ├── schemas/
│   │   └── contract.py
│   ├── services/
│   │   ├── claude_service.py
│   │   ├── perplexity_service.py
│   │   └── docx_service.py
│   └── main.py
├── tests/
│   ├── integration/
│   └── unit/
└── requirements.txt
```

### Running Tests
```bash
pytest
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Security

- API keys are managed through environment variables
- Rate limiting prevents abuse
- File size restrictions prevent DOS attacks
- Input validation on all endpoints
- Error handling prevents information leakage

## License

No Support or license as this is just a midnight hackathon!:)