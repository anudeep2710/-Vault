# Quick Start Guide

## Installation (5 minutes)

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download spaCy Model
```bash
python -m spacy download en_core_web_sm
```

### 3. Install Ollama (Optional for AI features)
- Visit: https://ollama.ai
- Download and install for your OS
- Pull a model:
```bash
ollama pull llama3.2:3b
```

## First Run

### Option 1: Quick Demo (Recommended)
```bash
python demo.py
```
This will demonstrate all three modules in action!

### Option 2: Interactive CLI
```bash
python cli.py
```
Navigate the menus to explore features.

### Option 3: Python Scripts
```python
from agent import PrivacyAgent

with PrivacyAgent() as agent:
    # Add a journal entry
    agent.add_journal_entry("Feeling great today!")
    
    # Parse a bank SMS
    agent.add_transaction_from_sms("Debited Rs.500 at CAFE")
    
    # Process a document
    agent.process_document("contract.pdf")
```

## Common Tasks

### Add Journal Entry
```bash
python cli.py
# Select: 1 (Journal) → 1 (Add entry) → Type your entry
```

### Parse Bank SMS
```bash
python cli.py
# Select: 2 (Finance) → 1 (SMS) → Paste SMS text
```

### Analyze Document
```bash
python cli.py
# Select: 3 (Documents) → 1 (Process) → Enter file path
```

### View Privacy Audit
```bash
python cli.py
# Select: 4 (Privacy Audit)
```

### Export Your Data
```bash
python cli.py
# Select: 6 (Export Data)
```

## Troubleshooting

**"Module not found"**
```bash
pip install -r requirements.txt
```

**"spaCy model not found"**
```bash
python -m spacy download en_core_web_sm
```

**"Ollama not available"**
- Make sure Ollama is running
- Check: http://localhost:11434
- Pull a model: `ollama pull llama3.2:3b`

**"Database locked"**
- Only run one instance at a time
- Close any running Python processes

## Where is My Data?

All your data is stored locally in:
- `data/database/agent_data.db` (encrypted)
- `data/logs/agent.log` (application logs)
- `data/exports/` (when you export)

## Privacy Tips

✅ **DO:**
- Use full-disk encryption
- Back up your database file
- Export your data regularly
- Review privacy audit logs

❌ **DON'T:**
- Share your encryption keys
- Use on public/shared computers
- Upload database to cloud
- Commit data/ folder to git

## Next Steps

1. ✅ Run `python demo.py` to see all features
2. ✅ Add your first real journal entry
3. ✅ Parse a bank SMS
4. ✅ Review the privacy audit
5. ✅ Explore the CLI menus

## Getting Help

- 📖 Read: [README.md](README.md)
- 💡 Check: [examples/README.md](examples/README.md)
- 🔍 Review: Privacy audit logs for transparency
- 🐛 Issues: Check console output for errors

---

**🔒 Remember: Your data stays private on your device! 🔒**
