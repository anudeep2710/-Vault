# 🔒 Privacy-First Personal Agent

> **100% Local • Zero Cloud • Maximum Privacy**

A privacy-first intelligent agent that processes highly sensitive personal data entirely on-device. Your financial records, health journals, and legal documents never leave your computer.

## 🌟 Features

### 📓 Mental Health Journaling
- **Mood Analysis**: Automatic sentiment analysis using TextBlob
- **Pattern Detection**: Identify mood trends over time
- **Trigger Detection**: Recognize concerning patterns
- **AI Insights**: Local LLM analyzes your entries (optional)
- **Complete Privacy**: Your thoughts stay on your device

### 💰 Finance Tracker
- **SMS Parsing**: Extract transactions from bank notifications
- **Auto-Categorization**: Smart spending categorization
- **Budget Tracking**: Set and monitor budgets
- **Spending Insights**: Analyze patterns and get recommendations
- **Bank-Level Privacy**: Financial data encrypted at rest

### 📄 Document Analyzer
- **Multi-Format Support**: PDF, DOCX, TXT
- **Entity Extraction**: Identify names, dates, amounts, addresses
- **Summarization**: Generate concise summaries
- **Q&A**: Ask questions about your documents
- **Legal-Grade Privacy**: Documents never uploaded to cloud

## 🔐 Privacy Guarantees

- ✅ **100% Local Processing**: All computation on your device
- ✅ **Encrypted Storage**: AES encryption for all sensitive data
- ✅ **No Network Calls**: Except to localhost Ollama (optional)
- ✅ **Privacy Audit**: Full transparency log of all data access
- ✅ **Data Portability**: Export all your data anytime
- ✅ **Secure Deletion**: Proper data wiping on deletion

## 📋 Requirements

- **Python**: 3.8 or higher
- **RAM**: 4-8GB (for local LLM, optional)
- **Storage**: 2-5GB (for models and data)
- **OS**: Windows, macOS, or Linux

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download this repository
cd "c:/Users/anude/Pictures/claude challenge"

# Run setup (installs dependencies and initializes database)
python setup.py
```

### 2. Install Ollama (Optional but Recommended)

For AI-powered insights, install Ollama:

```bash
# Visit https://ollama.ai and install
# Then pull a lightweight model:
ollama pull llama3.2:3b
```

> **Note**: The agent works without Ollama using rule-based processing, but LLM features enhance insights significantly.

### 3. Run the Agent

```bash
python cli.py
```

## 💡 Usage Examples

### Journal Entry
```
📓 New Journal Entry
> Had a productive day at work. Feeling accomplished but a bit tired.

✓ Entry saved!
Mood: positive
Sentiment: 0.450
Feedback: Glad to see you're in a good place. Keep up the positive energy!
```

### SMS Transaction Parsing
```
💰 Add Transaction from SMS
> Your A/C XX1234 debited with Rs.450.50 at COFFEE SHOP on 04-12-24

✓ Transaction added!
Amount: ₹450.50
Type: debit
Category: Food & Dining
```

### Document Analysis
```
📄 Process Document
> /path/to/contract.pdf

✓ Document processed!
Summary: This agreement outlines consulting services...
Entities: John Smith, Acme Corporation, $50,000, December 1, 2024
```

## 📊 Features Overview

| Module | Features | Privacy Level |
|--------|----------|---------------|
| **Journal** | Mood tracking, sentiment analysis, pattern detection | 🔒🔒🔒 Maximum |
| **Finance** | SMS parsing, categorization, budgets, insights | 🔒🔒🔒 Maximum |
| **Documents** | PDF/DOCX processing, NER, summarization, Q&A | 🔒🔒🔒 Maximum |

## 🏗️ Architecture

```
Privacy-First Agent
├── Core Infrastructure
│   ├── config.py          # Configuration management
│   ├── encryption.py      # Fernet encryption + keyring
│   ├── database.py        # Encrypted SQLite storage
│   ├── llm_handler.py     # Local Ollama integration
│   └── utils.py           # Helper utilities
├── Modules
│   ├── journal/           # Mental health journaling
│   ├── finance/           # Financial tracking
│   └── documents/         # Document analysis
├── Interfaces
│   ├── cli.py             # Command-line interface
│   └── agent.py           # Main orchestrator
└── Data (Auto-created)
    ├── database/          # Encrypted SQLite DB
    ├── logs/              # Application logs
    └── exports/           # Data exports
