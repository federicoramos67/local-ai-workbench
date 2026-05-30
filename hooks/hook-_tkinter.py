from __future__ import annotations

import os
from pathlib import Path


python_root = Path(os.environ.get("LOCAL_AI_WORKBENCH_PYTHON_ROOT", "")).resolve()
tcl_root = Path(os.environ.get("LOCAL_AI_WORKBENCH_TCL_ROOT", "")).resolve()

hiddenimports = [
    "tkinter",
    "tkinter.constants",
    "tkinter.filedialog",
    "tkinter.font",
    "tkinter.messagebox",
    "tkinter.ttk",
]

datas = []
binaries = []

if tcl_root.exists():
    for folder_name, target_root in (("tcl8.6", "_tcl_data"), ("tk8.6", "_tk_data")):
        source_root = tcl_root / folder_name
        if source_root.exists():
            for file_path in source_root.rglob("*"):
                if file_path.is_file():
                    relative_parent = file_path.parent.relative_to(source_root)
                    datas.append((str(file_path), str(Path(target_root) / relative_parent)))

if python_root.exists():
    dll_root = python_root / "DLLs"
    for dll_name in ("tcl86t.dll", "tk86t.dll"):
        dll_path = dll_root / dll_name
        if dll_path.exists():
            binaries.append((str(dll_path), "."))

