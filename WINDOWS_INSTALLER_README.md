# 🪟 Cite-Agent Windows Installer

**Version:** 1.5.7  
**Installer Name:** `Install-CiteAgent-v1.5.7-BULLETPROOF.ps1`  
**Works on:** Any Windows machine (even without Python!)

---

## 📥 Quick Install

### Option 1: One-Line Install (Easiest)

Open PowerShell and run:
```powershell
iwr -useb https://raw.githubusercontent.com/Spectating101/cite-agent/main/Install-CiteAgent-BULLETPROOF.ps1 | iex
```

### Option 2: Download and Run

1. **Download:** [Install-CiteAgent-v1.5.7-BULLETPROOF.ps1](https://github.com/Spectating101/cite-agent/raw/main/Install-CiteAgent-BULLETPROOF.ps1)
2. **Right-click** the file → **Run with PowerShell**
3. **Wait** 2-3 minutes while it installs
4. **Done!** Open Command Prompt or PowerShell and type: `cite-agent`

---

## ✨ What Gets Installed

- ✅ **Python 3.11** (embedded, if you don't have Python)
- ✅ **Cite-Agent v1.5.7** from PyPI
- ✅ **Desktop shortcut** (optional)
- ✅ **Start Menu shortcut** (optional)
- ✅ **PATH setup** (automatic)

**Total size:** ~150MB  
**Install location:** `%LOCALAPPDATA%\Cite-Agent`

---

## 🚀 First Run

After installation, open **Command Prompt** or **PowerShell**:

```bash
# Check version
cite-agent --version
# Should show: cite-agent version 1.5.7

# Try a query
cite-agent "What is the capital of France?"

# Search papers
cite-agent "Find papers on neural networks"

# Get financial data
cite-agent "What's Tesla's revenue?"
```

---

## 🎯 Key Features

### Academic Research
- Search 200M+ papers (Semantic Scholar, OpenAlex, PubMed)
- Get citations, abstracts, DOIs instantly

### Financial Data
- Real-time stock prices, earnings, financial reports
- SEC filings, company metrics

### Data Analysis
- Load CSV/Excel files
- Statistical analysis (correlation, regression, t-tests)
- Clean, formatted output

### Truth-Seeking
- Fact-checking with sources
- Confidence scores
- Multi-language support

---

## 🛠️ Troubleshooting

### "cite-agent is not recognized"
**Fix:** Restart your terminal (Command Prompt or PowerShell)  
**Why:** PATH changes require terminal restart

### "PowerShell execution policy error"
**Fix:** Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Still not working?
Run the verbose installer:
```powershell
.\Install-CiteAgent-BULLETPROOF.ps1 -Verbose
```

Check the log at: `%LOCALAPPDATA%\Cite-Agent\logs\install-*.log`

---

## 🔄 Update to Latest Version

Already have Cite-Agent installed? Update with:

```bash
pip install --upgrade cite-agent
```

Or re-run the installer—it will detect existing installation and upgrade.

---

## 📋 What's New in v1.5.7

### Formatting Improvements ✨
- **Numbers look professional** - no more `.0000` spam
- **Comma separators** for large numbers (1,234,567)
- **No LaTeX notation** in terminal output
- **No stray backticks** from markdown

### Examples

**Before v1.5.7:**
```
Mean: 120.0000, Total: 1234567, Result: $\boxed{42.0}$
```

**After v1.5.7:**
```
Mean: 120, Total: 1,234,567, Result: 42
```

Much cleaner! 🎨

---

## 📚 More Resources

- **Full README:** [README.md](https://github.com/Spectating101/cite-agent)
- **PyPI:** https://pypi.org/project/cite-agent/
- **GitHub:** https://github.com/Spectating101/cite-agent
- **Feedback:** [Open an issue](https://github.com/Spectating101/cite-agent/issues)

---

## 🎓 For Developers

Want to contribute or build from source?

```bash
git clone https://github.com/Spectating101/cite-agent.git
cd cite-agent
pip install -e .
```

See [CONTRIBUTING.md](https://github.com/Spectating101/cite-agent/blob/main/CONTRIBUTING.md) for guidelines.

---

**Questions?** Open an issue on GitHub or check the full documentation!

**Enjoy Cite-Agent v1.5.7!** 🚀
