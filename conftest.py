# Root conftest: exclude vendor directory from test collection
collect_ignore_glob = ["vendor/*"]

import sys, pathlib
# ensure repo root is on sys.path so `scripts.*` and top-level modules are importable
_root = str(pathlib.Path(__file__).parent)
if _root not in sys.path:
    sys.path.insert(0, _root)
