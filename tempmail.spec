# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# 收集 customtkinter 相关文件
ctk_datas = collect_data_files('customtkinter')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        *ctk_datas,  # 添加 customtkinter 数据文件
    ],
    hiddenimports=[
        'engineio.async_drivers.threading',
        *collect_submodules('customtkinter'),  # 添加 customtkinter 的所有子模块
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
    name='CursorReset',
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
)
