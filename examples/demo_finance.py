"""
Example 2: Finance SMS Parsing Demo
Demonstrates parsing bank SMS notifications and generating spending reports.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import PrivacyAgent
from utils import format_currency

def main():
    print("="*60)
    print("💰 Finance Module Demo")
    print("="*60)
    
    with PrivacyAgent() as agent:
        # Sample bank SMS messages
        sms_messages = [
            "Your A/C XX1234 debited with Rs.450.50 at COFFEE SHOP on 01-12-24. Avl Bal: Rs.5000",
            "INR 2500.00 credited to A/C XX1234 on 01-12-24. Salary credited.",
            "Debited Rs.1,234.00 from account for AMAZON SHOPPING on 02-12-24",
            "Your A/C XX5678 debited with Rs.850.00 at METRO CARD RECHARGE on 02-12-24",
            "Debited Rs.3,200.00 for ELECTRICITY BILL on 03-12-24",
            "Your A/C XX1234 debited with Rs.950.00 at RESTAURANT on 03-12-24",
            "Debited Rs.1,500.00 for MOBILE RECHARGE on 04-12-24"
        ]
        
        print("\n📱 Parsing SMS Messages...\n")
        for sms in sms_messages:
            result = agent.add_transaction_from_sms(sms)
            if 'error' not in result:
                print(f"✓ {format_currency(result['amount']):>12} | {result['type']:>6} | {result['category']}")
            else:
                print(f"✗ Could not parse: {sms[:50]}")
        
        print(f"\n📊 Spending Summary (Last 30 Days):")
        summary = agent.get_spending_summary(days=30)
        
        print(f"\nTotal Spent:  {format_currency(summary['total_spent'])}")
        print(f"Total Income: {format_currency(summary['total_income'])}")
        print(f"Net:          {format_currency(summary['net'])}")
        
        print(f"\n📈 Top Spending Categories:")
        for cat in summary.get('top_categories', []):
            print(f"  {cat['category']:>20}: {format_currency(cat['total'])}")
        
        print(f"\n💡 Insights:")
        insights = agent.get_finance_insights(days=30)
        print(f"  {insights}")
        
        print("\n" + "="*60)
        print("✓ Demo Complete!")
        print("="*60)

if __name__ == "__main__":
    main()
