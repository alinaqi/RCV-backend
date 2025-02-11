from typing import List, Tuple
from fastapi import UploadFile, HTTPException
import docx
from io import BytesIO
import logging
from datetime import datetime

from src.app.core.config import settings
from src.app.schemas.contract import RedlineItem

logger = logging.getLogger(__name__)

class DocxService:
    """Service for handling DOCX file operations."""
    
    async def parse_contract(self, file: UploadFile) -> Tuple[str, List[RedlineItem]]:
        """
        Parse and validate a DOCX contract file.
        
        Args:
            file (UploadFile): The uploaded DOCX file
            
        Returns:
            Tuple[str, List[RedlineItem]]: Tuple of (contract_text, redlines)
            
        Raises:
            HTTPException: If file is invalid or parsing fails
        """
        try:
            # Validate file type
            if not file.filename.endswith('.docx'):
                raise HTTPException(
                    status_code=400,
                    detail="Only DOCX files are supported"
                )
            
            # Read and validate file size
            content = await file.read()
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE // (1024*1024)}MB"
                )
            
            # Parse DOCX
            doc = docx.Document(BytesIO(content))
            
            # Extract text with paragraph numbers
            text_blocks = []
            redlines = []
            
            for i, paragraph in enumerate(doc.paragraphs, 1):
                if paragraph.text.strip():
                    text_blocks.append(f"[P{i}] {paragraph.text}")
                    
                    # Extract redlines from paragraph
                    redlines.extend(self._extract_redlines(paragraph, i))
            
            return "\n\n".join(text_blocks), redlines
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error parsing DOCX file: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=400,
                detail="Failed to parse DOCX file. Please ensure it's a valid DOCX document."
            )
    
    def _extract_redlines(self, paragraph: docx.text.paragraph.Paragraph, paragraph_number: int) -> List[RedlineItem]:
        """
        Extract redlines (tracked changes) from a paragraph.
        
        Args:
            paragraph (Paragraph): The paragraph to analyze
            paragraph_number (int): The number of the paragraph
            
        Returns:
            List[RedlineItem]: List of redlines found in the paragraph
        """
        redlines = []
        
        if not hasattr(paragraph._element, 'xpath'):
            return redlines
            
        try:
            # Define namespace map for XML parsing
            nsmap = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            # Find deletions
            dels = paragraph._element.findall('.//w:del', nsmap)
            for deletion in dels:
                author = deletion.get(f'{{{nsmap["w"]}}}author', 'Unknown')
                date = deletion.get(f'{{{nsmap["w"]}}}date', datetime.utcnow().isoformat())
                text = deletion.text if deletion.text else ""
                
                if text:
                    redlines.append(RedlineItem(
                        paragraph_number=paragraph_number,
                        original_text=text,
                        modified_text="",
                        author=author,
                        date=date,
                        change_type='deletion'
                    ))
            
            # Find insertions
            ins = paragraph._element.findall('.//w:ins', nsmap)
            for insertion in ins:
                author = insertion.get(f'{{{nsmap["w"]}}}author', 'Unknown')
                date = insertion.get(f'{{{nsmap["w"]}}}date', datetime.utcnow().isoformat())
                text = insertion.text if insertion.text else ""
                
                if text:
                    redlines.append(RedlineItem(
                        paragraph_number=paragraph_number,
                        original_text="",
                        modified_text=text,
                        author=author,
                        date=date,
                        change_type='insertion'
                    ))
            
            # Find moves (treated as modifications)
            moves = paragraph._element.findall('.//w:moveFrom', nsmap) + \
                   paragraph._element.findall('.//w:moveTo', nsmap)
            
            for move in moves:
                author = move.get(f'{{{nsmap["w"]}}}author', 'Unknown')
                date = move.get(f'{{{nsmap["w"]}}}date', datetime.utcnow().isoformat())
                text = move.text if move.text else ""
                
                if text:
                    change_type = 'deletion' if move.tag.endswith('moveFrom') else 'insertion'
                    redlines.append(RedlineItem(
                        paragraph_number=paragraph_number,
                        original_text=text if change_type == 'deletion' else "",
                        modified_text=text if change_type == 'insertion' else "",
                        author=author,
                        date=date,
                        change_type=change_type
                    ))
                    
        except Exception as e:
            logger.error(f"Error extracting redlines from paragraph {paragraph_number}: {str(e)}", exc_info=True)
            
        return redlines 