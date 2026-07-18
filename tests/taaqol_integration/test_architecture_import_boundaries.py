"""
Architecture guard: taaqqul_slot_geometry may only be imported from
pipeline/taaqol_integration/. Direct imports in core pipeline modules are forbidden.
"""
import ast
import os
import pytest

FORBIDDEN_PATHS = [
    'pipeline/p3_candidate/',
    'pipeline/p4_wazn/',
    'pipeline/p4_bab/',
    'pipeline/p4_masdar/',
    'pipeline/p4_mushtaqat/',
    'pipeline/p5_inflection/',
    'pipeline/p2_projection/',
    'pipeline/p2_augmented/',
    'pipeline/pre_root/',
]

TAAQOL_MODULE = 'taaqqul_slot_geometry'

def find_py_files(base_dir: str):
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for f in files:
            if f.endswith('.py'):
                yield os.path.join(root, f)

def has_taaqol_import(filepath: str) -> bool:
    try:
        with open(filepath, 'r', encoding='utf-8') as fh:
            tree = ast.parse(fh.read(), filename=filepath)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or '']
                if any(TAAQOL_MODULE in (n or '') for n in names):
                    return True
    except Exception:
        pass
    return False

HOKOM_BASE = os.path.join(os.path.dirname(__file__), '..', '..')

@pytest.mark.parametrize("forbidden_dir", FORBIDDEN_PATHS)
def test_no_taaqol_import_in_core(forbidden_dir):
    base = os.path.normpath(os.path.join(HOKOM_BASE, forbidden_dir))
    if not os.path.isdir(base):
        pytest.skip(f"Directory {forbidden_dir} does not exist")
    violations = [f for f in find_py_files(base) if has_taaqol_import(f)]
    assert violations == [], f"Forbidden taaqqul_slot_geometry imports in {forbidden_dir}: {violations}"

def test_no_taaqol_import_in_hokom_pipeline():
    pipeline_file = os.path.join(HOKOM_BASE, 'hokom_pipeline.py')
    assert not has_taaqol_import(pipeline_file), "hokom_pipeline.py must not directly import taaqqul_slot_geometry"
