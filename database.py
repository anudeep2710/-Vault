"""
Encrypted local database handler for privacy-first data storage.
Uses SQLite with encryption for all sensitive data.
"""
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from config import DATABASE_PATH, DATA_RETENTION_DAYS, AUTO_DELETE_ENABLED
from encryption import get_encryption_manager


class PrivacyDatabase:
    """Encrypted local database for all agent data."""
    
    def __init__(self, db_path: Path = DATABASE_PATH):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.encryption_manager = get_encryption_manager()
        self.conn: Optional[sqlite3.Connection] = None
        
    def connect(self) -> None:
        """Establish database connection and create tables if needed."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        self._create_tables()
        
        if AUTO_DELETE_ENABLED:
            self._cleanup_old_data()
    
    def _create_tables(self) -> None:
        """Create all necessary tables."""
        cursor = self.conn.cursor()
        
        # Journal entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                content_encrypted BLOB NOT NULL,
                sentiment_score REAL,
                mood_category TEXT,
                tags TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Financial transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                amount REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                category TEXT,
                merchant_encrypted BLOB,
                description_encrypted BLOB,
                account_number_encrypted BLOB,
                tags TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Budget tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL UNIQUE,
                monthly_limit REAL NOT NULL,
                alert_threshold REAL DEFAULT 0.9,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath_encrypted BLOB,
                content_encrypted BLOB NOT NULL,
                file_type TEXT,
                summary_encrypted BLOB,
                entities_encrypted BLOB,
                processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Privacy audit log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL,
                module TEXT NOT NULL,
                details_encrypted BLOB,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_journal_timestamp ON journal_entries(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_processed ON documents(processed_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp)")
        
        self.conn.commit()
    
    def _cleanup_old_data(self) -> None:
        """Remove old data based on retention policies."""
        cursor = self.conn.cursor()
        
        for table, days in DATA_RETENTION_DAYS.items():
            if table == "audit_logs":
                table = "audit_log"
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            if table == "journal_entries":
                cursor.execute("DELETE FROM journal_entries WHERE timestamp < ?", (cutoff_date,))
            elif table == "finance":
                cursor.execute("DELETE FROM transactions WHERE timestamp < ?", (cutoff_date,))
            elif table == "documents":
                cursor.execute("DELETE FROM documents WHERE processed_at < ?", (cutoff_date,))
            elif table == "audit_log":
                cursor.execute("DELETE FROM audit_log WHERE timestamp < ?", (cutoff_date,))
        
        self.conn.commit()
    
    # ========== Journal Methods ==========
    
    def add_journal_entry(self, content: str, sentiment_score: float, mood_category: str, tags: List[str] = None) -> int:
        """Add a new journal entry."""
        self._log_audit("add_entry", "journal", {"length": len(content)})
        
        encrypted_content = self.encryption_manager.encrypt(content)
        tags_json = json.dumps(tags) if tags else None
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO journal_entries (timestamp, content_encrypted, sentiment_score, mood_category, tags)
            VALUES (?, ?, ?, ?, ?)
        """, (datetime.now(), encrypted_content, sentiment_score, mood_category, tags_json))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_journal_entries(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve journal entries within a date range."""
        self._log_audit("read_entries", "journal", {"start": str(start_date), "end": str(end_date)})
        
        cursor = self.conn.cursor()
        query = "SELECT * FROM journal_entries WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        entries = []
        for row in rows:
            entry = dict(row)
            entry['content'] = self.encryption_manager.decrypt(entry['content_encrypted'])
            entry['tags'] = json.loads(entry['tags']) if entry['tags'] else []
            del entry['content_encrypted']
            entries.append(entry)
        
        return entries
    
    def get_mood_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get mood statistics for the past N days."""
        start_date = datetime.now() - timedelta(days=days)
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT mood_category, COUNT(*) as count, AVG(sentiment_score) as avg_sentiment
            FROM journal_entries
            WHERE timestamp >= ?
            GROUP BY mood_category
        """, (start_date,))
        
        results = cursor.fetchall()
        return {
            "statistics": [dict(row) for row in results],
            "period_days": days
        }
    
    # ========== Finance Methods ==========
    
    def add_transaction(self, timestamp: datetime, amount: float, transaction_type: str, 
                       category: str, merchant: str = None, description: str = None, 
                       account_number: str = None, tags: List[str] = None) -> int:
        """Add a new financial transaction."""
        self._log_audit("add_transaction", "finance", {"amount": amount, "category": category})
        
        merchant_enc = self.encryption_manager.encrypt(merchant) if merchant else None
        description_enc = self.encryption_manager.encrypt(description) if description else None
        account_enc = self.encryption_manager.encrypt(account_number) if account_number else None
        tags_json = json.dumps(tags) if tags else None
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (timestamp, amount, transaction_type, category, 
                                     merchant_encrypted, description_encrypted, 
                                     account_number_encrypted, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, amount, transaction_type, category, merchant_enc, description_enc, account_enc, tags_json))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_transactions(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, 
                        category: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve transactions."""
        self._log_audit("read_transactions", "finance", {"category": category})
        
        cursor = self.conn.cursor()
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        transactions = []
        for row in rows:
            txn = dict(row)
            if txn['merchant_encrypted']:
                txn['merchant'] = self.encryption_manager.decrypt(txn['merchant_encrypted'])
            if txn['description_encrypted']:
                txn['description'] = self.encryption_manager.decrypt(txn['description_encrypted'])
            if txn['account_number_encrypted']:
                txn['account_number'] = self.encryption_manager.decrypt(txn['account_number_encrypted'])
            txn['tags'] = json.loads(txn['tags']) if txn['tags'] else []
            
            # Remove encrypted fields
            for key in ['merchant_encrypted', 'description_encrypted', 'account_number_encrypted']:
                if key in txn:
                    del txn[key]
            
            transactions.append(txn)
        
        return transactions
    
    def get_spending_by_category(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get spending statistics by category."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT category, SUM(amount) as total, COUNT(*) as count
            FROM transactions
            WHERE timestamp BETWEEN ? AND ? AND transaction_type = 'debit'
            GROUP BY category
            ORDER BY total DESC
        """, (start_date, end_date))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def set_budget(self, category: str, monthly_limit: float, alert_threshold: float = 0.9) -> None:
        """Set or update a budget for a category."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO budgets (category, monthly_limit, alert_threshold)
            VALUES (?, ?, ?)
            ON CONFLICT(category) DO UPDATE SET
                monthly_limit = ?,
                alert_threshold = ?,
                updated_at = CURRENT_TIMESTAMP
        """, (category, monthly_limit, alert_threshold, monthly_limit, alert_threshold))
        
        self.conn.commit()
    
    # ========== Document Methods ==========
    
    def add_document(self, filename: str, filepath: str, content: str, file_type: str,
                    summary: str = None, entities: List[str] = None) -> int:
        """Add a processed document."""
        self._log_audit("add_document", "documents", {"filename": filename})
        
        filepath_enc = self.encryption_manager.encrypt(filepath)
        content_enc = self.encryption_manager.encrypt(content)
        summary_enc = self.encryption_manager.encrypt(summary) if summary else None
        entities_enc = self.encryption_manager.encrypt(json.dumps(entities)) if entities else None
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO documents (filename, filepath_encrypted, content_encrypted, 
                                  file_type, summary_encrypted, entities_encrypted)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (filename, filepath_enc, content_enc, file_type, summary_enc, entities_enc))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_documents(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve processed documents."""
        self._log_audit("read_documents", "documents", {})
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM documents
            ORDER BY processed_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        documents = []
        
        for row in rows:
            doc = dict(row)
            doc['filepath'] = self.encryption_manager.decrypt(doc['filepath_encrypted'])
            doc['content'] = self.encryption_manager.decrypt(doc['content_encrypted'])
            if doc['summary_encrypted']:
                doc['summary'] = self.encryption_manager.decrypt(doc['summary_encrypted'])
            if doc['entities_encrypted']:
                doc['entities'] = json.loads(self.encryption_manager.decrypt(doc['entities_encrypted']))
            
            # Remove encrypted fields
            for key in ['filepath_encrypted', 'content_encrypted', 'summary_encrypted', 'entities_encrypted']:
                if key in doc:
                    del doc[key]
            
            documents.append(doc)
        
        return documents
    
    # ========== Audit Methods ==========
    
    def _log_audit(self, action_type: str, module: str, details: Dict[str, Any]) -> None:
        """Log an action for privacy audit trail."""
        details_enc = self.encryption_manager.encrypt(json.dumps(details))
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO audit_log (action_type, module, details_encrypted)
            VALUES (?, ?, ?)
        """, (action_type, module, details_enc))
        
        self.conn.commit()
    
    def get_audit_log(self, module: Optional[str] = None, days: int = 7) -> List[Dict[str, Any]]:
        """Retrieve privacy audit logs."""
        start_date = datetime.now() - timedelta(days=days)
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM audit_log WHERE timestamp >= ?"
        params = [start_date]
        
        if module:
            query += " AND module = ?"
            params.append(module)
        
        query += " ORDER BY timestamp DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        logs = []
        for row in rows:
            log = dict(row)
            log['details'] = json.loads(self.encryption_manager.decrypt(log['details_encrypted']))
            del log['details_encrypted']
            logs.append(log)
        
        return logs
    
    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


if __name__ == "__main__":
    # Test database functionality
    print("Testing Privacy Database...")
    
    with PrivacyDatabase() as db:
        print("✓ Database connected and tables created")
        
        # Test journal entry
        entry_id = db.add_journal_entry(
            content="Feeling great today! Had a productive day at work.",
            sentiment_score=0.8,
            mood_category="positive",
            tags=["work", "productivity"]
        )
        print(f"✓ Added journal entry #{entry_id}")
        
        # Test transaction
        txn_id = db.add_transaction(
            timestamp=datetime.now(),
            amount=45.50,
            transaction_type="debit",
            category="Food & Dining",
            merchant="Coffee Shop",
            description="Morning coffee"
        )
        print(f"✓ Added transaction #{txn_id}")
        
        # Retrieve and verify
        entries = db.get_journal_entries(limit=1)
        print(f"✓ Retrieved {len(entries)} journal entry")
        
        transactions = db.get_transactions(limit=1)
        print(f"✓ Retrieved {len(transactions)} transaction")
        
        print("\n✓ All database tests passed!")
