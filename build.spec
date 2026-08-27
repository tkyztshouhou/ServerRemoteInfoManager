# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for ServerRemoteInfoManager v2.2
# 用法:
#   pyinstaller build.spec --noconfirm                       # 文件夹版（给 Inno Setup 用）
#   set PYI_ONEFILE=1 && pyinstaller build.spec --noconfirm  # 单文件版（给 RAR 用）

import os, sys
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None
PROJECT_ROOT = os.path.abspath(SPECPATH)
ONE_FILE = os.environ.get('PYI_ONEFILE', '0') == '1'

hiddenimports = []
hiddenimports += collect_submodules('tkinter')
hiddenimports += collect_submodules('PIL')
hiddenimports += collect_submodules('faq')
hiddenimports += ['sqlite3','subprocess','threading','webbrowser','re',
                  'tempfile','os','sys','datetime','json','base64',
                  'hashlib','shutil','pathlib',
                  'markdown','tkhtmlview']

datas = [
    (os.path.join('img'), 'img'),
    (os.path.join('version.txt'), '.'),
]

excludes = [
    'matplotlib','numpy','pandas','scipy',
    'PyQt5','PyQt6','PySide2','PySide6','wx',
    'unittest','test','tests','setuptools','pip',
    'docutils','jinja2','sphinx','pytest','black','flake8',
    'IPython','notebook','pydoc_data',
]

# Windows 下显式带 tcl/tk，确保无 Python 电脑可运行
if sys.platform.startswith('win'):
    try:
        import tkinter
        tcl_dir = os.path.join(os.path.dirname(tkinter.__file__), 'tcl8.6')
        tk_dir  = os.path.join(os.path.dirname(tkinter.__file__), 'tk8.6')
        if os.path.isdir(tcl_dir): datas += [(tcl_dir,'tcl8.6')]
        if os.path.isdir(tk_dir):  datas += [(tk_dir,'tk8.6')]
    except Exception:
        pass

icon_path = os.path.join('img','app.ico')
icon_arg  = icon_path if os.path.exists(icon_path) else None

if ONE_FILE:
    a = Analysis(['app.py'], pathex=[PROJECT_ROOT], datas=datas,
                 hiddenimports=hiddenimports, excludes=excludes)
    pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
    EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
        name='ServerRemoteInfoManager', debug=False, strip=False,
        upx=True, console=False, icon=icon_arg, version='version.txt')
else:
    a = Analysis(['app.py'], pathex=[PROJECT_ROOT], datas=datas,
                 hiddenimports=hiddenimports, excludes=excludes)
    pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
    exe = EXE(pyz, a.scripts, [], exclude_binaries=True,
              name='ServerRemoteInfoManager', debug=False, strip=False,
              upx=True, console=False, icon=icon_arg, version='version.txt')
    COLLECT(exe, a.binaries, a.zipfiles, a.datas,
            strip=False, upx=True, name='ServerRemoteInfoManager')
