"""
Privacy audit logging and transparency module.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

from database import PrivacyDatabase
from utils import create_table


class PrivacyAuditor:
    """Manages privacy audit logging and reporting."""
    
    def __init__(self):
        """Initialize the privacy auditor."""
        self.db = PrivacyDatabase()
        self.db.connect()
    
    def get_audit_report(self, days: int = 30) -> Dict[str, Any]:
        """
        Generate a comprehensive privacy audit report.
        
        Args:
            days: Number of days to include in report
            
        Returns:
            Audit report with statistics
        """
        logs = self.db.get_audit_log(days=days)
        
        if not logs:
            return {
                "period_days": days,
                "total_events": 0,
                "message": "No audit events in this period"
            }
        
        # Calculate statistics
        by_module = {}
        by_action = {}
        
        for log in logs:
            module = log['module']
            action = log['action_type']
            
            by_module[module] = by_module.get(module, 0) + 1
            by_action[action] = by_action.get(action, 0) + 1
        
        return {
            "period_days": days,
            "total_events": len(logs),
            "by_module": by_module,
            "by_action": by_action,
            "recent_events": logs[:10]  # Last 10 events
        }
    
    def print_audit_report(self, days: int = 7):
        """Print a formatted audit report."""
        report = self.get_audit_report(days)
        
        print(f"\n{'='*60}")
        print(f"Privacy Audit Report - Last {days} Days")
        print(f"{'='*60}")
        
        if report['total_events'] == 0:
            print("\nNo activity recorded in this period.")
            return
        
        print(f"\nTotal Events: {report['total_events']}")
        
        print(f"\n📊 Events by Module:")
        for module, count in sorted(report['by_module'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {module}: {count}")
        
        print(f"\n📋 Events by Action:")
        for action, count in sorted(report['by_action'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {action}: {count}")
        
        print(f"\n🕒 Recent Events:")
        for event in report['recent_events']:
            print(f"\n  {event['timestamp']}")
            print(f"  {event['module']} → {event['action_type']}")
            if event.get('details'):
                print(f"  Details: {event['details']}")
    
    def close(self):
        """Close database connection."""
        self.db.close()


if __name__ == "__main__":
    auditor = PrivacyAuditor()
    auditor.print_audit_report(days=30)
    auditor.close()
