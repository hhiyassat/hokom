"""
P5 verdict isolation tests — يثبت أن _run() يعكس mb.verdict بلا hardcoding.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from pipeline.p5_lexical.mabni_inventory import MabniEntry
from pipeline.p5_lexical.mabni_projection import _verdict_from


def test_is_operator_true_gives_operator_boundary():
    entry = MabniEntry('وَ','و','العطف','Conjunction',1,'عطف','test',is_operator=True)
    assert _verdict_from([entry], 'ACCEPT') == 'OPERATOR_BOUNDARY'


def test_is_operator_false_gives_mabni_boundary():
    entry = MabniEntry('هَذَا','هذا','إشارة','Demonstrative',5,'إشارة','test',is_operator=False)
    assert _verdict_from([entry], 'ACCEPT') == 'MABNI_BOUNDARY'


def test_defer_gives_operator_deferred_regardless_of_is_operator():
    e_op = MabniEntry('وَ','و','العطف','Conjunction',1,'عطف','test',is_operator=True)
    assert _verdict_from([e_op], 'DEFER') == 'OPERATOR_DEFERRED'


def test_mixed_entries_with_any_operator_gives_operator_boundary():
    e_op   = MabniEntry('x','x','g','g',1,'p','t', is_operator=True)
    e_non  = MabniEntry('y','y','g','g',2,'p','t', is_operator=False)
    assert _verdict_from([e_op, e_non], 'ACCEPT') == 'OPERATOR_BOUNDARY'


def test_run_helper_uses_mb_verdict():
    """Verify _run() in the integration test does not hardcode 'OPERATOR_BOUNDARY'."""
    import ast, pathlib
    src = pathlib.Path('tests/integration/test_all_mabniyat_json_examples.py').read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == '_run':
            code = ast.unparse(node)
            assert "return 'OPERATOR_BOUNDARY', r" not in code, \
                "_run() still hardcodes 'OPERATOR_BOUNDARY' — verdict isolation violated"
            assert "mb.verdict" in code, \
                "_run() must return mb.verdict, not a constant"
            return
    raise AssertionError("_run() function not found in test file")


def test_old_catalog_not_referenced_in_runtime_code():
    """الكتالوج القديم (بدون _corrected) لا يُستخدم في كود runtime (خارج التعليقات والـdocstrings)."""
    import re, ast, pathlib
    inv_path = pathlib.Path('pipeline/p5_lexical/mabni_inventory.py')
    inv_text = inv_path.read_text()
    corrected = 'operators_catalog_split_vocalized_corrected.csv'
    old_bare  = 'operators_catalog_split_vocalized.csv'
    assert corrected in inv_text, "mabni_inventory.py must reference the corrected catalog"

    # استخدم AST لاستخراج السلاسل الفعلية المُستخدمة في الكود (ليس في docstrings/تعليقات)
    tree = ast.parse(inv_text)
    docstring_values = set()
    for node in ast.walk(tree):
        # docstrings هي أول Expr في Module/FunctionDef/ClassDef
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                docstring_values.add(node.body[0].value.value)

    # افحص كل String literal في AST — باستثناء الـdocstrings
    old_in_code = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if old_bare in node.value and node.value not in docstring_values:
                # تحقق أنه ليس مجرد جزء من _corrected
                stripped = node.value.replace(corrected, '')
                if old_bare in stripped:
                    old_in_code = True
                    break

    assert not old_in_code, \
        f"Old catalog '{old_bare}' still referenced in mabni_inventory.py runtime strings (outside docstrings)"
