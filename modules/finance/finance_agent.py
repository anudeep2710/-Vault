"""
Finance Tracker Module - SMS parsing and spending analysis.
All transaction processing happens on-device with no cloud uploads.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import re

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from database import PrivacyDatabase
from llm_handler import get_llm_handler
from config import FINANCE_CONFIG
from utils import extract_amount, format_currency


class FinanceAgent:
    """Privacy-first finance tracker with SMS parsing."""
    
    def __init__(self):
        """Initialize the finance agent."""
        self.db = PrivacyDatabase()
        self.db.connect()
        self.llm = get_llm_handler()
        self.config = FINANCE_CONFIG
    
    def parse_sms(self, sms_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse bank SMS notification to extract transaction details.
        
        Args:
            sms_text: SMS message text
            
        Returns:
            Parsed transaction details or None
        """
        # Extract amount
        amount = extract_amount(sms_text)
        if amount == 0:
            return None
        
        # Determine transaction type (debit/credit)
        transaction_type = "debit"
        if any(word in sms_text.lower() for word in ["credited", "credit", "received", "deposited"]):
            transaction_type = "credit"
        
        # Extract merchant/description
        merchant = self._extract_merchant(sms_text)
        
        # Extract date (default to now if not found)
        timestamp = self._extract_date(sms_text) or datetime.now()
        
        # Extract account number
        account = self._extract_account_number(sms_text)
        
        return {
            "amount": amount,
            "transaction_type": transaction_type,
            "merchant": merchant,
            "timestamp": timestamp,
            "account_number": account,
            "raw_sms": sms_text
        }
    
    def _extract_merchant(self, text: str) -> Optional[str]:
        """Extract merchant name from SMS."""
        patterns = [
            r'(?:at|to|from)\s+([A-Z][A-Z\s&]+?)(?:\s+on|\s+dated|\.|\,|\s+INR|\s+Rs)',
            r'(?:merchant|vendor):\s*([A-Z][A-Z\s&]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                merchant = match.group(1).strip()
                # Clean up merchant name
                merchant = re.sub(r'\s+', ' ', merchant)
                return merchant
        
        return None
    
    def _extract_date(self, text: str) -> Optional[datetime]:
        """Extract date from SMS."""
        patterns = [
            (r'(\d{2})/(\d{2})/(\d{4})', '%d/%m/%Y'),
            (r'(\d{2})-(\d{2})-(\d{4})', '%d-%m-%Y'),
            (r'(\d{2})-([A-Z]{3})-(\d{2})', '%d-%b-%y'),
        ]
        
        for pattern, fmt in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    date_str = match.group(0)
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
        
        return None
    
    def _extract_account_number(self, text: str) -> Optional[str]:
        """Extract account number from SMS."""
        pattern = r'(?:a\/c|account|A\/C)\s*(?:XX|xx)?(\d+)'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        return None
    
    def add_transaction(self, amount: float, transaction_type: str, 
                       merchant: str = None, description: str = None,
                       category: str = None, timestamp: datetime = None,
                       account_number: str = None, auto_categorize: bool = True) -> Dict[str, Any]:
        """
        Add a transaction manually or from parsed SMS.
        
        Args:
            amount: Transaction amount
            transaction_type: 'debit' or 'credit'
            merchant: Merchant name
            description: Transaction description
            category: Spending category
            timestamp: Transaction timestamp (defaults to now)
            account_number: Account number
            auto_categorize: Use LLM to categorize if category not provided
            
        Returns:
            Transaction details with ID
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Auto-categorize if not provided
        if category is None and auto_categorize:
            if transaction_type == "credit":
                category = "Income"
            else:
                category = self._categorize_transaction(description or merchant or "")
        
        # Store transaction
        txn_id = self.db.add_transaction(
            timestamp=timestamp,
            amount=amount,
            transaction_type=transaction_type,
            category=category or "Other",
            merchant=merchant,
            description=description,
            account_number=account_number
        )
        
        # Check budget alerts
        alert = self._check_budget_alert(category)
        
        return {
            "id": txn_id,
            "amount": amount,
            "type": transaction_type,
            "category": category,
            "merchant": merchant,
            "timestamp": timestamp.isoformat(),
            "budget_alert": alert
        }
    
    def add_from_sms(self, sms_text: str) -> Dict[str, Any]:
        """
        Parse and add transaction from SMS.
        
        Args:
            sms_text: Bank SMS text
            
        Returns:
            Transaction details or error
        """
        parsed = self.parse_sms(sms_text)
        
        if parsed is None:
            return {"error": "Could not parse transaction from SMS"}
        
        return self.add_transaction(
            amount=parsed['amount'],
            transaction_type=parsed['transaction_type'],
            merchant=parsed['merchant'],
            description=parsed['raw_sms'],
            timestamp=parsed['timestamp'],
            account_number=parsed['account_number']
        )
    
    def _categorize_transaction(self, description: str) -> str:
        """Categorize transaction using LLM or rules."""
        # Try LLM first
        if self.llm.available and description:
            category = self.llm.categorize_transaction(description)
            if category in self.config['default_categories']:
                return category
        
        # Fallback to keyword matching
        description_lower = description.lower()
        
        keyword_map = {
            "Food & Dining": ["restaurant", "cafe", "coffee", "zomato", "swiggy", "food", "dining"],
            "Transportation": ["uber", "ola", "metro", "bus", "petrol", "fuel", "parking"],
            "Shopping": ["amazon", "flipkart", "mall", "store", "shopping"],
            "Entertainment": ["movie", "netflix", "spotify", "game", "concert"],
            "Bills & Utilities": ["electricity", "water", "internet", "mobile", "recharge"],
            "Healthcare": ["hospital", "pharmacy", "doctor", "medical", "health"],
            "Education": ["school", "college", "course", "tuition", "books"],
        }
        
        for category, keywords in keyword_map.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
        
        return "Other"
    
    def _check_budget_alert(self, category: str) -> Optional[str]:
        """Check if spending exceeds budget threshold."""
        # Get current month spending
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_month = datetime.now()
        
        spending = self.db.get_spending_by_category(start_of_month, end_of_month)
        
        # Find category spend
        category_spend = next((s['total'] for s in spending if s['category'] == category), 0)
        
        # Check against budget (would need to get budget from db)
        # For now, return None - can implement budget checking later
        return None
    
    def get_transactions(self, days: int = 30, category: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent transactions."""
        start_date = datetime.now() - timedelta(days=days)
        return self.db.get_transactions(start_date=start_date, category=category, limit=limit)
    
    def get_spending_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Get spending summary and statistics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Spending statistics by category
        """
        start_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()
        
        # Get spending by category
        spending = self.db.get_spending_by_category(start_date, end_date)
        
        # Calculate totals
        total_debit = sum(s['total'] for s in spending)
        
        # Get income (credits)
        transactions = self.db.get_transactions(start_date=start_date, end_date=end_date, limit=1000)
        total_credit = sum(t['amount'] for t in transactions if t['transaction_type'] == 'credit')
        
        # Top categories
        top_categories = sorted(spending, key=lambda x: x['total'], reverse=True)[:5]
        
        return {
            "period_days": days,
            "total_spent": total_debit,
            "total_income": total_credit,
            "net": total_credit - total_debit,
            "by_category": spending,
            "top_categories": top_categories,
            "transaction_count": len(transactions)
        }
    
    def get_insights(self, days: int = 30) -> str:
        """Generate spending insights."""
        summary = self.get_spending_summary(days)
        
        if summary['transaction_count'] == 0:
            return "Start tracking transactions to see personalized insights!"
        
        # Create data summary for LLM
        data_summary = f"""
        Period: {days} days
        Total spent: {format_currency(summary['total_spent'])}
        Total income: {format_currency(summary['total_income'])}
        Net: {format_currency(summary['net'])}
        Top spending categories: {', '.join([c['category'] + ': ' + format_currency(c['total']) for c in summary['top_categories']])}
        """
        
        # Get LLM insight
        if self.llm.available:
            insight = self.llm.generate_insight(
                data_summary,
                "Personal finance spending patterns"
            )
            if insight:
                return insight
        
        # Fallback insight
        top_cat = summary['top_categories'][0] if summary['top_categories'] else None
        if top_cat:
            return f"Your top spending category is {top_cat['category']} with {format_currency(top_cat['total'])}. Consider setting a budget to track this better."
        
        return "Keep tracking your spending to identify patterns and optimize your budget!"
    
    def set_budget(self, category: str, monthly_limit: float) -> None:
        """Set a monthly budget for a category."""
        self.db.set_budget(category, monthly_limit)
    
    def close(self):
        """Close database connection."""
        self.db.close()


if __name__ == "__main__":
    # Test finance agent
    print("Testing Finance Agent...")
    
    agent = FinanceAgent()
    
    # Test SMS parsing
    test_sms = [
        "Your A/C XX1234 debited with Rs.450.50 at COFFEE SHOP on 04-12-24. Avl Bal: Rs.5000",
        "INR 2500.00 credited to A/C XX1234 on 01-12-24. Salary credited.",
        "Debited Rs.1,234.00 from your account for AMAZON SHOPPING on 03-12-24"
    ]
    
    for sms in test_sms:
        print(f"\n--- Processing SMS ---")
        print(f"SMS: {sms[:60]}...")
        result = agent.add_from_sms(sms)
        if 'error' not in result:
            print(f"✓ Amount: {format_currency(result['amount'])}")
            print(f"  Type: {result['type']}")
            print(f"  Category: {result['category']}")
        else:
            print(f"✗ {result['error']}")
    
    # Get spending summary
    print("\n--- Spending Summary ---")
    summary = agent.get_spending_summary(days=30)
    print(f"Total spent: {format_currency(summary['total_spent'])}")
    print(f"Total income: {format_currency(summary['total_income'])}")
    print(f"Transactions: {summary['transaction_count']}")
    
    # Get insights
    print("\n--- Insights ---")
    insights = agent.get_insights(days=30)
    print(insights)
    
    agent.close()
