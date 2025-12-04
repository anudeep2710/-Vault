"""
Example 3: Document Analysis Demo
Demonstrates processing documents and asking questions.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import PrivacyAgent

def main():
    print("="*60)
    print("📄 Document Module Demo")
    print("="*60)
    
    # Create a sample document
    sample_doc = Path("sample_contract.txt")
    sample_doc.write_text("""
CONFIDENTIAL CONSULTING AGREEMENT

This Agreement is entered into on December 1, 2024, between:

Party A: John Smith
Address: 123 Main Street, New York, NY 10001
Email: john.smith@email.com

Party B: Acme Corporation
Address: 456 Business Avenue, San Francisco, CA 94102
Contact: Jane Doe, CEO

TERMS AND CONDITIONS:

1. Services: Party A will provide consulting services in software development
   and system architecture for a period of 6 months.

2. Compensation: Party B agrees to pay Party A a total of $50,000 USD,
   payable in monthly installments of $8,333.33.

3. Confidentiality: Both parties agree to maintain confidentiality of all
   proprietary information shared during the engagement.

4. Term: This agreement is effective from December 1, 2024, and will
   terminate on May 31, 2025, unless extended by mutual written consent.

5. Termination: Either party may terminate this agreement with 30 days
   written notice.

Signatures:

_____________________          _____________________
John Smith                     Jane Doe
Date: December 1, 2024        Date: December 1, 2024
    """)
    
    try:
        with PrivacyAgent() as agent:
            print("\n📄 Processing Document...\n")
            result = agent.process_document(str(sample_doc))
            
            if 'error' not in result:
                print(f"✓ Document: {result['filename']}")
                print(f"  Text length: {result['text_length']} characters")
                
                if result.get('summary'):
                    print(f"\n📝 Summary:")
                    print(f"  {result['summary']}")
                
                if result.get('entities'):
                    print(f"\n🏷️  Entities Found ({len(result['entities'])}):")
                    for entity in result['entities'][:10]:
                        print(f"  • {entity}")
                
                # Ask questions about the document
                if agent.llm.available:
                    print(f"\n💭 Q&A:")
                    
                    questions = [
                        "What is the total contract value?",
                        "When does the agreement start and end?",
                        "Who are the parties involved?"
                    ]
                    
                    for question in questions:
                        print(f"\nQ: {question}")
                        answer = agent.query_document(result['id'], question)
                        print(f"A: {answer}")
                else:
                    print("\n⚠️  LLM not available - Q&A requires Ollama")
            else:
                print(f"✗ Error: {result['error']}")
            
            print("\n" + "="*60)
            print("✓ Demo Complete!")
            print("="*60)
    
    finally:
        # Cleanup
        if sample_doc.exists():
            sample_doc.unlink()

if __name__ == "__main__":
    main()
