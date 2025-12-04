"""
Excel export functionality for Vault.
Export journal entries, transactions, and documents to XLSX format.
"""
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from config import EXPORTS_DIR


class ExcelExporter:
    """Export data to Excel format."""
    
    def __init__(self):
        """Initialize the Excel exporter."""
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    def export_journal(self, entries: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Export journal entries to Excel.
        
        Args:
            entries: List of journal entries
            filename: Optional custom filename
            
        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"journal_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        filepath = EXPORTS_DIR / filename
        
        # Prepare data for export
        data = []
        for entry in entries:
            data.append({
                'Date': entry['timestamp'],
                'Mood': entry['mood_category'],
                'Sentiment Score': entry['sentiment_score'],
                'Content': entry['content'],
                'Tags': ', '.join(entry.get('tags', [])),
            })
        
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False, sheet_name='Journal Entries')
        
        return str(filepath)
    
    def export_transactions(self, transactions: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Export financial transactions to Excel.
        
        Args:
            transactions: List of transactions
            filename: Optional custom filename
            
        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"transactions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        filepath = EXPORTS_DIR / filename
        
        # Prepare data
        data = []
        for txn in transactions:
            data.append({
                'Date': txn['timestamp'],
                'Amount': txn['amount'],
                'Type': txn['transaction_type'],
                'Category': txn.get('category', 'N/A'),
                'Merchant': txn.get('merchant', 'N/A'),
                'Description': txn.get('description', 'N/A'),
            })
        
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False, sheet_name='Transactions')
        
        return str(filepath)
    
    def export_documents(self, documents: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Export document metadata to Excel.
        
        Args:
            documents: List of documents
            filename: Optional custom filename
            
        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"documents_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        filepath = EXPORTS_DIR / filename
        
        # Prepare data
        data = []
        for doc in documents:
            data.append({
                'Filename': doc['filename'],
                'Type': doc['file_type'],
                'Processed Date': doc['processed_at'],
                'Summary': doc.get('summary', 'N/A')[:200],  # Truncate long summaries
                'Entities': ', '.join(doc.get('entities', [])[:10]),  # First 10 entities
            })
        
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False, sheet_name='Documents')
        
        return str(filepath)
    
    def export_all(self, journal_entries: List, transactions: List, documents: List) -> str:
        """
        Export all data to a single Excel file with multiple sheets.
        
        Returns:
            Path to exported file
        """
        filename = f"vault_complete_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = EXPORTS_DIR / filename
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Journal sheet
            if journal_entries:
                journal_data = [{
                    'Date': e['timestamp'],
                    'Mood': e['mood_category'],
                    'Sentiment': e['sentiment_score'],
                    'Content': e['content'],
                    'Tags': ', '.join(e.get('tags', [])),
                } for e in journal_entries]
                pd.DataFrame(journal_data).to_excel(writer, sheet_name='Journal', index=False)
            
            # Transactions sheet
            if transactions:
                txn_data = [{
                    'Date': t['timestamp'],
                    'Amount': t['amount'],
                    'Type': t['transaction_type'],
                    'Category': t.get('category', 'N/A'),
                    'Merchant': t.get('merchant', 'N/A'),
                } for t in transactions]
                pd.DataFrame(txn_data).to_excel(writer, sheet_name='Transactions', index=False)
            
            # Documents sheet
            if documents:
                doc_data = [{
                    'Filename': d['filename'],
                    'Type': d['file_type'],
                    'Processed': d['processed_at'],
                    'Summary': d.get('summary', 'N/A')[:200],
                } for d in documents]
                pd.DataFrame(doc_data).to_excel(writer, sheet_name='Documents', index=False)
        
        return str(filepath)


if __name__ == "__main__":
    # Test Excel export
    exporter = ExcelExporter()
    print("Excel Exporter ready!")
