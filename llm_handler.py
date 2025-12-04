"""
LLM Handler - Supports both Ollama and RunAnywhere SDK
Automatically uses RunAnywhere if available, falls back to Ollama
"""
import requests
from typing import Optional, Dict, Any
import json

from config import OLLAMA_BASE_URL, DEFAULT_MODEL

# Try to use RunAnywhere handler, fallback to Ollama
try:
    from runanywhere_handler import RunAnywhereHandler
    RUNANYWHERE_AVAILABLE = True
except ImportError:
    RUNANYWHERE_AVAILABLE = False


class LocalLLMHandler:
    """Unified LLM handler supporting multiple backends."""
    
    def __init__(self):
        """Initialize LLM handler with best available backend."""
        self.runanywhere = None
        self.ollama_url = OLLAMA_BASE_URL
        self.model = DEFAULT_MODEL
        
        # Try RunAnywhere first
        if RUNANYWHERE_AVAILABLE:
            try:
                self.runanywhere = RunAnywhereHandler()
                if self.runanywhere.available:
                    print("[OK] Using RunAnywhere SDK for AI")
                    self.available = True
                    self.backend = "runanywhere"
                    return
            except:
                pass
        
        # Fallback to Ollama
        self.available = self._check_ollama()
        self.backend = "ollama" if self.available else "none"
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = [m['name'] for m in response.json().get('models', [])]
                if any(self.model in name for name in models):
                    print(f"[OK] Using Ollama with model: {self.model}")
                    return True
        except:
            pass
        print("[WARNING] No LLM available - using rule-based processing")
        return False
    
    def analyze_journal_mood(self, text: str) -> Dict[str, Any]:
        """Analyze journal mood using best available method."""
        if self.backend == "runanywhere":
            result = self.runanywhere.analyze_sentiment(text)
            if result and '_latency_ms' in result:
                result['_backend'] = 'runanywhere'
                return result
        
        # Ollama fallback
        if self.backend == "ollama":
            prompt = f"""Analyze mood from this journal entry and respond with JSON:
{{
  "mood": "positive/negative/neutral",
  "mood_category": "very_positive/positive/neutral/negative/very_negative",
  "score": -1.0 to 1.0,
  "emotions": ["emotion1", "emotion2"],
  "insight": "supportive message"
}}

Entry: {text}"""
            
            result = self._generate_ollama(prompt)
            if result:
                try:
                    json_start = result.find('{')
                    json_end = result.rfind('}') + 1
                    if json_start >= 0:
                        data = json.loads(result[json_start:json_end])
                        data['_backend'] = 'ollama'
                        return data
                except:
                    pass
        
        return {"error": "LLM not available", "mood_category": "neutral"}
    
    def categorize_transaction(self, description: str, merchant: str = "") -> str:
        """Categorize transaction."""
        if self.backend == "runanywhere":
            result = self.runanywhere.parse_sms_transaction(
                f"Transaction: {description} at {merchant}"
            )
            if result and 'category' in result:
                return result['category']
        
        if self.backend == "ollama":
            categories = ["Food & Dining", "Transportation", "Shopping", 
                         "Entertainment", "Bills & Utilities", "Healthcare",
                         "Education", "Income", "Transfer", "Other"]
            
            prompt = f"""Categorize: {description} at {merchant}
Categories: {', '.join(categories)}
Respond with ONLY the category name."""
            
            result = self._generate_ollama(prompt, max_tokens=20)
            for cat in categories:
                if cat.lower() in (result or '').lower():
                    return cat
        
        return "Other"
    
    def summarize_document(self, text: str, max_length: int = 200) -> str:
        """Summarize document."""
        if len(text) > 4000:
            text = text[:4000]
        
        if self.backend == "runanywhere":
            result = self.runanywhere.summarize(text, max_length)
            if result:
                return result
        
        if self.backend == "ollama":
            prompt = f"Summarize in {max_length} words:\n\n{text}"
            result = self._generate_ollama(prompt)
            return result or "Summary unavailable"
        
        return "Summary unavailable"
    
    def answer_document_question(self, text: str, question: str) -> str:
        """Answer question about document."""
        if self.backend == "ollama":
            prompt = f"Document:\n{text}\n\nQuestion: {question}\n\nAnswer:"
            return self._generate_ollama(prompt) or "Cannot answer"
        
        return "Q&A unavailable"
    
    def _generate_ollama(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        """Generate using Ollama."""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": self.model, "prompt": prompt, 
                      "stream": False, "options": {"num_predict": max_tokens}},
                timeout=30
            )
            if response.status_code == 200:
                return response.json().get('response', '').strip()
        except:
            pass
        return None


_llm_handler = None

def get_llm_handler():
    global _llm_handler
    if _llm_handler is None:
        _llm_handler = LocalLLMHandler()
    return _llm_handler
