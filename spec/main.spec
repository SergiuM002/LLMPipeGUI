# -*- mode: python ; coding: utf-8 -*-
import os

project_root = os.path.abspath(os.path.join(SPECPATH, '..'))
src_dir = os.path.abspath(os.path.join(SPECPATH, '../src'))

a = Analysis(
    ['../src/llmpipegui/__main__.py'],
    pathex=[project_root, src_dir],
    binaries=[],
    datas=[],
    hiddenimports=['PIL._tkinter_finder'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LLMPipeGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../icons/llmpipegui.ico'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LLMPipeGUI',
)
app = BUNDLE(
    exe,
    name='LLMPipeGUI.app',
    icon='../icons/llmpipegui.icns',
    bundle_identifier='com.sergiu.llmpipegui',
)
