# -*- mode: python ; coding: utf-8 -*-
import os
import customtkinter

block_cipher = None
ctk_path = os.path.dirname(customtkinter.__file__)

added_files = [
    ('ip_lists', 'ip_lists'),
    ('assets/warpgate.ico', 'assets'),
    ('assets/warpgate_logo.png', 'assets'),
    ('LOGO_SMALL_APPLICATION.ico', '.'),
    (ctk_path, 'customtkinter')
]

a = Analysis(
    ['modern_app.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'customtkinter',
        'pythonping',
        'win32com.client',
        'requests',
        'PIL',
        'PIL._tkinter_finder'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WARPGATE-Universal-v2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='LOGO_SMALL_APPLICATION.ico',
    uac_admin=True
)
