"""
Voice Journaling Module using RunAnywhere SDK Voice Pipeline
Enables users to record voice journal entries with on-device transcription
"""
import io
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from runanywhere_handler import RunAnywhereHandler
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False


class VoiceJournalAgent:
    """Voice journaling with on-device transcription."""
    
    def __init__(self):
        """Initialize voice journal agent."""
        self.handler = RunAnywhereHandler() if VOICE_AVAILABLE else None
        self.available = self.handler and self.handler.available if VOICE_AVAILABLE else False
    
    def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """
        Transcribe audio to text using RunAnywhere Voice Pipeline.
        
        Args:
            audio_data: Raw audio bytes (WAV format)
            
        Returns:
            Transcribed text or None
        """
        if not self.available:
            return None
        
        try:
            text = self.handler.voice_to_text(audio_data)
            return text
        except Exception as e:
            print(f"Transcription error: {e}")
            return None
    
    def record_voice_entry(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Record and transcribe voice journal entry.
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            {
                "text": str,
                "timestamp": str,
                "duration_seconds": float,
                "success": bool
            }
        """
        if not self.available:
            return {"success": False, "error": "Voice transcription not available"}
        
        try:
            # Read audio file
            audio_path = Path(audio_file_path)
            if not audio_path.exists():
                return {"success": False, "error": "Audio file not found"}
            
            audio_data = audio_path.read_bytes()
            
            # Transcribe
            text = self.transcribe_audio(audio_data)
            
            if text:
                return {
                    "success": True,
                    "text": text,
                    "timestamp": datetime.now().isoformat(),
                    "duration_seconds": len(audio_data) / (16000 * 2),  # Approximate
                    "word_count": len(text.split())
                }
            else:
                return {"success": False, "error": "Transcription failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}


# Example usage
if __name__ == "__main__":
    voice = VoiceJournalAgent()
    
    if voice.available:
        print("[OK] Voice journaling available")
        print("Record audio and save as WAV file, then call:")
        print('result = voice.record_voice_entry("recording.wav")')
    else:
        print("[WARNING] Voice journaling requires RunAnywhere SDK")
        print("Install RunAnywhere SDK and initialize voice pipeline")
