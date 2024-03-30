# -*- mode: python ; coding: utf-8 -*-

import os
import whisper

whisper_assets_path = os.path.join(os.path.dirname(whisper.__file__), 'assets')
whisper_normalizers_path = os.path.join(os.path.dirname(whisper.__file__), 'normalizers')
print(whisper_assets_path)
print(whisper_normalizers_path)


a = Analysis(
    ['../src/project_interface.py'],
    pathex=[],
    binaries=[],
    datas=[(whisper_assets_path, 'whisper/assets'), (whisper_normalizers_path, 'whisper/normalizers')],
    hiddenimports=['PIL', 'whisper.normalizers', 'tiktoken', 'tiktoken_ext.openai_public', 'tiktoken_ext', 'PIL._imagingtk', 'PIL._tkinter_finder'],
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

