# Cite Agent Windows Installer Build Guide

## Quick Start (For CCT/Developers)

**Build a Windows installer in 3 commands:**

```batch
# On Windows:
git clone https://github.com/Spectating101/cite-agent
cd cite-agent
build_windows_installer.bat
```

This creates `CiteAgentSetup-1.4.8.exe` - a complete Windows installer.

## What Gets Built

1. **Standalone Executable** - Python + all dependencies bundled
2. **Windows Installer** - Professional .exe with:
   - Desktop shortcut
   - Start menu entry
   - PATH configuration (type `cite-agent` anywhere)
   - Uninstaller in Add/Remove Programs

## Prerequisites

- Windows 10/11
- Python 3.9+ ([python.org](https://python.org))
- NSIS 3.x ([nsis.sourceforge.io](https://nsis.sourceforge.io/Download))

## Build Files

| File | Purpose |
|------|---------|
| `cite_agent.spec` | PyInstaller spec - bundles Python + deps |
| `installer.nsi` | NSIS script - creates Windows installer |
| `EnvVarUpdate.nsh` | NSIS plugin for PATH management |
| `build_windows_installer.bat` | One-click Windows build script |
| `build_installer.py` | Cross-platform Python build script |

## User Experience

**For Professors (Zero Terminal Knowledge Required):**

1. Double-click `CiteAgentSetup-1.4.8.exe`
2. Click "Next" through installer
3. Desktop shortcut appears
4. Double-click shortcut OR type `cite-agent` in any terminal
5. First run auto-launches setup wizard
6. Enter email + password, done!

**Auto-Setup Features:**
- First-run detection auto-launches setup wizard
- No need to remember `--setup` flag
- Credentials saved securely in Windows Credential Manager
- Auto-updates check daily (no manual pip commands)

## Distribution

After building, distribute:

```
CiteAgentSetup-1.4.8.exe  (~50-80 MB)
```

Or for portable use:

```
CiteAgent-1.4.8-portable.zip
```

## Technical Details

### PyInstaller Bundling

The spec file bundles:
- Python 3.x interpreter
- All cite_agent modules
- aiohttp, groq, openai, requests, rich, keyring, ddgs
- SSL certificates (certifi)

Excludes heavy deps not needed:
- tkinter, matplotlib, numpy, pandas, scipy, sklearn

### NSIS Installer Features

- Registry entries for Add/Remove Programs
- PATH modification via EnvVarUpdate
- Desktop and Start Menu shortcuts
- Clean uninstaller
- License agreement screen

### First-Run Auto-Setup

Located in `cite_agent/cli.py`:

```python
def check_first_run():
    # Creates ~/.cite_agent/.first_run_complete marker
    # Checks if auth is configured
    # Auto-launches setup_wizard() if not
```

## Troubleshooting

**PyInstaller fails:**
```
pip install --upgrade pyinstaller
pip install -e .
```

**NSIS not found:**
- Install from [nsis.sourceforge.io](https://nsis.sourceforge.io/Download)
- Add to PATH: `C:\Program Files (x86)\NSIS\Bin`

**Executable won't run:**
- Check Windows Defender isn't blocking
- Run as Administrator once to clear security flags

**Missing DLLs:**
- Run `pip install pywin32` before building
- Ensure Visual C++ Redistributable is installed

## Alternative: Python Build Script

For cross-platform or more control:

```bash
python build_installer.py           # Full build
python build_installer.py --pyinst  # PyInstaller only
python build_installer.py --clean   # Clean build artifacts
```

## Version Management

Update version in these files before building:
- `cite_agent/__init__.py`
- `setup.py`
- `installer.nsi`
- `build_installer.py`

Current version: **1.4.8**

---

**Questions?** Open an issue at [GitHub](https://github.com/Spectating101/cite-agent/issues)
