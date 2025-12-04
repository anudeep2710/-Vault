"""
Tags and favorites system for Vault.
Add tags to entries, transactions, and documents. Mark items as favorites.
"""
from typing import List, Optional
from database import PrivacyDatabase


class TagsManager:
    """Manage tags across all modules."""
    
    def __init__(self):
        """Initialize tags manager."""
        self.db = PrivacyDatabase()
        self.db.connect()
    
    def add_tags_to_journal(self, entry_id: int, tags: List[str]) -> bool:
        """Add tags to a journal entry."""
        # This would require updating the database schema
        # For now, tags are added during entry creation
        pass
    
    def get_all_tags(self) -> Dict[str, List[str]]:
        """Get all unique tags from all modules."""
        journal_tags = set()
        
        # Get journal tags
        entries = self.db.get_journal_entries(limit=10000)
        for entry in entries:
            journal_tags.update(entry.get('tags', []))
        
        return {
            'journal': sorted(list(journal_tags)),
            'count': len(journal_tags)
        }
    
    def search_by_tag(self, tag: str) -> List:
        """Find all items with a specific tag."""
        entries = self.db.get_journal_entries(limit=10000)
        return [e for e in entries if tag.lower() in [t.lower() for t in e.get('tags', [])]]
    
    def get_popular_tags(self, limit: int = 10) -> List[tuple]:
        """Get most frequently used tags."""
        tag_counts = {}
        
        entries = self.db.get_journal_entries(limit=10000)
        for entry in entries:
            for tag in entry.get('tags', []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Sort by count
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_tags[:limit]
    
    def close(self):
        """Close database connection."""
        self.db.close()


class FavoritesManager:
    """Manage favorites/bookmarks."""
    
    def __init__(self):
        """Initialize favorites manager."""
        self.db = PrivacyDatabase()
        self.db.connect()
        self._create_favorites_table()
    
    def _create_favorites_table(self):
        """Create favorites table if it doesn't exist."""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(module, item_id)
            )
        """)
        self.db.conn.commit()
    
    def add_favorite(self, module: str, item_id: int) -> bool:
        """
        Mark an item as favorite.
        
        Args:
            module: 'journal', 'finance', or 'documents'
            item_id: ID of the item
            
        Returns:
            True if successful
        """
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO favorites (module, item_id)
                VALUES (?, ?)
            """, (module, item_id))
            self.db.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding favorite: {e}")
            return False
    
    def remove_favorite(self, module: str, item_id: int) -> bool:
        """Remove an item from favorites."""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("""
                DELETE FROM favorites
                WHERE module = ? AND item_id = ?
            """, (module, item_id))
            self.db.conn.commit()
            return True
        except Exception as e:
            print(f"Error removing favorite: {e}")
            return False
    
    def get_favorites(self, module: Optional[str] = None) -> List[Dict]:
        """
        Get all favorites, optionally filtered by module.
        
        Args:
            module: Optional module filter
            
        Returns:
            List of favorite items
        """
        cursor = self.db.conn.cursor()
        
        if module:
            cursor.execute("""
                SELECT * FROM favorites
                WHERE module = ?
                ORDER BY created_at DESC
            """, (module,))
        else:
            cursor.execute("""
                SELECT * FROM favorites
                ORDER BY created_at DESC
            """)
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def is_favorite(self, module: str, item_id: int) -> bool:
        """Check if an item is favorited."""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM favorites
            WHERE module = ? AND item_id = ?
        """, (module, item_id))
        
        count = cursor.fetchone()[0]
        return count > 0
    
    def close(self):
        """Close database connection."""
        self.db.close()


if __name__ == "__main__":
    # Test tags and favorites
    tags_mgr = TagsManager()
    fav_mgr = FavoritesManager()
    
    print("Tags and Favorites system ready!")
    
    tags_mgr.close()
    fav_mgr.close()
