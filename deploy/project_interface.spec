# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['../src/project_interface.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['PIL', 'PIL._imagingtk', 'PIL._tkinter_finder'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=True,
    cipher=None,
)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [('v', None, 'OPTION')],
    exclude_binaries=True,
    name='hunspeechrecognition',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../images/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='hunspeechrecognition',
)

