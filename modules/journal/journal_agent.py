"""
Mental Health Journal Module - Mood tracking and analysis.
Processes journal entries entirely on-device with local LLM and sentiment analysis.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from textblob import TextBlob

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from database import PrivacyDatabase
from llm_handler import get_llm_handler
from config import JOURNAL_CONFIG


class JournalAgent:
    """Mental health journaling companion with local mood analysis."""
    
    def __init__(self):
        """Initialize the journal agent."""
        self.db = PrivacyDatabase()
        self.db.connect()
        self.llm = get_llm_handler()
        self.config = JOURNAL_CONFIG
    
    def add_entry(self, content: str, tags: List[str] = None) -> Dict[str, Any]:
        """
        Add a new journal entry with automatic mood analysis.
        
        Args:
            content: Journal entry text
            tags: Optional tags for the entry
            
        Returns:
            Entry details with mood analysis
        """
        # Perform sentiment analysis using TextBlob
        sentiment_score = self._analyze_sentiment(content)
        mood_category = self._categorize_mood(sentiment_score)
        
        # Try to get LLM insights
        llm_analysis = None
        if self.llm.available:
            llm_analysis = self.llm.analyze_journal_mood(content)
        
        # Check for trigger words
        triggers = self._detect_triggers(content)
        
        # Store in database
        entry_id = self.db.add_journal_entry(
            content=content,
            sentiment_score=sentiment_score,
            mood_category=mood_category,
            tags=tags
        )
        
        response = {
            "id": entry_id,
            "sentiment_score": sentiment_score,
            "mood_category": mood_category,
            "timestamp": datetime.now().isoformat(),
            "triggers_detected": triggers,
        }
        
        # Add LLM insights if available
        if llm_analysis and 'error' not in llm_analysis:
            response['llm_analysis'] = llm_analysis
        
        # Provide supportive feedback
        response['feedback'] = self._generate_feedback(mood_category, triggers)
        
        return response
    
    def _analyze_sentiment(self, text: str) -> float:
        """
        Analyze sentiment using TextBlob.
        
        Returns:
            Sentiment polarity score (-1.0 to 1.0)
        """
        blob = TextBlob(text)
        return blob.sentiment.polarity
    
    def _categorize_mood(self, sentiment_score: float) -> str:
        """Categorize mood based on sentiment score."""
        if sentiment_score >= 0.5:
            return "very_positive"
        elif sentiment_score >= 0.1:
            return "positive"
        elif sentiment_score >= -0.1:
            return "neutral"
        elif sentiment_score >= -0.5:
            return "negative"
        else:
            return "very_negative"
    
    def _detect_triggers(self, text: str) -> List[str]:
        """Detect concerning trigger words."""
        text_lower = text.lower()
        detected = []
        
        for trigger in self.config['trigger_words']:
            if trigger.lower() in text_lower:
                detected.append(trigger)
        
        return detected
    
    def _generate_feedback(self, mood: str, triggers: List[str]) -> str:
        """Generate supportive feedback based on mood."""
        if triggers:
            return "I noticed you're going through a difficult time. Remember that it's okay to seek support. Consider talking to someone you trust."
        elif mood == "very_positive":
            return "It's wonderful to hear you're feeling great! Keep capturing these positive moments."
        elif mood == "positive":
            return "Glad to see you're in a good place. Keep up the positive energy!"
        elif mood == "neutral":
            return "Thanks for sharing. Your thoughts matter, and tracking them helps understand patterns."
        elif mood == "negative":
            return "I hear you. It's important to acknowledge difficult feelings. Be kind to yourself."
        else:
            return "Thank you for trusting me with your feelings. Remember, difficult times are temporary."
    
    def get_entries(self, days: int = 7, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve recent journal entries.
        
        Args:
            days: Number of days to look back
            limit: Maximum entries to return
            
        Returns:
            List of journal entries
        """
        start_date = datetime.now() - timedelta(days=days)
        return self.db.get_journal_entries(start_date=start_date, limit=limit)
    
    def get_mood_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze mood trends over time.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Mood statistics and trends
        """
        stats = self.db.get_mood_statistics(days=days)
        entries = self.get_entries(days=days, limit=1000)
        
        # Calculate additional metrics
        if entries:
            avg_sentiment = sum(e['sentiment_score'] for e in entries) / len(entries)
            
            # Calculate mood distribution
            mood_counts = {}
            for entry in entries:
                mood = entry['mood_category']
                mood_counts[mood] = mood_counts.get(mood, 0) + 1
            
            # Detect patterns (simple day-of-week analysis)
            day_moods = {}
            for entry in entries:
                day = datetime.fromisoformat(entry['timestamp']).strftime('%A')
                if day not in day_moods:
                    day_moods[day] = []
                day_moods[day].append(entry['sentiment_score'])
            
            day_averages = {
                day: sum(scores) / len(scores) 
                for day, scores in day_moods.items()
            }
            
            return {
                "period_days": days,
                "total_entries": len(entries),
                "average_sentiment": round(avg_sentiment, 3),
                "mood_distribution": mood_counts,
                "day_of_week_averages": day_averages,
                "statistics": stats['statistics']
            }
        
        return {
            "period_days": days,
            "total_entries": 0,
            "message": "No entries found in this period"
        }
    
    def get_insights(self, days: int = 30) -> str:
        """
        Generate insights from journal patterns.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Natural language insights
        """
        trends = self.get_mood_trends(days)
        
        if trends['total_entries'] == 0:
            return "Start journaling regularly to see personalized insights!"
        
        # Create data summary for LLM
        summary = f"""
        Period: {days} days
        Total entries: {trends['total_entries']}
        Average sentiment: {trends.get('average_sentiment', 0):.2f}
        Mood distribution: {trends.get('mood_distribution', {})}
        """
        
        # Get LLM insight if available
        if self.llm.available:
            insight = self.llm.generate_insight(
                summary,
                "Mental health journaling patterns"
            )
            if insight:
                return insight
        
        # Fallback to rule-based insight
        avg = trends.get('average_sentiment', 0)
        if avg > 0.3:
            return f"Over the past {days} days, you've been mostly positive! Keep nurturing what makes you happy."
        elif avg < -0.3:
            return f"You've had some challenging days recently. Consider activities that bring you joy and don't hesitate to reach out for support."
        else:
            return f"Your mood has been fairly balanced over the past {days} days. Journaling is a great way to maintain self-awareness!"
    
    def close(self):
        """Close database connection."""
        self.db.close()


if __name__ == "__main__":
    # Test journal agent
    print("Testing Journal Agent...")
    
    agent = JournalAgent()
    
    # Add test entries
    test_entries = [
        "Had an amazing day! Finished my project and went for a run. Feeling accomplished!",
        "Feeling a bit stressed about work deadlines. Need to organize better.",
        "Quiet day today. Just reflecting on things.",
    ]
    
    for entry_text in test_entries:
        result = agent.add_entry(entry_text)
        print(f"\n--- Entry Added ---")
        print(f"Mood: {result['mood_category']}")
        print(f"Sentiment: {result['sentiment_score']:.2f}")
        print(f"Feedback: {result['feedback']}")
        if 'llm_analysis' in result:
            print(f"LLM Analysis: {result['llm_analysis']}")
    
    # Get trends
    print("\n--- Mood Trends ---")
    trends = agent.get_mood_trends(days=30)
    print(f"Total entries: {trends['total_entries']}")
    print(f"Average sentiment: {trends.get('average_sentiment', 0)}")
    
    # Get insights
    print("\n--- Insights ---")
    insights = agent.get_insights(days=30)
    print(insights)
    
    agent.close()
