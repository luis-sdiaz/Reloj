#!/usr/bin/env python3
import sys
import traceback
from pathlib import Path

# Ensure `src` is importable when running scripts from repository root
repo_root = Path(__file__).resolve().parents[1]
repo_root_str = str(repo_root)
if repo_root_str not in sys.path:
    sys.path.insert(0, repo_root_str)

print('Inserted repo_root into sys.path:', repo_root_str)
print('repo_root in sys.path?', repo_root_str in sys.path)

print('--- SMOKE TEST START ---')
print('Python:', sys.version)

def safe_run(fn_name, fn):
    try:
        fn()
        print(f'{fn_name}: OK')
    except Exception:
        print(f'{fn_name}: ERROR')
        traceback.print_exc()


def test_db():
    from src.services.database_service import DatabaseService
    db = DatabaseService()
    print('DB path:', db.db_path)
    db.create_tables()
    db.set_setting('smoke_test_key', 'valor_prueba')
    v = db.get_setting('smoke_test_key')
    print('DB roundtrip:', v)


def test_core_imports():
    from src.core.clock_structure import ClockStructure
    from src.core.hand_factory import HandFactory
    cs = ClockStructure()
    print('ClockStructure instantiated')
    # ensure factory can create a simple hand without GUI
    h = HandFactory.create_hand('second', cs, start_value=0, length=10, color='#00FFFF')
    print('HandFactory created:', type(h).__name__)


def test_tts():
    try:
        import pyttsx3
    except Exception as e:
        print('pyttsx3 import failed:', e)
        raise
    engine = pyttsx3.init()
    engine.say('Prueba de texto a voz desde el proyecto Reloj')
    engine.runAndWait()


safe_run('DB test', test_db)
safe_run('Core imports and factory', test_core_imports)
safe_run('TTS test', test_tts)

print('--- SMOKE TEST END ---')
