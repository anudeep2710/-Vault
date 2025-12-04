# 🚀 Setup Instructions

## Current Status
- ✅ Ollama installed
- 🔄 Python dependencies installing...

## Next Steps

### 1. Wait for Dependencies Installation
The current pip install should complete in a few minutes.

### 2. Setup Ollama Model

**Option A: Restart your terminal and run:**
```bash
ollama pull llama3.2:3b
```

**Option B: Use full path (if Ollama not in PATH):**
```bash
# Windows
"C:\Users\%USERNAME%\AppData\Local\Programs\Ollama\ollama.exe" pull llama3.2:3b

# Or try
"%LOCALAPPDATA%\Programs\Ollama\ollama.exe" pull llama3.2:3b
```

**Option C: Start Ollama from Start Menu, then run:**
```bash
ollama pull llama3.2:3b
```

### 3. Install spaCy Model
```bash
python -m spacy download en_core_web_sm
```

### 4. Test the System

**Run the quick demo:**
```bash
python demo.py
```

**Or start the interactive CLI:**
```bash
python cli.py
```

## Troubleshooting

### "ollama: command not found"
1. Close and reopen your terminal/PowerShell
2. Or restart your computer (Ollama updates PATH)
3. Or use the full path to ollama.exe (see Option B above)

### Check Ollama Status
Open browser: http://localhost:11434
- If you see "Ollama is running", it's working!

### Verify Installation
```bash
python -c "import textblob; print('✓ textblob installed')"
python -c "import spacy; print('✓ spacy installed')"
```

## What to Expect

### With Ollama + Model:
- 🤖 AI-powered mood insights
- 🎯 Smart transaction categorization
- 📝 Document summarization
- 💬 Q&A over documents

### Without Ollama (Still Works!):
- ✅ Sentiment analysis (TextBlob)
- ✅ Rule-based categorization
- ✅ Entity extraction (spaCy)
- ✅ All core features

## Quick Test Commands

```bash
# 1. Test basic functionality (no LLM needed)
python test_basic.py

# 2. Test journal module
python examples/demo_journal.py

# 3. Test finance module
python examples/demo_finance.py

# 4. Test document module
python examples/demo_document.py

# 5. Full interactive demo
python demo.py

# 6. Start using the agent
python cli.py
```

## Expected Output

When everything works, you'll see:
```
🔒 PRIVACY-FIRST PERSONAL AGENT - QUICK DEMO
============================================================

✓ LLM Available (if Ollama running)
✓ Modules: journal, finance, documents
✓ All features working
```

## Need Help?

1. **Dependencies not installing?**
   - Try: `pip install --upgrade pip`
   - Then run the install command again

2. **Ollama not starting?**
   - Check Task Manager for "Ollama" process
   - Try starting from Start Menu

3. **Want to skip Ollama for now?**
   - The system works fine without it!
   - Just run `python demo.py` - it will use fallback processing

## Privacy Reminder
- ✅ All your data stays on your device
- ✅ Ollama runs locally (localhost only)
- ✅ No external API calls
- ✅ Complete privacy guaranteed

---

**Ready to start? Run:** `python demo.py`
