"""
Main Privacy-First Personal Agent Orchestrator.
Coordinates all modules and provides a unified interface.
"""
from pathlib import Path
from typing import Dict, Any, Optional

from modules.journal.journal_agent import JournalAgent
from modules.finance.finance_agent import FinanceAgent
from modules.documents.document_agent import DocumentAgent
from llm_handler import get_llm_handler
from database import PrivacyDatabase
from config import FEATURES
from utils import setup_logging
from excel_export import ExcelExporter
from global_search import GlobalSearch
from tags_favorites import FavoritesManager

logger = setup_logging()


class PrivacyAgent:
    """Main agent orchestrating all privacy-first modules."""
    
    def __init__(self):
        """Initialize the privacy agent and all modules."""
        logger.info("Initializing Privacy-First Personal Agent...")
        
        # Initialize LLM handler
        self.llm = get_llm_handler()
        
        # Initialize modules based on feature flags
        self.journal = JournalAgent() if FEATURES['journal_enabled'] else None
        self.finance = FinanceAgent() if FEATURES['finance_enabled'] else None
        self.documents = DocumentAgent() if FEATURES['document_enabled'] else None
        
        # Database for privacy audit
        self.db = PrivacyDatabase()
        self.db.connect()
        
        # Additional features
        self.excel_exporter = ExcelExporter()
        self.search = GlobalSearch()
        self.favorites = FavoritesManager()
        
        logger.info("[OK] Privacy-First Personal Agent initialized")
        logger.info(f"  LLM Available: {self.llm.available}")
        logger.info(f"  Journal Module: {'[OK]' if self.journal else '[X]'}")
        logger.info(f"  Finance Module: {'[OK]' if self.finance else '[X]'}")
        logger.info(f"  Document Module: {'[OK]' if self.documents else '[X]'}")
    
    # ========== Journal Methods ==========
    
    def add_journal_entry(self, content: str, tags: list = None) -> Dict[str, Any]:
        """Add a journal entry."""
        if not self.journal:
            return {"error": "Journal module not enabled"}
        return self.journal.add_entry(content, tags)
    
    def get_journal_entries(self, days: int = 7) -> list:
        """Get recent journal entries."""
        if not self.journal:
            return []
        return self.journal.get_entries(days=days)
    
    def get_mood_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get mood trends."""
        if not self.journal:
            return {"error": "Journal module not enabled"}
        return self.journal.get_mood_trends(days=days)
    
    def get_journal_insights(self, days: int = 30) -> str:
        """Get journal insights."""
        if not self.journal:
            return "Journal module not enabled"
        return self.journal.get_insights(days=days)
    
    # ========== Finance Methods ==========
    
    def add_transaction_from_sms(self, sms_text: str) -> Dict[str, Any]:
        """Add transaction from SMS."""
        if not self.finance:
            return {"error": "Finance module not enabled"}
        return self.finance.add_from_sms(sms_text)
    
    def add_transaction(self, amount: float, transaction_type: str, **kwargs) -> Dict[str, Any]:
        """Add transaction manually."""
        if not self.finance:
            return {"error": "Finance module not enabled"}
        return self.finance.add_transaction(amount, transaction_type, **kwargs)
    
    def get_transactions(self, days: int = 30, category: str = None) -> list:
        """Get recent transactions."""
        if not self.finance:
            return []
        return self.finance.get_transactions(days=days, category=category)
    
    def get_spending_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get spending summary."""
        if not self.finance:
            return {"error": "Finance module not enabled"}
        return self.finance.get_spending_summary(days=days)
    
    def get_finance_insights(self, days: int = 30) -> str:
        """Get finance insights."""
        if not self.finance:
            return "Finance module not enabled"
        return self.finance.get_insights(days=days)
    
    def set_budget(self, category: str, monthly_limit: float) -> None:
        """Set a budget."""
        if self.finance:
            self.finance.set_budget(category, monthly_limit)
    
    # ========== Document Methods ==========
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process a document."""
        if not self.documents:
            return {"error": "Document module not enabled"}
        return self.documents.process_document(file_path)
    
    def query_document(self, document_id: int, question: str) -> str:
        """Ask question about a document."""
        if not self.documents:
            return "Document module not enabled"
        return self.documents.query_document(document_id, question)
    
    def get_documents(self, limit: int = 50) -> list:
        """Get processed documents."""
        if not self.documents:
            return []
        return self.documents.get_documents(limit=limit)
    
    def search_documents(self, query: str) -> list:
        """Search documents."""
        if not self.documents:
            return []
        return self.documents.search_documents(query)
    
    # ========== Privacy & Audit Methods ==========
    
    def get_privacy_audit(self, module: str = None, days: int = 7) -> list:
        """Get privacy audit logs."""
        return self.db.get_audit_log(module=module, days=days)
    
    # ========== Excel Export Methods ==========
    
    def export_to_excel(self, module: str = "all") -> str:
        """
        Export data to Excel.
        
        Args:
            module: 'journal', 'finance', 'documents', or 'all'
            
        Returns:
            Path to exported file
        """
        if module == "all":
            return self.excel_exporter.export_all(
                self.get_journal_entries(days=9999),
                self.get_transactions(days=9999),
                self.get_documents(limit=9999)
            )
        elif module == "journal":
            return self.excel_exporter.export_journal(self.get_journal_entries(days=9999))
        elif module == "finance":
            return self.excel_exporter.export_transactions(self.get_transactions(days=9999))
        elif module == "documents":
            return self.excel_exporter.export_documents(self.get_documents(limit=9999))
    
    # ========== Global Search Methods ==========
    
    def search_all(self, query: str, limit: int = 50) -> Dict[str, Any]:
        """Search across all modules."""
        return self.search.search_all(query, limit)
    
    # ========== Favorites Methods ==========
    
    def add_favorite(self, module: str, item_id: int) -> bool:
        """Mark an item as favorite."""
        return self.favorites.add_favorite(module, item_id)
    
    def remove_favorite(self, module: str, item_id: int) -> bool:
        """Remove item from favorites."""
        return self.favorites.remove_favorite(module, item_id)
    
    def get_favorites(self, module: str = None) -> List:
        """Get all favorites."""
        return self.favorites.get_favorites(module)
    
    def export_data(self, export_path: str = None) -> str:
        """Export all data (for GDPR-like data portability)."""
        import json
        from datetime import datetime
        
        if export_path is None:
            export_path = f"privacy_agent_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "export_date": datetime.now().isoformat(),
            "journal_entries": self.get_journal_entries(days=9999) if self.journal else [],
            "transactions": self.get_transactions(days=9999) if self.finance else [],
            "documents": [
                {k: v for k, v in doc.items() if k != 'content'}  # Exclude full content
                for doc in self.get_documents(limit=1000)
            ] if self.documents else [],
            "audit_log": self.get_privacy_audit(days=90)
        }
        
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"✓ Data exported to {export_path}")
        return export_path
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and statistics."""
        status = {
            "llm_available": self.llm.available,
            "modules": {
                "journal": FEATURES['journal_enabled'],
                "finance": FEATURES['finance_enabled'],
                "documents": FEATURES['document_enabled']
            },
            "statistics": {}
        }
        
        # Get statistics from each module
        if self.journal:
            status['statistics']['journal_entries'] = len(self.get_journal_entries(days=9999))
        
        if self.finance:
            status['statistics']['transactions'] = len(self.get_transactions(days=9999))
        
        if self.documents:
            status['statistics']['documents'] = len(self.get_documents(limit=9999))
        
        return status
    
    def close(self):
        """Close all connections."""
        logger.info("Closing Privacy-First Personal Agent...")
        
        if self.journal:
            self.journal.close()
        if self.finance:
            self.finance.close()
        if self.documents:
            self.documents.close()
        
        self.db.close()
        
        logger.info("[OK] Agent closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


if __name__ == "__main__":
    # Test the main agent
    print("Testing Privacy-First Personal Agent...")
    
    with PrivacyAgent() as agent:
        # Get system status
        status = agent.get_system_status()
        print(f"\nSystem Status:")
        print(f"  LLM: {'✓' if status['llm_available'] else '✗'}")
        print(f"  Modules: {', '.join([m for m, enabled in status['modules'].items() if enabled])}")
        print(f"  Stats: {status['statistics']}")
        
        print("\n✓ Privacy-First Personal Agent is ready!")
