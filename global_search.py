"""
Global search functionality across all Vault modules.
Search journal entries, transactions, and documents.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

from database import PrivacyDatabase


class GlobalSearch:
    """Search across all modules in Vault."""
    
    def __init__(self):
        """Initialize global search."""
        self.db = PrivacyDatabase()
        self.db.connect()
    
    def search_all(self, query: str, limit: int = 50) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search across all modules.
        
        Args:
            query: Search query
            limit: Maximum results per module
            
        Returns:
            Dictionary with results from each module
        """
        query_lower = query.lower()
        
        results = {
            'journal': self._search_journal(query_lower, limit),
            'transactions': self._search_transactions(query_lower, limit),
            'documents': self._search_documents(query_lower, limit),
        }
        
        # Add total count
        results['total'] = sum(len(v) for v in results.values())
        
        return results
    
    def _search_journal(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search journal entries."""
        entries = self.db.get_journal_entries(limit=1000)
        
        matching = []
        for entry in entries:
            # Search in content, mood, and tags
            if (query in entry['content'].lower() or
                query in entry['mood_category'].lower() or
                any(query in tag.lower() for tag in entry.get('tags', []))):
                matching.append(entry)
                if len(matching) >= limit:
                    break
        
        return matching
    
    def _search_transactions(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search financial transactions."""
        transactions = self.db.get_transactions(limit=1000)
        
        matching = []
        for txn in transactions:
            # Search in category, merchant, description
            if (query in txn.get('category', '').lower() or
                query in txn.get('merchant', '').lower() or
                query in txn.get('description', '').lower()):
                matching.append(txn)
                if len(matching) >= limit:
                    break
        
        return matching
    
    def _search_documents(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search documents."""
        documents = self.db.get_documents(limit=1000)
        
        matching = []
        for doc in documents:
            # Search in filename, content, summary, entities
            if (query in doc['filename'].lower() or
                query in doc['content'].lower() or
                (doc.get('summary') and query in doc['summary'].lower()) or
                any(query in entity.lower() for entity in doc.get('entities', []))):
                matching.append(doc)
                if len(matching) >= limit:
                    break
        
        return matching
    
    def search_by_date(self, start_date: datetime, end_date: datetime) -> Dict[str, List]:
        """
        Search all data within a date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Results from all modules
        """
        return {
            'journal': self.db.get_journal_entries(start_date=start_date, end_date=end_date),
            'transactions': self.db.get_transactions(start_date=start_date, end_date=end_date),
            'documents': [d for d in self.db.get_documents() 
                         if start_date <= datetime.fromisoformat(d['processed_at']) <= end_date],
        }
    
    def search_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Search journal entries by tag."""
        entries = self.db.get_journal_entries(limit=1000)
        return [e for e in entries if tag.lower() in [t.lower() for t in e.get('tags', [])]]
    
    def search_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Search transactions by category."""
        return self.db.get_transactions(category=category, limit=1000)
    
    def close(self):
        """Close database connection."""
        self.db.close()


if __name__ == "__main__":
    # Test global search
    search = GlobalSearch()
    results = search.search_all("test")
    print(f"Found {results['total']} results")
    search.close()
