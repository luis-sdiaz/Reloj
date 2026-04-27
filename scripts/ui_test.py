#!/usr/bin/env python3
import sys
from pathlib import Path

# ensure repo root on sys.path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

import tkinter as tk
from src.ui.settings_dialog import SettingsDialog
from src.services.database_service import DatabaseService

def main():
    root = tk.Tk()
    root.withdraw()

    applied = {}

    def apply_cb(changes):
        applied.update(changes)

    dlg = SettingsDialog(root, apply_callback=apply_cb)

    # set values programmatically
    dlg.logo_name.set('Real Madrid')
    dlg.second_color.set('#FF0000')

    print('Calling Speak Time (pyttsx3)...')
    try:
        dlg._speak_time()
        print('Speak Time invoked')
    except Exception as e:
        print('Speak Time failed:', e)

    print('Saving settings...')
    dlg._on_save()

    # verify persistence
    db = DatabaseService()
    val = db.get_setting('logo_name')
    print('Persisted logo_name:', val)

    # cleanup
    try:
        dlg.destroy()
    except Exception:
        pass
    try:
        root.destroy()
    except Exception:
        pass

if __name__ == '__main__':
    main()
