# 📦 Cite-Agent Windows Installer Options

Two installer packages are available for Windows users. Choose based on your needs:

---

## Option 1: Online Installer (Recommended) ⚡

**File**: `cite-agent-windows-installer.zip` **(8.7 KB)**

### ✅ Advantages
- **Tiny download** - Only 8.7 KB
- **Always latest** - Downloads newest cite-agent from PyPI
- **Fast** - Quick to download and start
- **Easy updates** - Just re-run to update

### ⚠️ Requirements
- **Internet connection required** during installation
- Downloads ~130 MB of Python + dependencies

### 📥 What It Contains
- `Install-CiteAgent-BULLETPROOF.ps1` - PowerShell installer script
- `INSTALLER_README.md` - Instructions

### 🚀 Installation Steps
1. Extract `cite-agent-windows-installer.zip`
2. Right-click `Install-CiteAgent-BULLETPROOF.ps1` → Run with PowerShell
3. Installer auto-downloads Python 3.11.9 (if needed) + cite-agent + dependencies
4. Done! Desktop shortcut created

### ⏱️ Installation Time
- **With internet**: 3-5 minutes
- **Downloads**: ~130 MB total

---

## Option 2: Offline Installer (No Internet Needed) 📦

**File**: `cite-agent-windows-offline-installer.zip` **(120 MB)**

### ✅ Advantages
- **No internet required** - Works completely offline
- **Bundled everything** - Python + cite-agent + all 65 dependencies
- **Reliable** - No download failures
- **Air-gapped systems** - Works on isolated networks

### ⚠️ Trade-offs
- **Large download** - 120 MB (vs 8.7 KB online)
- **Fixed version** - cite-agent 1.4.8 bundled
- **Slower download** - Bigger file to transfer

### 📥 What It Contains
- `Install-CiteAgent-OFFLINE.ps1` - Offline installer script
- `Install-CiteAgent-OFFLINE.bat` - Double-click launcher
- `python-embed.zip` - Python 3.11.9 embedded (~30 MB)
- `get-pip.py` - pip installer
- `packages/` - All 65 Python packages (~97 MB)
  - cite-agent 1.4.8
  - pandas, numpy, scipy, scikit-learn
  - groq, openai, aiohttp
  - rich, plotext
  - ...and 56 more dependencies
- `README-OFFLINE.txt` - Offline-specific instructions

### 🚀 Installation Steps
1. Extract `cite-agent-windows-offline-installer.zip`
2. Double-click `Install-CiteAgent-OFFLINE.bat`
3. Installer uses bundled Python + packages (no download)
4. Done! Desktop shortcut created

### ⏱️ Installation Time
- **Without internet**: 2-3 minutes
- **Downloads**: 0 MB (everything bundled)

---

## Comparison Table

| Feature | Online Installer | Offline Installer |
|---------|-----------------|-------------------|
| **Download Size** | 8.7 KB | 120 MB |
| **Internet Required** | ✅ Yes (during install) | ❌ No |
| **Installation Time** | 3-5 min | 2-3 min |
| **cite-agent Version** | Latest from PyPI | 1.4.8 (bundled) |
| **Updates** | Easy (re-run) | Manual (new package) |
| **Use Case** | Most users | Air-gapped systems |

---

## Which Should You Choose?

### ✅ Choose **Online Installer** if:
- You have internet connection
- You want the latest version
- You want easy updates
- You want a tiny download

### ✅ Choose **Offline Installer** if:
- No internet during installation
- Working on air-gapped/isolated systems
- Company firewall blocks PyPI
- Want guaranteed installation success

---

## Both Installers Provide

✅ Python 3.11.9 (auto-installed or bundled)
✅ cite-agent with all dependencies
✅ Desktop shortcut
✅ Start Menu entry
✅ PATH configuration (type `cite-agent` anywhere)
✅ No admin rights needed
✅ Works on Windows 10 & 11

---

## Testing Results

Both installers have been tested and verified:

| Machine | OS | Installer | Result |
|---------|----|-----------| -------|
| 100.78.102.111 | Windows 11 | Online | ✅ Success |
| 100.92.237.90 | Windows 10 | Online | ✅ Success |
| Local Test | Windows 11 | Offline | ✅ Success |

---

## Download Links

**Online Installer** (8.7 KB):
- GitHub: `cite-agent-windows-installer.zip`
- Direct: [Download from Releases]

**Offline Installer** (120 MB):
- GitHub: `cite-agent-windows-offline-installer.zip`
- Direct: [Download from Releases]

---

## Support

Having issues? Check:
1. **INSTALLER_README.md** - Detailed instructions
2. **README-OFFLINE.txt** - Offline-specific help
3. **GitHub Issues**: https://github.com/Spectating101/cite-agent/issues

---

**Recommendation**: Most users should use the **Online Installer** (8.7 KB) for convenience. Use the **Offline Installer** (120 MB) only if you specifically need offline installation.

---

**Last Updated**: 2025-11-18
**cite-agent Version**: 1.4.9
**Python Version**: 3.11.9
**Platforms**: Windows 10, Windows 11 (64-bit)
