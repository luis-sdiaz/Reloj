#!/usr/bin/env python3
import sys, importlib, traceback, os

# ensure src is importable
root = os.path.dirname(os.path.dirname(__file__))
src = os.path.join(root, 'src')
# ensure both project root and src are available for absolute and package imports
if root not in sys.path:
    sys.path.insert(0, root)
if src not in sys.path:
    sys.path.insert(0, src)

modules = [
    'ui.clock_face',
    'core.clock_structure',
    'core.hand_factory',
    'controllers.clock_controller',
    'services.database_service',
    'utils.geometry',
]

ok = True
for m in modules:
    try:
        importlib.import_module(m)
        print(f'OK {m}')
    except Exception:
        ok = False
        print(f'ERR {m}')
        traceback.print_exc()

if ok:
    print('All imports OK')
    sys.exit(0)
else:
    print('One or more imports failed')
    sys.exit(2)
