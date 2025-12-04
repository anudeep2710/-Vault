"""
Example 1: Quick Journal Demo
Demonstrates adding journal entries and viewing mood trends.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import PrivacyAgent

def main():
    print("="*60)
    print("📓 Journal Module Demo")
    print("="*60)
    
    with PrivacyAgent() as agent:
        # Add some sample entries
        entries = [
            "Had an amazing day! Completed my project and went for a run. Feeling accomplished!",
            "Feeling a bit stressed about work deadlines. Need to organize better.",
            "Quiet day today. Just reflecting on things and reading a good book.",
            "Great news! Got positive feedback from my manager. Very happy!",
            "Struggling with sleep lately. Feeling tired and overwhelmed."
        ]
        
        print("\n📝 Adding Journal Entries...\n")
        for entry in entries:
            result = agent.add_journal_entry(entry)
            print(f"✓ {result['mood_category']:>15} | {entry[:50]}...")
        
        print(f"\n📊 Mood Trends (Last 30 Days):")
        trends = agent.get_mood_trends(days=30)
        
        if trends.get('total_entries', 0) > 0:
            print(f"Total entries: {trends['total_entries']}")
            print(f"Average sentiment: {trends['average_sentiment']:.3f}")
            print(f"\nMood Distribution:")
            for mood, count in trends.get('mood_distribution', {}).items():
                print(f"  {mood:>15}: {'█' * count} {count}")
        
        print(f"\n💡 Insights:")
        insights = agent.get_journal_insights(days=30)
        print(f"  {insights}")
        
        print("\n" + "="*60)
        print("✓ Demo Complete!")
        print("="*60)

if __name__ == "__main__":
    main()
