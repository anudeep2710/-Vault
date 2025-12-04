"""
Local LLM handler using Ollama for privacy-first on-device inference.
Falls back to rule-based processing if LLM is unavailable.
"""
import requests
from typing import Optional, Dict, Any, List
import json

from config import OLLAMA_BASE_URL, DEFAULT_MODEL, NLP_CONFIG


class LocalLLMHandler:
    """Handles all LLM inference using local Ollama instance."""
    
    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = DEFAULT_MODEL):
        """
        Initialize the LLM handler.
        
        Args:
            base_url: Ollama API base URL (localhost only)
            model: Model name to use
        """
        self.base_url = base_url
        self.model = model
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                
                # Check if our model is available
                if any(self.model in name for name in model_names):
                    print(f"[OK] Ollama is running with model: {self.model}")
                    return True
                else:
                    print(f"[WARNING] Ollama is running but model '{self.model}' not found")
                    print(f"Available models: {', '.join(model_names)}")
                    print("Run: ollama pull llama3.2:3b")
                    return False
            return False
        except requests.exceptions.RequestException:
            print(f"[WARNING] Ollama not available at {self.base_url}")
            print("Install: https://ollama.ai")
            return False
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, 
                max_tokens: int = 500, temperature: float = 0.7) -> Optional[str]:
        """
        Generate text using the local LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System/role prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text or None if unavailable
        """
        if not self.available:
            return None
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                print(f"LLM error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"LLM inference error: {e}")
            return None
    
    def chat(self, messages: List[Dict[str, str]], max_tokens: int = 500) -> Optional[str]:
        """
        Chat-style inference with conversation history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response or None
        """
        if not self.available:
            return None
        
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('message', {}).get('content', '').strip()
            else:
                return None
                
        except Exception as e:
            print(f"Chat error: {e}")
            return None
    
    # ========== Domain-Specific Prompts ==========
    
    def analyze_journal_mood(self, journal_text: str) -> Dict[str, Any]:
        """Analyze mood and themes from journal entry."""
        if not self.available:
            return {"error": "LLM not available"}
        
        system_prompt = """You are a compassionate mental health assistant. Analyze journal entries 
        for mood, emotional themes, and patterns. Be supportive and non-judgmental. 
        Respond in JSON format only."""
        
        prompt = f"""Analyze this journal entry and provide:
1. Overall mood (very_negative, negative, neutral, positive, very_positive)
2. Key emotional themes (list of 3-5 emotions)
3. A brief supportive insight (1-2 sentences)

Journal entry:
{journal_text}

Respond in this JSON format:
{{
    "mood": "...",
    "themes": ["...", "..."],
    "insight": "..."
}}"""
        
        response = self.generate(prompt, system_prompt=system_prompt)
        
        if response:
            try:
                # Extract JSON from response
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    return json.loads(response[json_start:json_end])
            except json.JSONDecodeError:
                pass
        
        return {"error": "Could not parse LLM response"}
    
    def categorize_transaction(self, description: str, merchant: str = None) -> str:
        """Categorize a financial transaction."""
        if not self.available:
            return "Other"
        
        categories = ["Food & Dining", "Transportation", "Shopping", "Entertainment",
                     "Bills & Utilities", "Healthcare", "Education", "Income", "Transfer", "Other"]
        
        prompt = f"""Categorize this transaction into exactly ONE of these categories:
{', '.join(categories)}

Transaction: {description}
Merchant: {merchant or 'Unknown'}

Respond with ONLY the category name, nothing else."""
        
        response = self.generate(prompt, max_tokens=20, temperature=0.3)
        
        # Validate response
        if response and response in categories:
            return response
        
        # Fallback: try to find category in response
        for cat in categories:
            if cat.lower() in (response or '').lower():
                return cat
        
        return "Other"
    
    def summarize_document(self, document_text: str, max_length: int = 200) -> str:
        """Generate a summary of a document."""
        if not self.available:
            return "Summary unavailable (LLM not running)"
        
        # Truncate very long documents
        if len(document_text) > 10000:
            document_text = document_text[:10000] + "..."
        
        prompt = f"""Summarize the following document in {max_length} words or less. 
Be concise and focus on key points.

Document:
{document_text}

Summary:"""
        
        response = self.generate(prompt, max_tokens=max_length * 2)
        return response or "Could not generate summary"
    
    def answer_document_question(self, document_text: str, question: str) -> str:
        """Answer a question about a document."""
        if not self.available:
            return "LLM not available for Q&A"
        
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that answers questions about documents accurately and concisely. Only use information from the provided document."
            },
            {
                "role": "user",
                "content": f"Document:\n{document_text}\n\nQuestion: {question}"
            }
        ]
        
        response = self.chat(messages)
        return response or "Could not answer question"
    
    def generate_insight(self, data_summary: str, context: str) -> str:
        """Generate insights from data patterns."""
        if not self.available:
            return None
        
        prompt = f"""Based on this data, provide one actionable insight.

Context: {context}
Data: {data_summary}

Provide a brief, actionable insight (1-2 sentences):"""
        
        return self.generate(prompt, max_tokens=100)


# Global LLM handler instance
_llm_handler: Optional[LocalLLMHandler] = None


def get_llm_handler() -> LocalLLMHandler:
    """Get or create the global LLM handler instance."""
    global _llm_handler
    if _llm_handler is None:
        _llm_handler = LocalLLMHandler()
    return _llm_handler


if __name__ == "__main__":
    # Test LLM functionality
    print("Testing Local LLM Handler...")
    
    llm = LocalLLMHandler()
    
    if llm.available:
        print("\n--- Testing Journal Analysis ---")
        result = llm.analyze_journal_mood("I'm feeling really anxious about the upcoming presentation at work.")
        print(json.dumps(result, indent=2))
        
        print("\n--- Testing Transaction Categorization ---")
        category = llm.categorize_transaction("Coffee and breakfast", "Starbucks")
        print(f"Category: {category}")
        
        print("\n--- Testing Document Summary ---")
        doc = "This is a test document about machine learning. It discusses various algorithms and techniques."
        summary = llm.summarize_document(doc)
        print(f"Summary: {summary}")
    else:
        print("⚠ LLM not available. Install Ollama and pull a model:")
        print("  curl -fsSL https://ollama.ai/install.sh | sh")
        print(f"  ollama pull {DEFAULT_MODEL}")
