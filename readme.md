# 🚀 Cite-Agent - Quick Start

**Version:** 1.5.7  
**What is this?** AI research assistant for your terminal

---

## 📥 Installation (Windows)

### Easy Way: Just Double-Click!

1. **Double-click** `Click-this-one.bat`
2. **Wait** 2-3 minutes while it installs
3. **Done!** Open Command Prompt and type: `cite-agent`

That's it!

---

## 📋 What's in This Folder

- **`Click-this-one.bat`** ← Start here! Double-click to install
- **`Backend-Installer.ps1`** - The actual installer (runs automatically)
- **`readme.md`** - This file
- **`Feedback-Form.html`** - Share your thoughts after trying it!

---

## ✨ What You Can Do

Once installed, open **Command Prompt** or **PowerShell** and try:

```bash
# Search academic papers
cite-agent "Find papers on neural networks"

# Get financial data
cite-agent "What's Tesla's revenue?"

# Analyze data
cite-agent "Load data.csv and show summary"

# Quick facts
cite-agent "What is the capital of France?"
```

---

## 🎯 Features

- **200M+ academic papers** - Search Semantic Scholar, OpenAlex, PubMed
- **Live financial data** - Stock prices, earnings, SEC filings
- **Data analysis** - Load CSV/Excel, get instant insights
- **Clean output** - Numbers look professional (NEW in v1.5.7!)

---

## 🛠️ Troubleshooting

### "cite-agent is not recognized"
**Fix:** Close and reopen your terminal (Command Prompt/PowerShell)

### Still not working?
**Option 1:** Right-click `Backend-Installer.ps1` → Run with PowerShell

**Option 2:** Open PowerShell as Admin and run:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try `Click-this-one.bat` again.

---

## 📊 What's New in v1.5.7

**Cleaner output formatting:**
- Numbers display properly (120 not 120.0000)
- Large numbers use commas (1,234,567)
- No LaTeX notation artifacts
- No stray markdown backticks

**Before:** `Mean: 120.0000, Total: 1234567`  
**After:** `Mean: 120, Total: 1,234,567`

---

## 💬 Feedback

We'd love to hear what you think! After trying Cite-Agent, please fill out our quick feedback form: **`Feedback-Form.html`** (just double-click to open)

---

## 🔗 More Info

- **GitHub:** https://github.com/Spectating101/cite-agent
- **PyPI:** https://pypi.org/project/cite-agent/
- **Issues:** https://github.com/Spectating101/cite-agent/issues

---

**Questions?** Open an issue on GitHub or contact us!

**Enjoy!** 🎉
