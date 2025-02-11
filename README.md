# Contract Validator API

An advanced FastAPI-based backend service that analyzes legal contracts using Claude AI to identify potential issues, risks, and suggest improvements. The service includes intelligent contract validation, section analysis, and redline tracking capabilities.

## Features

### Contract Analysis
- **AI-Powered Analysis**: Uses Claude AI for deep contract analysis
- **Risk Assessment**: Provides detailed risk scoring and analysis
- **Issue Detection**: Identifies potential legal and compliance issues
- **Smart Suggestions**: Offers context-aware improvement recommendations
- **Jurisdiction Awareness**: Considers local legal requirements when specified

### Redline Management
- **Dual Redline Tracking**:
  - Document Tracked Changes: Captures existing redlines in the document
  - AI-Suggested Changes: Highlights problematic sections with suggested improvements
- **Change Attribution**: Tracks authors and timestamps for all changes
- **Sorted Organization**: Presents changes in paragraph order for easy navigation

### Contract Validation
- **Intelligent Validation**: Uses AI to determine document legitimacy
- **Section Analysis**: Identifies and extracts key contract sections
- **Fallback Validation**: Includes basic validation as a backup

### Key Contract Sections Analyzed
- Liability Provisions
- Payment Terms
- Notice Periods
- Termination Conditions
- Jurisdiction and Governing Law

## Setup

### Prerequisites
- Python 3.11+
- Virtual Environment (recommended)
- Anthropic API Key (for Claude AI)

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

### API Endpoints

#### Contract Analysis
`POST /api/v1/analyze-contract`

Analyzes a contract document and provides comprehensive analysis with redlines.

**Request:**
- Content-Type: `multipart/form-data`
- Parameters:
  - `file`: DOCX file (required)
  - `description`: Brief description of contract purpose (required)
  - `contract_type`: Type of contract (optional)
  - `jurisdiction`: Country/region for legal context (optional)

**Response:**
```json
{
    "status": "success",
    "analysis": {
        "issues": [
            {
                "type": "string",
                "severity": "critical|high|medium|low|info",
                "description": "string",
                "location": {
                    "paragraph": number,
                    "text": "string"
                },
                "suggestion": "string"
            }
        ],
        "suggestions": [
            {
                "category": "string",
                "description": "string",
                "current": "string",
                "suggested": "string"
            }
        ],
        "risk_score": number,
        "analysis_timestamp": "datetime",
        "redlines": [
            {
                "paragraph_number": number,
                "original_text": "string",
                "modified_text": "string",
                "author": "string",
                "date": "string",
                "change_type": "insertion|deletion|modification"
            }
        ]
    }
}
```

### Error Handling

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
│   │   └── contract_parser.py
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