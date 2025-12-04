# Privacy-First Personal Agent - Examples

This directory contains example scripts and usage scenarios.

## Example 1: Journal Entry with Mood Analysis

```python
from agent import PrivacyAgent

with PrivacyAgent() as agent:
    # Add a journal entry
    result = agent.add_journal_entry(
        content="Today was challenging but I learned a lot. Feeling grateful.",
        tags=["work", "learning", "gratitude"]
    )
    
    print(f"Mood: {result['mood_category']}")
    print(f"Sentiment: {result['sentiment_score']}")
    print(f"Feedback: {result['feedback']}")
    
    # Get insights
    insights = agent.get_journal_insights(days=30)
    print(f"\nInsights: {insights}")
```

## Example 2: Parse Bank SMS

```python
from agent import PrivacyAgent

with PrivacyAgent() as agent:
    # Sample bank SMS
    sms = "Your A/C XX1234 debited with Rs.1,250.00 at AMAZON INDIA on 04-12-24"
    
    result = agent.add_transaction_from_sms(sms)
    
    print(f"Amount: ₹{result['amount']}")
    print(f"Category: {result['category']}")
```

## Example 3: Analyze a Document

```python
from agent import PrivacyAgent

with PrivacyAgent() as agent:
    # Process a confidential document
    result = agent.process_document("path/to/contract.pdf")
    
    print(f"Summary: {result['summary']}")
    print(f"Entities: {result['entities']}")
    
    # Ask questions about it
    answer = agent.query_document(
        result['id'],
        "What is the contract value?"
    )
    print(f"Answer: {answer}")
```

## Example 4: Monthly Financial Report

```python
from agent import PrivacyAgent

with PrivacyAgent() as agent:
    # Get spending summary
    summary = agent.get_spending_summary(days=30)
    
    print(f"Total Spent: ₹{summary['total_spent']}")
    print(f"Total Income: ₹{summary['total_income']}")
    print(f"Net: ₹{summary['net']}")
    
    print("\nTop Categories:")
    for cat in summary['top_categories']:
        print(f"  {cat['category']}: ₹{cat['total']}")
```

## Example 5: Privacy Audit

```python
from agent import PrivacyAgent

with PrivacyAgent() as agent:
    # View what the agent has accessed
    audit_logs = agent.get_privacy_audit(days=7)
    
    for log in audit_logs:
        print(f"{log['timestamp']} - {log['module']}: {log['action_type']}")
```

## Example 6: Data Export

```python
from agent import PrivacyAgent

with PrivacyAgent() as agent:
    # Export all your data
    export_path = agent.export_data()
    print(f"Data exported to: {export_path}")
```

## Running Examples

To run these examples:

```bash
cd examples
python example_name.py
```

Remember: All processing happens on your device. No data leaves your computer!
