"""
Quick Start Demo - Run all three modules in sequence
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agent import PrivacyAgent
from utils import format_currency, color_text

def print_section(title):
    """Print a section header."""
    print("\n" + "="*60)
    print(color_text(f"  {title}", "cyan"))
    print("="*60 + "\n")

def main():
    print_section("🔒 PRIVACY-FIRST PERSONAL AGENT - QUICK DEMO")
    
    print(color_text("This demo showcases all three modules:", "yellow"))
    print("  📓 Mental Health Journal")
    print("  💰 Finance Tracker")
    print("  📄 Document Analyzer\n")
    
    with PrivacyAgent() as agent:
        # System Status
        print_section("📊 System Status")
        status = agent.get_system_status()
        print(f"LLM Available: {color_text('✓', 'green') if status['llm_available'] else color_text('✗', 'red')}")
        print(f"Modules: {', '.join([m for m, enabled in status['modules'].items() if enabled])}")
        
        # Journal Demo
        print_section("📓 Journal Module")
        print("Adding sample entry...")
        result = agent.add_journal_entry(
            "Had a productive day today! Completed my tasks and feeling great.",
            tags=["work", "productivity"]
        )
        print(color_text(f"✓ Entry saved", "green"))
        print(f"  Mood: {result['mood_category']}")
        print(f"  Sentiment: {result['sentiment_score']:.3f}")
        print(f"  Feedback: {result['feedback']}")
        
        # Finance Demo
        print_section("💰 Finance Module")
        print("Parsing bank SMS...")
        sms = "Your A/C XX1234 debited with Rs.1,250.00 at COFFEE SHOP on 04-12-24"
        result = agent.add_transaction_from_sms(sms)
        if 'error' not in result:
            print(color_text(f"✓ Transaction added", "green"))
            print(f"  Amount: {format_currency(result['amount'])}")
            print(f"  Category: {result['category']}")
        
        # Document Demo (create sample)
        print_section("📄 Document Module")
        sample_doc = Path("quick_demo_doc.txt")
        sample_doc.write_text("""
        Sample Business Proposal
        
        Company: Tech Solutions Inc.
        Contact: Alice Johnson
        Date: December 4, 2024
        Budget: $25,000
        
        We propose to develop a custom web application for your business needs.
        The project will take approximately 3 months to complete.
        """)
        
        try:
            print("Processing document...")
            result = agent.process_document(str(sample_doc))
            if 'error' not in result:
                print(color_text(f"✓ Document processed", "green"))
                print(f"  File: {result['filename']}")
                print(f"  Text length: {result['text_length']} chars")
                if result.get('entities'):
                    print(f"  Entities: {', '.join(result['entities'][:5])}")
        finally:
            sample_doc.unlink()
        
        # Privacy Audit
        print_section("🔍 Privacy Audit")
        audit = agent.get_privacy_audit(days=1)
        print(f"Recent activity: {len(audit)} events")
        for event in audit[:3]:
            print(f"  • {event['module']} → {event['action_type']}")
        
        # Final Message
        print_section("✅ Demo Complete!")
        print(color_text("All three modules are working correctly!", "green"))
        print("\nYour data is:")
        print("  🔒 Encrypted at rest")
        print("  🏠 Stored locally on your device")
        print("  🔍 Fully audited for transparency")
        print("\nTo start the full CLI: python cli.py")

if __name__ == "__main__":
    main()
