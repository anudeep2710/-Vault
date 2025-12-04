"""
RunAnywhere SDK Integration for Vault
Replaces Ollama with RunAnywhere AI for on-device inference
"""
import requests
from typing import Optional, Dict, Any, List
import json

# RunAnywhere SDK configuration
RUNANYWHERE_API_URL = "http://localhost:8000"  # Local RunAnywhere server


class RunAnywhereHandler:
    """
    Handler for RunAnywhere SDK integration.
    Provides on-device AI with sub-80ms latency.
    """
    
    def __init__(self, api_url: str = RUNANYWHERE_API_URL):
        """
        Initialize RunAnywhere handler.
        
        Args:
            api_url: RunAnywhere API endpoint (localhost)
        """
        self.api_url = api_url
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if RunAnywhere SDK is running."""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=2)
            if response.status_code == 200:
                print("[OK] RunAnywhere SDK is running")
                return True
            return False
        except requests.exceptions.RequestException:
            print("[WARNING] RunAnywhere SDK not available")
            print("Falling back to Ollama or rule-based processing")
            return False
    
    def structured_output(self, prompt: str, schema: Dict[str, Any]) -> Optional[Dict]:
        """
        Generate structured output using RunAnywhere SDK.
        Perfect for SMS parsing and entity extraction.
        
        Args:
            prompt: Input text
            schema: JSON schema for output structure
            
        Returns:
            Structured JSON output
        """
        if not self.available:
            return None
        
        try:
            payload = {
                "prompt": prompt,
                "schema": schema,
                "max_tokens": 500
            }
            
            response = requests.post(
                f"{self.api_url}/structured",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            print(f"RunAnywhere error: {e}")
            return None
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment with structured output.
        
        Returns:
            {
                "sentiment": "positive/negative/neutral",
                "score": float,
                "mood": "very_positive/positive/neutral/negative/very_negative",
                "emotions": ["happy", "excited"],
                "confidence": float
            }
        """
        schema = {
            "type": "object",
            "properties": {
                "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
                "score": {"type": "number", "minimum": -1, "maximum": 1},
                "mood": {"type": "string", "enum": ["very_positive", "positive", "neutral", "negative", "very_negative"]},
                "emotions": {"type": "array", "items": {"type": "string"}},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1}
            },
            "required": ["sentiment", "score", "mood"]
        }
        
        prompt = f"""Analyze the sentiment and mood of this journal entry:

"{text}"

Provide sentiment analysis with emotions detected."""
        
        return self.structured_output(prompt, schema)
    
    def parse_sms_transaction(self, sms_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse bank SMS using structured output.
        
        Returns:
            {
                "amount": float,
                "type": "debit/credit",
                "merchant": str,
                "date": str,
                "account": str,
                "category": str
            }
        """
        schema = {
            "type": "object",
            "properties": {
                "amount": {"type": "number"},
                "type": {"type": "string", "enum": ["debit", "credit"]},
                "merchant": {"type": "string"},
                "date": {"type": "string"},
                "account": {"type": "string"},
                "category": {"type": "string", "enum": [
                    "Food & Dining", "Transportation", "Shopping", 
                    "Entertainment", "Bills & Utilities", "Healthcare",
                    "Education", "Income", "Transfer", "Other"
                ]}
            },
            "required": ["amount", "type"]
        }
        
        prompt = f"""Parse this bank SMS transaction:

"{sms_text}"

Extract amount, transaction type, merchant, date, account number, and categorize the spending."""
        
        return self.structured_output(prompt, schema)
    
    def extract_document_entities(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract entities from document using structured output.
        
        Returns:
            {
                "people": ["John Smith"],
                "organizations": ["Acme Corp"],
                "dates": ["December 1, 2024"],
                "amounts": ["$50,000"],
                "locations": ["New York"],
                "key_terms": ["contract", "agreement"]
            }
        """
        schema = {
            "type": "object",
            "properties": {
                "people": {"type": "array", "items": {"type": "string"}},
                "organizations": {"type": "array", "items": {"type": "string"}},
                "dates": {"type": "array", "items": {"type": "string"}},
                "amounts": {"type": "array", "items": {"type": "string"}},
                "locations": {"type": "array", "items": {"type": "string"}},
                "key_terms": {"type": "array", "items": {"type": "string"}}
            }
        }
        
        prompt = f"""Extract all entities from this document:

"{text[:2000]}"  # Limit for performance

Identify people, organizations, dates, monetary amounts, locations, and key legal/business terms."""
        
        return self.structured_output(prompt, schema)
    
    def summarize(self, text: str, max_length: int = 200) -> Optional[str]:
        """Generate summary of text."""
        if not self.available:
            return None
        
        try:
            payload = {
                "prompt": f"Summarize this in {max_length} words:\n\n{text}",
                "max_tokens": max_length * 2
            }
            
            response = requests.post(
                f"{self.api_url}/generate",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get("text", "")
            return None
            
        except Exception as e:
            print(f"Summarization error: {e}")
            return None
    
    def voice_to_text(self, audio_data: bytes) -> Optional[str]:
        """
        Convert voice to text using RunAnywhere Voice Pipeline.
        
        Args:
            audio_data: Audio bytes
            
        Returns:
            Transcribed text
        """
        if not self.available:
            return None
        
        try:
            files = {"audio": audio_data}
            response = requests.post(
                f"{self.api_url}/voice/transcribe",
                files=files,
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json().get("text", "")
            return None
            
        except Exception as e:
            print(f"Voice transcription error: {e}")
            return None
    
    def get_latency_stats(self) -> Dict[str, float]:
        """Get performance statistics."""
        if not self.available:
            return {"available": False}
        
        try:
            response = requests.get(f"{self.api_url}/stats")
            if response.status_code == 200:
                return response.json()
            return {}
        except:
            return {}


# Global instance
_runanywhere_handler: Optional[RunAnywhereHandler] = None


def get_runanywhere_handler() -> RunAnywhereHandler:
    """Get or create RunAnywhere handler instance."""
    global _runanywhere_handler
    if _runanywhere_handler is None:
        _runanywhere_handler = RunAnywhereHandler()
    return _runanywhere_handler


if __name__ == "__main__":
    # Test RunAnywhere SDK
    print("Testing RunAnywhere SDK Integration...")
    
    handler = RunAnywhereHandler()
    
    if handler.available:
        print("\n✓ RunAnywhere SDK is available!")
        
        # Test sentiment analysis
        result = handler.analyze_sentiment("I'm feeling great today!")
        print(f"\nSentiment: {result}")
        
        # Test SMS parsing
        sms = "Debited Rs.500 from A/C XX1234 at COFFEE SHOP on 04-12-24"
        result = handler.parse_sms_transaction(sms)
        print(f"\nParsed SMS: {result}")
        
        # Get stats
        stats = handler.get_latency_stats()
        print(f"\nLatency: {stats.get('avg_latency_ms', 'N/A')}ms")
    else:
        print("\n⚠ RunAnywhere SDK not running")
        print("Start the RunAnywhere server first")
