import sys, os
from cx_Freeze import setup, Executable
import main

if sys.platform == "win32":
	base = "Win32GUI"
else:
        base = None
		
shortcut_table = [
    ("DesktopShortcut",        # Shortcut
     "DesktopFolder",          # Directory_
     "Diabolik Stock",           # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]main.exe",# Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     )
    ]
msi_data = {'Shortcut':shortcut_table}

options = {'build_exe': {
        "excludes": [],
        "includes": [],
        "include_files": ['create_tables.sql', 'images', 'icon.ico'],
        "optimize": 2},
		'bdist_msi':{'data': msi_data}
         }

setup(name = "DiabolikStock",
    version = main.VERSION,
    description = "Diabolik Stock",
    options = options,
    executables = [Executable("main.py",
        base=base,
        icon="icon.ico",
        shortcutName="Diabolik Stock",
        shortcutDir="DesktopFolder",
        copyright="Kidivid")])
