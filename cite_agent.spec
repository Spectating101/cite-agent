# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Cite Agent Windows installer.
This bundles Python + all dependencies into a single executable.
"""

import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collect all cite_agent submodules
cite_agent_datas, cite_agent_binaries, cite_agent_hiddenimports = collect_all('cite_agent')

# Additional hidden imports for dependencies
hidden_imports = [
    'cite_agent',
    'cite_agent.cli',
    'cite_agent.enhanced_ai_agent',
    'cite_agent.workflow',
    'cite_agent.query_cache',
    'cite_agent.response_validation',
    'cite_agent.setup_config',
    'cite_agent.telemetry',
    'cite_agent.updater',
    'cite_agent.cli_workflow',
    'cite_agent.session_manager',
    'aiohttp',
    'groq',
    'openai',
    'requests',
    'dotenv',
    'pydantic',
    'rich',
    'keyring',
    'ddgs',
    'asyncio',
    'json',
    'hashlib',
    'platform',
    'pathlib',
    'argparse',
    'ssl',
    'certifi',
]

# Extend with collected imports
hidden_imports.extend(cite_agent_hiddenimports)

# Analysis
a = Analysis(
    ['cite_agent/cli.py'],
    pathex=[],
    binaries=cite_agent_binaries,
    datas=cite_agent_datas + [
        ('README.md', '.'),
        ('LICENSE', '.') if os.path.exists('LICENSE') else (),
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'sklearn',
        'PIL',
        'cv2',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Create PYZ archive
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='cite-agent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Console app, not GUI
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)

# Also create a one-folder distribution (faster to start, easier to debug)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='cite-agent',
)
