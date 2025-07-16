# raidassist.spec - Enhanced PyInstaller configuration for RaidAssist
# Updated for enhanced version with new logging, error handling, and overlay systems
block_cipher = None

a = Analysis(
    ['main.py'],  # Use main.py as entry point instead of ui/interface.py
    pathex=[],
    binaries=[],
    datas=[
        ('assets/*', 'assets'),
        ('api/*', 'api'),
        ('ui/*', 'ui'),
        ('utils/*', 'utils'),  # Include new utils directory
        ('requirements.txt', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtWidgets', 
        'PySide6.QtGui',
        'utils.logging_manager',
        'utils.error_handler',
        'ui.interface',
        'ui.overlay',
        'api.bungie',
        'api.manifest',
        'api.oauth',
        'api.parse_profile',
        'api.exotics',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'PyQt5',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RaidAssist',  # Back to standard name
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Pure GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/raidassist_icon.ico',
    version_file=None,  # Could add version info file later
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RaidAssist'
)
