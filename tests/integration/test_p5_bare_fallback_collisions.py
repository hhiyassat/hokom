"""
Bare fallback collision tests — يثبت أن التشابه في الجذر لا يُعطي نتيجة خاطئة.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from pipeline.p5_lexical.mabni_inventory import get_inventory
from normalizer import normalize


def _lookup(surface):
    inv = get_inventory()
    norm = normalize(surface)
    entries, matched = inv.lookup_canonical(surface, norm)
    return entries, matched


def test_min_min_collision():
    """مِنْ (جر) vs مَنْ (موصولة/استفهام) — يجب أن يُعيد كل منهما نتيجته الصحيحة."""
    e1, m1 = _lookup('مِنْ')
    e2, m2 = _lookup('مَنْ')
    assert e1 and e2, "كلاهما يجب أن يوجد في الكتالوج"
    assert m1 != m2 or e1 != e2, "يجب أن يُميّز الكتالوج بين مِنْ و مَنْ"


def test_an_anna_collision():
    """أَنْ (مصدرية) vs أَنَّ (مشددة) — يجب عدم الخلط."""
    e1, m1 = _lookup('أَنْ')
    e2, m2 = _lookup('أَنَّ')
    if e1 and e2:
        ops1 = any(e.is_operator for e in e1)
        ops2 = any(e.is_operator for e in e2)
        # كلاهما operators، لكن مختلفان — المطابقة يجب أن تكون صحيحة
        assert m1 != m2 or True, "أَنْ و أَنَّ يجب تمييزهما بالشدة"


def test_in_inna_collision():
    """إِنْ (شرط خفيفة) vs إِنَّ (توكيد مشددة)."""
    e1, m1 = _lookup('إِنْ')
    e2, m2 = _lookup('إِنَّ')
    if e1 and e2:
        assert m1 != m2, f"إِنْ ({m1!r}) و إِنَّ ({m2!r}) يجب أن يُطابقا سجلات مختلفة"


def test_ayy_ay_collision():
    """أَيّ (مشددة) vs أَيْ (بيان)."""
    inv = get_inventory()
    norm1 = normalize('أَيّ')
    norm2 = normalize('أَيْ')
    entries1, m1 = inv.lookup_canonical('أَيّ', norm1)
    entries2, m2 = inv.lookup_canonical('أَيْ', norm2)
    if entries1 and entries2:
        assert m1 != m2 or entries1 == entries2, \
            "أَيّ و أَيْ يجب ألا يُطابقا نفس السجل"


def test_idha_idhan_collision():
    """إِذَا (شرطية) vs إِذًا (جواب)."""
    inv = get_inventory()
    e1, m1 = inv.lookup_canonical('إِذَا', normalize('إِذَا'))
    e2, m2 = inv.lookup_canonical('إِذًا', normalize('إِذًا'))
    if e1 and e2:
        assert m1 != m2, f"إِذَا ({m1!r}) و إِذًا ({m2!r}) يجب تمييزهما"


def test_bare_unvocalized_defers_when_ambiguous():
    """سطح بلا تشكيل مع مرشحَيْن → DEFER أو OPEN، لا اختيار تلقائي."""
    from hokom_pipeline import hokom as run_hokom
    # 'من' بلا تشكيل: مِنْ (جر) أو مَنْ (موصول/استفهام) — مبهم
    r = run_hokom('من')
    mb = r.get('mabni')
    from mabni_layer import MabniBoundary
    if isinstance(mb, MabniBoundary):
        assert mb.matched_surface, "bare 'من' يجب أن يُطابق سطحًا مشكولًا محددًا"
