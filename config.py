"""
Configuration management for Privacy-First Personal Agent.
All settings are local-only with privacy-first defaults.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = DATA_DIR / "database"
LOGS_DIR = DATA_DIR / "logs"
EXPORTS_DIR = DATA_DIR / "exports"

# Ensure directories exist
for directory in [DATA_DIR, DB_DIR, LOGS_DIR, EXPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Database Configuration
DATABASE_PATH = DB_DIR / "agent_data.db"
DATABASE_ENCRYPTION_KEY_NAME = "privacy_agent_db_key"

# Ollama Configuration (Local LLM)
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2:3b"  # Lightweight model, can be changed
ALTERNATIVE_MODELS = [
    "phi3:mini",      # Even lighter alternative
    "llama3.2:1b",    # Smallest option
    "mistral:7b",     # More capable but heavier
]

# Privacy Settings
DATA_RETENTION_DAYS = {
    "journal": 365,      # Keep journal entries for 1 year by default
    "finance": 730,      # Keep financial data for 2 years
    "documents": 180,    # Keep analyzed documents for 6 months
    "audit_logs": 90,    # Keep privacy audit logs for 3 months
}

AUTO_DELETE_ENABLED = False  # User must explicitly enable auto-deletion
EXPORT_FORMAT = "json"       # Options: json, csv

# Encryption Settings
ENCRYPTION_ALGORITHM = "Fernet"
KEY_DERIVATION_ITERATIONS = 100000
SALT_LENGTH = 32

# Journal Module Configuration
JOURNAL_CONFIG = {
    "sentiment_threshold_positive": 0.3,
    "sentiment_threshold_negative": -0.3,
    "pattern_lookback_days": 30,
    "mood_categories": ["very_negative", "negative", "neutral", "positive", "very_positive"],
    "trigger_words": [
        "anxious", "depressed", "overwhelmed", "stressed", "panic",
        "lonely", "hopeless", "worthless", "exhausted", "angry"
    ]
}

# Finance Module Configuration
FINANCE_CONFIG = {
    "default_categories": [
        "Food & Dining",
        "Transportation",
        "Shopping",
        "Entertainment",
        "Bills & Utilities",
        "Healthcare",
        "Education",
        "Income",
        "Transfer",
        "Other"
    ],
    "bank_sms_patterns": {
        # Common patterns for Indian banks
        "transaction": r"(?:Rs\.?|INR|₹)\s*([\d,]+\.?\d*)",
        "date": r"(\d{2}[/-]\d{2}[/-]\d{4}|\d{2}-[A-Z]{3}-\d{2})",
        "account": r"(?:a\/c|account|A\/C)\s*(?:XX|xx)?(\d+)",
        "merchant": r"(?:at|to|from)\s+([A-Z\s]+?)(?:\s+on|\s+dated|\.|\,)"
    },
    "budget_alert_threshold": 0.9,  # Alert when 90% of budget spent
}

# Document Module Configuration
DOCUMENT_CONFIG = {
    "max_file_size_mb": 50,
    "supported_formats": [".txt", ".pdf", ".docx", ".doc", ".rtf"],
    "pii_entities": ["PERSON", "ORG", "GPE", "DATE", "MONEY", "CARDINAL"],
    "summary_max_length": 500,
    "chunk_size": 1000,  # For processing large documents
}

# NLP Settings
NLP_CONFIG = {
    "spacy_model": "en_core_web_sm",  # Lightweight model
    "use_gpu": False,  # Set to True if GPU available
    "max_context_length": 2048,
}

# Web Interface Configuration (Optional)
WEB_CONFIG = {
    "host": "127.0.0.1",  # Localhost only for security
    "port": 5000,
    "debug": False,
    "secret_key": os.environ.get("SECRET_KEY", os.urandom(24).hex()),
    "session_timeout_minutes": 30,
}

# Logging Configuration
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": LOGS_DIR / "agent.log",
    "max_bytes": 10 * 1024 * 1024,  # 10 MB
    "backup_count": 5,
}

# Privacy Audit Configuration
AUDIT_CONFIG = {
    "log_all_queries": True,
    "log_data_access": True,
    "log_llm_requests": True,
    "anonymize_logs": False,  # Keep full logs for user transparency
}

# Feature Flags
FEATURES = {
    "journal_enabled": True,
    "finance_enabled": True,
    "document_enabled": True,
    "web_ui_enabled": True,
    "llm_enabled": True,  # Can disable if Ollama not available
}

def get_config():
    """Return all configuration as a dictionary."""
    return {
        "database": {
            "path": str(DATABASE_PATH),
            "encryption_key_name": DATABASE_ENCRYPTION_KEY_NAME,
        },
        "ollama": {
            "base_url": OLLAMA_BASE_URL,
            "model": DEFAULT_MODEL,
        },
        "privacy": DATA_RETENTION_DAYS,
        "features": FEATURES,
    }

if __name__ == "__main__":
    # Print configuration for verification (excluding sensitive data)
    print("Privacy-First Personal Agent Configuration")
    print("=" * 50)
    print(f"Base Directory: {BASE_DIR}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Database Path: {DATABASE_PATH}")
    print(f"Default LLM Model: {DEFAULT_MODEL}")
    print(f"\nFeatures Enabled:")
    for feature, enabled in FEATURES.items():
        print(f"  - {feature}: {'✓' if enabled else '✗'}")
