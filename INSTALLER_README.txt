═══════════════════════════════════════════════════════════════════════
  CITE-AGENT WINDOWS INSTALLER v1.5.1
═══════════════════════════════════════════════════════════════════════

INSTALLATION INSTRUCTIONS
═════════════════════════

1. Extract this ZIP file to any location
2. Double-click "CLICK_THIS_TO_INSTALL.bat"
3. Follow the on-screen prompts
4. Installation completes in ~2-3 minutes

After installation, cite-agent is accessible from any command prompt by
typing: cite-agent


LAUNCHING CITE-AGENT
═══════════════════

Option 1 (Recommended): Command Line
  • Open PowerShell or Command Prompt
  • Type: cite-agent
  • Press Enter

Option 2: Create Desktop Shortcut Manually
  If you prefer a desktop icon:
  1. Right-click on Desktop → New → Shortcut
  2. Location: C:\Users\<YourUsername>\AppData\Local\Cite-Agent\venv\Scripts\cite-agent.exe
  3. Name: Cite-Agent
  4. Click Finish

Option 3: Run from File Explorer
  • Navigate to: C:\Users\<YourUsername>\AppData\Local\Cite-Agent\venv\Scripts\
  • Double-click: cite-agent.exe


WHAT GETS INSTALLED
═══════════════════

• Python 3.11.9 or uses your existing Python 3.10-3.13
• Virtual environment at: C:\Users\<YourUsername>\AppData\Local\Cite-Agent\
• cite-agent package from PyPI
• PATH updated to include cite-agent command


TROUBLESHOOTING
═══════════════

Installation fails?
  • Check your internet connection
  • Run as Administrator (right-click CLICK_THIS_TO_INSTALL.bat → Run as administrator)
  • Check logs at: C:\Users\<YourUsername>\AppData\Local\Cite-Agent\logs\

cite-agent command not found?
  • Close and reopen your terminal (PATH needs refresh)
  • Or run: $env:Path = [System.Environment]::GetEnvironmentVariable("Path","User")

Need help?
  • GitHub Issues: https://github.com/Spectating101/cite-agent/issues
  • Documentation: https://github.com/Spectating101/cite-agent


UNINSTALLATION
══════════════

To remove cite-agent:
  1. Delete: C:\Users\<YourUsername>\AppData\Local\Cite-Agent\
  2. Remove from PATH:
     - Open: System Properties → Environment Variables
     - Find "Path" in User variables
     - Remove entry containing "Cite-Agent\venv\Scripts"


═══════════════════════════════════════════════════════════════════════
© 2025 Cite-Agent Team | MIT License
═══════════════════════════════════════════════════════════════════════