```

## 🔧 Configuration

Edit `config.py` to customize:

```python
# LLM Model (choose based on your hardware)
DEFAULT_MODEL = "llama3.2:3b"  # Lightweight
# DEFAULT_MODEL = "llama3.2:1b"  # Even lighter
# DEFAULT_MODEL = "mistral:7b"   # More capable

# Data Retention (days)
DATA_RETENTION_DAYS = {
    "journal": 365,
    "finance": 730,
    "documents": 180,
}

# Auto-delete old data
AUTO_DELETE_ENABLED = False  # Set to True to enable
```

## 🛡️ Security Features

### Encryption
- **Algorithm**: Fernet (symmetric encryption)
- **Key Storage**: System keyring (encrypted)
- **Key Derivation**: PBKDF2 with 100,000 iterations
- **Data-at-Rest**: All sensitive data encrypted in SQLite

### Privacy Audit
- Every data access is logged
- View audit trail: `Privacy Audit` menu in CLI
- Logs include: module, action, timestamp, details
- Full transparency of what the agent does

### Data Export
- Export all your data: JSON format
- GDPR-style data portability
- No vendor lock-in
- Easy backup and migration

## 📱 Privacy Audit Log Example

```
2024-12-04 18:30:15 | journal | add_entry
  Details: {"length": 142}

2024-12-04 18:31:22 | finance | add_transaction
  Details: {"amount": 450.5, "category": "Food & Dining"}

2024-12-04 18:32:10 | documents | add_document
  Details: {"filename": "contract.pdf"}
```

## 🎯 Use Cases

### Mental Health Professional
Track client mood patterns without HIPAA concerns (all local).

### Freelancer / Independent Contractor
Analyze contracts and financial documents privately.

### Privacy-Conscious Individual
Journal, track finances, manage documents without Big Tech.

### Research / Academic
Process sensitive research data on-device.

## 🚨 Troubleshooting

### "Ollama not available"
```bash
# Install Ollama: https://ollama.ai
# Start Ollama service
# Pull a model:
ollama pull llama3.2:3b
```

### "spaCy model not found"
```bash
python -m spacy download en_core_web_sm
```

### "Database locked"
Make sure only one instance of the agent is running.

### Performance Issues
- Use a lighter model: `llama3.2:1b` or `phi3:mini`
- Disable LLM features in `config.py`: `FEATURES['llm_enabled'] = False`
- Close other applications to free RAM

## 📝 License

MIT License - See LICENSE file

## 🤝 Contributing

This is a privacy-first project. Contributions welcome, but must maintain:
1. Zero cloud dependencies
2. Local-only processing
3. End-to-end encryption
4. Full transparency

## ⚠️ Disclaimer

This agent aims to provide maximum privacy, but:
- Ensure your device is secure (disk encryption, strong password)
- Back up your encryption keys safely
- Use at your own risk for sensitive data
- This is not a substitute for professional mental health care

## 🌐 Resources

- [Ollama](https://ollama.ai) - Local LLM runtime
- [spaCy](https://spacy.io) - NLP library
- [Fernet](https://cryptography.io) - Encryption
- [SQLCipher](https://www.zetetic.net/sqlcipher/) - Encrypted SQLite

## 📧 Support

For issues or questions:
1. Check the troubleshooting section
2. Review privacy audit logs
3. Export your data for safekeeping

---

<div align="center">

**🔒 Your Data. Your Device. Your Privacy. 🔒**

*Built with privacy as the foundation, not an afterthought.*

</div>
