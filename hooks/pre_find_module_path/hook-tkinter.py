def pre_find_module_path(hook_api):
    # The local Windows build script explicitly supplies Tcl/Tk files.
    # Keep tkinter discoverable even if PyInstaller's Tcl probe cannot open a GUI.
    return

