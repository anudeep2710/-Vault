"""
Document Analyzer Module - Secure local document processing.
Analyzes documents on-device with no cloud uploads.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import docx
import PyPDF2

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from database import PrivacyDatabase
from llm_handler import get_llm_handler
from config import DOCUMENT_CONFIG
from utils import safe_filename, validate_file_size


class DocumentAgent:
    """Privacy-first document analyzer with local NLP."""
    
    def __init__(self):
        """Initialize the document agent."""
        self.db = PrivacyDatabase()
        self.db.connect()
        self.llm = get_llm_handler()
        self.config = DOCUMENT_CONFIG
        
        # Try to load spaCy model for NER
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
            self.spacy_available = True
        except:
            print("⚠ spaCy model not found. Run: python -m spacy download en_core_web_sm")
            self.spacy_available = False
    
    def process_document(self, file_path: str, extract_summary: bool = True, 
                        extract_entities: bool = True) -> Dict[str, Any]:
        """
        Process a document file.
        
        Args:
            file_path: Path to document file
            extract_summary: Generate summary using LLM
            extract_entities: Extract named entities
            
        Returns:
            Processing results
        """
        file_path = Path(file_path)
        
        # Validate file
        if not file_path.exists():
            return {"error": "File not found"}
        
        if file_path.suffix.lower() not in self.config['supported_formats']:
            return {"error": f"Unsupported format. Supported: {', '.join(self.config['supported_formats'])}"}
        
        if not validate_file_size(file_path, self.config['max_file_size_mb']):
            return {"error": f"File too large. Max size: {self.config['max_file_size_mb']}MB"}
        
        # Extract text
        text = self._extract_text(file_path)
        if not text:
            return {"error": "Could not extract text from document"}
        
        # Generate summary
        summary = None
        if extract_summary and self.llm.available:
            summary = self.llm.summarize_document(text, max_length=self.config['summary_max_length'])
        
        # Extract entities
        entities = None
        if extract_entities and self.spacy_available:
            entities = self._extract_entities(text)
        
        # Store in database
        doc_id = self.db.add_document(
            filename=file_path.name,
            filepath=str(file_path.absolute()),
            content=text,
            file_type=file_path.suffix,
            summary=summary,
            entities=entities
        )
        
        return {
            "id": doc_id,
            "filename": file_path.name,
            "file_type": file_path.suffix,
            "text_length": len(text),
            "summary": summary,
            "entities": entities,
            "processed_at": datetime.now().isoformat()
        }
    
    def _extract_text(self, file_path: Path) -> Optional[str]:
        """Extract text from various document formats."""
        try:
            if file_path.suffix.lower() == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif file_path.suffix.lower() == '.pdf':
                text = []
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text.append(page_text)
                return '\n'.join(text)
            
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                doc = docx.Document(file_path)
                return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            
        except Exception as e:
            print(f"Error extracting text: {e}")
            return None
        
        return None
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities using spaCy."""
        if not self.spacy_available:
            return []
        
        # Limit text length for processing
        if len(text) > 100000:
            text = text[:100000]
        
        doc = self.nlp(text)
        
        # Extract entities of interest
        entities = []
        for ent in doc.ents:
            if ent.label_ in self.config['pii_entities']:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_
                })
        
        # Remove duplicates
        seen = set()
        unique_entities = []
        for ent in entities:
            key = (ent['text'], ent['label'])
            if key not in seen:
                seen.add(key)
                unique_entities.append(ent['text'])
        
        return unique_entities[:50]  # Limit to top 50
    
    def query_document(self, document_id: int, question: str) -> str:
        """
        Ask a question about a processed document.
        
        Args:
            document_id: ID of the document
            question: Question to ask
            
        Returns:
            Answer from LLM
        """
        # Get document from database
        documents = self.db.get_documents(limit=1000)
        document = next((d for d in documents if d['id'] == document_id), None)
        
        if not document:
            return "Document not found"
        
        # Use LLM to answer question
        if not self.llm.available:
            return "LLM not available for Q&A. Please install Ollama."
        
        return self.llm.answer_document_question(document['content'], question)
    
    def get_documents(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of processed documents."""
        return self.db.get_documents(limit=limit)
    
    def get_document_by_id(self, document_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID."""
        documents = self.db.get_documents(limit=1000)
        return next((d for d in documents if d['id'] == document_id), None)
    
    def search_documents(self, query: str) -> List[Dict[str, Any]]:
        """
        Search documents by content (simple text search).
        
        Args:
            query: Search query
            
        Returns:
            Matching documents
        """
        all_docs = self.db.get_documents(limit=500)
        query_lower = query.lower()
        
        matching = []
        for doc in all_docs:
            # Search in filename, summary, and content
            if (query_lower in doc['filename'].lower() or
                (doc.get('summary') and query_lower in doc['summary'].lower()) or
                query_lower in doc['content'].lower()):
                matching.append(doc)
        
        return matching
    
    def close(self):
        """Close database connection."""
        self.db.close()


if __name__ == "__main__":
    # Test document agent
    print("Testing Document Agent...")
    
    agent = DocumentAgent()
    
    # Create a test document
    test_doc_path = Path("test_document.txt")
    with open(test_doc_path, 'w') as f:
        f.write("""
        This is a confidential legal document.
        
        Party A: John Smith, residing at 123 Main Street, New York.
        Party B: Acme Corporation, located at 456 Business Ave.
        
        Agreement Date: December 1, 2024
        Contract Value: $50,000
        
        This agreement outlines the terms of service between the parties
        for the provision of consulting services over a period of 6 months.
        """)
    
    print(f"\n--- Processing Document ---")
    result = agent.process_document(str(test_doc_path))
    
    if 'error' not in result:
        print(f"✓ Processed: {result['filename']}")
        print(f"  Text length: {result['text_length']} chars")
        if result.get('summary'):
            print(f"  Summary: {result['summary'][:100]}...")
        if result.get('entities'):
            print(f"  Entities found: {len(result['entities'])}")
            print(f"  Sample entities: {', '.join(result['entities'][:5])}")
        
        # Test Q&A
        if agent.llm.available:
            print(f"\n--- Document Q&A ---")
            answer = agent.query_document(result['id'], "What is the contract value?")
            print(f"Q: What is the contract value?")
            print(f"A: {answer}")
    else:
        print(f"✗ Error: {result['error']}")
    
    # Cleanup
    test_doc_path.unlink()
    
    agent.close()
