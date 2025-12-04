"""
Command-Line Interface for Privacy-First Personal Agent.
Interactive menu system for all agent features.
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path
from colorama import init, Fore, Style
init()

from agent import PrivacyAgent
from utils import color_text, format_currency, create_table


def print_header():
    """Print application header."""
    print("\n" + "="*60)
    print(color_text("🔒 PRIVACY-FIRST PERSONAL AGENT 🔒", "cyan"))
    print(color_text("100% Local • Zero Cloud • Maximum Privacy", "yellow"))
    print("="*60 + "\n")


def print_menu():
    """Print main menu."""
    print(color_text("\n📋 MAIN MENU:", "cyan"))
    print("  1. 📓 Journal Module")
    print("  2. 💰 Finance Module")
    print("  3. 📄 Document Module")
    print("  4. 🔍 Privacy Audit")
    print("  5. 📊 System Status")
    print("  6. 💾 Export Data")
    print("  0. ❌ Exit")


def journal_menu(agent: PrivacyAgent):
    """Journal module submenu."""
    while True:
        print(color_text("\n📓 JOURNAL MODULE:", "cyan"))
        print("  1. Add new entry")
        print("  2. View recent entries")
        print("  3. Mood trends")
        print("  4. Get insights")
        print("  0. Back to main menu")
        
        choice = input(color_text("\nChoice: ", "yellow"))
        
        if choice == "1":
            print(color_text("\n✍️ New Journal Entry", "green"))
            print("(Type your entry, press Enter twice when done)")
            
            lines = []
            while True:
                line = input()
                if line == "":
                    break
                lines.append(line)
            
            content = "\n".join(lines)
            if content.strip():
                tags_input = input("\nTags (comma-separated, optional): ")
                tags = [t.strip() for t in tags_input.split(",")] if tags_input else None
                
                result = agent.add_journal_entry(content, tags)
                
                if 'error' not in result:
                    print(color_text(f"\n✓ Entry saved!", "green"))
                    print(f"Mood: {result['mood_category']}")
                    print(f"Sentiment: {result['sentiment_score']:.3f}")
                    print(f"\n{result['feedback']}")
                    
                    if 'llm_analysis' in result and 'insight' in result['llm_analysis']:
                        print(color_text(f"\n💡 AI Insight:", "cyan"))
                        print(f"  {result['llm_analysis']['insight']}")
                else:
                    print(color_text(f"\n✗ Error: {result['error']}", "red"))
        
        elif choice == "2":
            days = input("\nDays to look back (default 7): ")
            days = int(days) if days.isdigit() else 7
            
            entries = agent.get_journal_entries(days=days)
            
            if entries:
                print(color_text(f"\n📖 Last {len(entries)} entries:", "cyan"))
                for entry in entries[:10]:  # Show last 10
                    timestamp = datetime.fromisoformat(entry['timestamp'])
                    print(f"\n{timestamp.strftime('%Y-%m-%d %H:%M')} | {entry['mood_category']}")
                    print(f"  {entry['content'][:100]}...")
            else:
                print(color_text("\nNo entries found.", "yellow"))
        
        elif choice == "3":
            days = input("\nDays to analyze (default 30): ")
            days = int(days) if days.isdigit() else 30
            
            trends = agent.get_mood_trends(days=days)
            
            if 'error' not in trends and trends.get('total_entries', 0) > 0:
                print(color_text(f"\n📊 Mood Trends (last {days} days):", "cyan"))
                print(f"Total entries: {trends['total_entries']}")
                print(f"Average sentiment: {trends['average_sentiment']:.3f}")
                print(f"\nMood Distribution:")
                for mood, count in trends.get('mood_distribution', {}).items():
                    print(f"  {mood}: {count}")
            else:
                print(color_text("\nNo data available yet.", "yellow"))
        
        elif choice == "4":
            days = input("\nDays to analyze (default 30): ")
            days = int(days) if days.isdigit() else 30
            
            insights = agent.get_journal_insights(days=days)
            print(color_text(f"\n💡 Insights:", "cyan"))
            print(f"  {insights}")
        
        elif choice == "0":
            break


def finance_menu(agent: PrivacyAgent):
    """Finance module submenu."""
    while True:
        print(color_text("\n💰 FINANCE MODULE:", "cyan"))
        print("  1. Add transaction from SMS")
        print("  2. Add transaction manually")
        print("  3. View recent transactions")
        print("  4. Spending summary")
        print("  5. Get insights")
        print("  6. Set budget")
        print("  0. Back to main menu")
        
        choice = input(color_text("\nChoice: ", "yellow"))
        
        if choice == "1":
            print(color_text("\n📱 Paste SMS text:", "cyan"))
            sms = input()
            
            result = agent.add_transaction_from_sms(sms)
            
            if 'error' not in result:
                print(color_text(f"\n✓ Transaction added!", "green"))
                print(f"Amount: {format_currency(result['amount'])}")
                print(f"Type: {result['type']}")
                print(f"Category: {result['category']}")
            else:
                print(color_text(f"\n✗ {result['error']}", "red"))
        
        elif choice == "2":
            print(color_text("\n➕ Manual Transaction:", "cyan"))
            amount = float(input("Amount: "))
            txn_type = input("Type (debit/credit): ").lower()
            merchant = input("Merchant (optional): ") or None
            category = input("Category (optional): ") or None
            
            result = agent.add_transaction(
                amount=amount,
                transaction_type=txn_type,
                merchant=merchant,
                category=category
            )
            
            if 'error' not in result:
                print(color_text(f"\n✓ Transaction added!", "green"))
                print(f"Category: {result['category']}")
            else:
                print(color_text(f"\n✗ {result['error']}", "red"))
        
        elif choice == "3":
            days = input("\nDays to look back (default 30): ")
            days = int(days) if days.isdigit() else 30
            
            transactions = agent.get_transactions(days=days)
            
            if transactions:
                print(color_text(f"\n💳 Last {len(transactions)} transactions:", "cyan"))
                
                rows = []
                for txn in transactions[:20]:  # Show last 20
                    timestamp = datetime.fromisoformat(txn['timestamp'])
                    rows.append([
                        timestamp.strftime('%Y-%m-%d'),
                        format_currency(txn['amount']),
                        txn['transaction_type'],
                        txn.get('category', 'N/A'),
                        (txn.get('merchant') or 'N/A')[:20]
                    ])
                
                print(create_table(
                    ["Date", "Amount", "Type", "Category", "Merchant"],
                    rows
                ))
            else:
                print(color_text("\nNo transactions found.", "yellow"))
        
        elif choice == "4":
            days = input("\nDays to analyze (default 30): ")
            days = int(days) if days.isdigit() else 30
            
            summary = agent.get_spending_summary(days=days)
            
            if 'error' not in summary:
                print(color_text(f"\n📊 Spending Summary (last {days} days):", "cyan"))
                print(f"Total Spent: {format_currency(summary['total_spent'])}")
                print(f"Total Income: {format_currency(summary['total_income'])}")
                print(f"Net: {format_currency(summary['net'])}")
                print(f"\nTop Categories:")
                for cat in summary.get('top_categories', []):
                    print(f"  {cat['category']}: {format_currency(cat['total'])}")
            else:
                print(color_text(f"\n✗ {summary['error']}", "red"))
        
        elif choice == "5":
            days = input("\nDays to analyze (default 30): ")
            days = int(days) if days.isdigit() else 30
            
            insights = agent.get_finance_insights(days=days)
            print(color_text(f"\n💡 Insights:", "cyan"))
            print(f"  {insights}")
        
        elif choice == "6":
            category = input("\nCategory: ")
            limit = float(input("Monthly limit: "))
            agent.set_budget(category, limit)
            print(color_text(f"\n✓ Budget set for {category}: {format_currency(limit)}", "green"))
        
        elif choice == "0":
            break


def document_menu(agent: PrivacyAgent):
    """Document module submenu."""
    while True:
        print(color_text("\n📄 DOCUMENT MODULE:", "cyan"))
        print("  1. Process new document")
        print("  2. View processed documents")
        print("  3. Ask question about document")
        print("  4. Search documents")
        print("  0. Back to main menu")
        
        choice = input(color_text("\nChoice: ", "yellow"))
        
        if choice == "1":
            file_path = input("\nDocument file path: ")
            
            result = agent.process_document(file_path)
            
            if 'error' not in result:
                print(color_text(f"\n✓ Document processed!", "green"))
                print(f"File: {result['filename']}")
                print(f"Text length: {result['text_length']} characters")
                
                if result.get('summary'):
                    print(color_text("\n📝 Summary:", "cyan"))
                    print(f"  {result['summary']}")
                
                if result.get('entities'):
                    print(color_text(f"\n🏷️ Entities found: {len(result['entities'])}", "cyan"))
                    print(f"  {', '.join(result['entities'][:10])}")
            else:
                print(color_text(f"\n✗ {result['error']}", "red"))
        
        elif choice == "2":
            documents = agent.get_documents(limit=50)
            
            if documents:
                print(color_text(f"\n📚 Processed Documents ({len(documents)}):", "cyan"))
                for i, doc in enumerate(documents[:20], 1):
                    print(f"\n{i}. [{doc['id']}] {doc['filename']}")
                    print(f"   Processed: {doc['processed_at'][:10]}")
                    if doc.get('summary'):
                        print(f"   Summary: {doc['summary'][:80]}...")
            else:
                print(color_text("\nNo documents processed yet.", "yellow"))
        
        elif choice == "3":
            doc_id = int(input("\nDocument ID: "))
            question = input("Your question: ")
            
            answer = agent.query_document(doc_id, question)
            print(color_text(f"\n💭 Answer:", "cyan"))
            print(f"  {answer}")
        
        elif choice == "4":
            query = input("\nSearch query: ")
            results = agent.search_documents(query)
            
            if results:
                print(color_text(f"\n🔍 Found {len(results)} documents:", "cyan"))
                for doc in results[:10]:
                    print(f"\n[{doc['id']}] {doc['filename']}")
                    if doc.get('summary'):
                        print(f"  {doc['summary'][:100]}...")
            else:
                print(color_text("\nNo matching documents found.", "yellow"))
        
        elif choice == "0":
            break


def main():
    """Main CLI application."""
    print_header()
    
    # Initialize agent
    try:
        agent = PrivacyAgent()
    except Exception as e:
        print(color_text(f"✗ Failed to initialize agent: {e}", "red"))
        return
    
    try:
        while True:
            print_menu()
            choice = input(color_text("\nChoice: ", "yellow"))
            
            if choice == "1":
                journal_menu(agent)
            
            elif choice == "2":
                finance_menu(agent)
            
            elif choice == "3":
                document_menu(agent)
            
            elif choice == "4":
                days = input("\nDays to look back (default 7): ")
                days = int(days) if days.isdigit() else 7
                
                logs = agent.get_privacy_audit(days=days)
                
                if logs:
                    print(color_text(f"\n🔍 Privacy Audit Log ({len(logs)} events):", "cyan"))
                    for log in logs[:20]:
                        print(f"\n{log['timestamp']} | {log['module']} | {log['action_type']}")
                        print(f"  Details: {log['details']}")
                else:
                    print(color_text("\nNo audit logs found.", "yellow"))
            
            elif choice == "5":
                status = agent.get_system_status()
                
                print(color_text("\n📊 SYSTEM STATUS:", "cyan"))
                print(f"LLM Available: {'✓' if status['llm_available'] else '✗'}")
                print(f"\nEnabled Modules:")
                for module, enabled in status['modules'].items():
                    print(f"  {module}: {'✓' if enabled else '✗'}")
                print(f"\nStatistics:")
                for key, value in status.get('statistics', {}).items():
                    print(f"  {key}: {value}")
            
            elif choice == "6":
                export_path = agent.export_data()
                print(color_text(f"\n✓ Data exported to: {export_path}", "green"))
            
            elif choice == "0":
                print(color_text("\nThank you for using Privacy-First Personal Agent!", "cyan"))
                print(color_text("Your data stays private and secure on your device. 🔒", "yellow"))
                break
    
    finally:
        agent.close()


if __name__ == "__main__":
    main()
