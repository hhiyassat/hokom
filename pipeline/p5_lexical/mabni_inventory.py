#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mabni_inventory.py — كتالوج المبنيات
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

المصادران:
  1. operators_catalog_split_vocalized.csv  — الأدوات/العوامل المشكولة
  2. /path/to/02_mabniyat/                 — بقية المبنيات (ضمائر، أسماء إشارة...)

القاعدة:
  Mabni(t)  ⟺  Slots(t) ∈ S⁺  ∧  t ∈ MabniCatalog
  لا يُثبت البناء بالمقطع، ولا يُقبل المبني مع بنية مقطعية فاسدة.
"""

import csv
import os
from dataclasses import dataclass, field
from pathlib import Path
from normalizer import normalize

# ── حروف التشكيل العربية ──────────────────────────────────────────────────────
# تُستخدم في المرحلة 3 من lookup_canonical() للمطابقة مع المداخل غير المشكولة.
# DEPRECATED (Phase A): parallel diacritic set — will consolidate into
# glyph_classification.MarkClass as the single source of truth.
# Do not expand this set; use build_glyph_traces() in new code.
_ARABIC_DIACRITICS = frozenset('ًٌٍَُِّْٰ')
_SHADDA            = 'ّ'   # U+0651 — الشدة وحدها
# حروف التشكيل باستثناء الشدة — تُستخدم في _by_bare لحفظ التمييز الصرفي
_DIACRITICS_NO_SHADDA = _ARABIC_DIACRITICS - {_SHADDA}

def _strip_diacritics(s: str) -> str:
    """أزِل جميع حروف التشكيل العربية من السلسلة (شاملةً الشدة)."""
    return ''.join(c for c in s if c not in _ARABIC_DIACRITICS)


def _diacritics_compatible(input_s: str, catalog_s: str) -> bool:
    """
    حارس التشكيل: تحقَّق أن كل حركة مُقيِّدة في المُدخَل موجودة في مدخل الكتالوج.

    يمنع هذا مطابقة هُوِ (بكسرة على الواو) بـ هُوَ (بفتحة على الواو)
    في المرحلة 3ب (bare fallback).

    القاعدة:
      السكون (ْ) في المُدخَل لا يُعدّ تعارضًا إن غاب عن الكتالوج.
      السكون على حروف المد (ا، و، ي) ترميز بديل شائع، وليس حركة فارقة.
      الحركات الفارقة فقط (فتحة، كسرة، ضمة، تنوين، شدة) تُفرز التعارض.

    أمثلة:
      هُوِ   vs هُوَ   → {ُ:1,ِ:1} vs {ُ:1,َ:1} → ِ غائبة في الكتالوج → False (REJECT)
      مَهمَا vs مَهْمَا → {َ:2}    vs {َ:2,ْ:1} → كل حركات المدخل موجودة → True (ACCEPT)
      عن    vs عَنْ   → {}        vs {َ:1,ْ:1} → مدخل أجرد              → True (ACCEPT)
      فِيْ  vs فِي    → {ِ:1} (بعد تجاهل ْ) vs {ِ:1} → True (ACCEPT)
    """
    from collections import Counter
    # السكون لا يُعدّ حركة فارقة حين يُكتب على حروف المد
    # نُزيله من المقارنة لتجنب الرفض الخاطئ (فِيْ ≈ فِي)
    _SUKUN = 'ْ'
    input_diacs = Counter(c for c in input_s
                          if c in _ARABIC_DIACRITICS and c != _SUKUN)
    if not input_diacs:
        return True  # مُدخَل أجرد (أو سكون فقط) → دائمًا مقبول
    catalog_diacs = Counter(c for c in catalog_s
                            if c in _ARABIC_DIACRITICS and c != _SUKUN)
    return all(catalog_diacs[d] >= count for d, count in input_diacs.items())

def _bare_preserve_shadda(s: str) -> str:
    """
    أزِل التشكيل باستثناء الشدة.

    يُستخدم كمفتاح فهرس _by_bare لأن الشدة فارق صرفي حقيقي يُميِّز:
      إِنَّ  (INNA)      → 'إنّ'   ← يُحفَظ
      إِنْ   (IN_SHART)  → 'إن'    ← يُحفَظ
      أَنَّ  (ANNA)      → 'أنّ'   ← يُحفَظ
      أَنْ   (AN)        → 'أن'    ← يُحفَظ
      أَيّ  (AYY_COND)  → 'أيّ'   ← يُحفَظ
      أَيْ  (AY_NIDA)   → 'أي'    ← يُحفَظ
    حذف الشدة من المفتاح يُدمج هذه الأزواج في نفس الحاوية، وهو خطأ دلالي.
    """
    return ''.join(c for c in s if c not in _DIACRITICS_NO_SHADDA)


# ══════════════════════════════════════════════════════════════════════════════
# هيكل MabniEntry
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class MabniEntry:
    surface_vocalized:      str            # السطح المشكول كما في الكتالوج
    surface_normalized:     str            # بعد التطبيع (الهمزة + ال + شدة)
    category_ar:            str            # الاسم العربي للمجموعة
    category_en:            str            # الاسم الإنجليزي
    group_number:           int
    purpose:                str            # الغرض/الاستخدام
    source:                 str            # اسم الملف
    is_operator:            bool = True    # أداة/عامل مغلق
    allows_root_path:       bool = False   # لا جذر ولا وزن


# ══════════════════════════════════════════════════════════════════════════════
# تحميل البيانات
# ══════════════════════════════════════════════════════════════════════════════

def _load_operators_csv(path: str) -> list[MabniEntry]:
    """
    حمِّل operators_catalog_split_vocalized_corrected.csv.
    مفتاح البحث: عمود Operator (المشكول مباشرةً).

    عمود is_operator (اختياري): True/False — إذا غاب فالقيمة الافتراضية True.
    يُتيح هذا العمود تحديد المبنيات غير العوامل (is_operator=False) التي تعطي
    MABNI_BOUNDARY بدلاً من OPERATOR_BOUNDARY.
    """
    entries: list[MabniEntry] = []
    with open(path, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            surface = row['Operator'].strip()
            if not surface:
                continue
            norm = normalize(surface)
            # قراءة is_operator من العمود إن وُجد، وإلا القيمة الافتراضية True
            is_op_col = (row.get('is_operator') or 'True').strip()
            is_op = is_op_col.lower() not in ('false', '0', 'no')
            entries.append(MabniEntry(
                surface_vocalized  = surface,
                surface_normalized = norm,
                category_ar        = row['Arabic Group Name'].strip(),
                category_en        = row['English Group Name'].strip(),
                group_number       = int(row['Group Number']) if row['Group Number'].strip().isdigit() else 0,
                purpose            = row['Purpose/Usage'].strip(),
                source             = Path(path).name,
                is_operator        = is_op,
                allows_root_path   = False,
            ))
    return entries


def _load_mabniyat_dir(directory: str) -> list[MabniEntry]:
    """
    حمِّل ملفات CSV من مجلد 02_mabniyat.
    كل ملف = صنف من المبنيات (ضمائر، أسماء إشارة، موصولات...).
    يتوقع: عمود surface_vocalized وعمود category على الأقل.

    CWD guard (RC1):
    إذا كان directory فارغًا أو يُحيل إلى CWD، لا تُحمَّل أي ملفات.
    يمنع هذا تلوث الفهرس بملفات CSV عشوائية من الجذر (مثل
    mabniyat_catalog_split_vocalized.csv و operators_catalog_split_vocalized.csv).
    """
    entries: list[MabniEntry] = []
    # ── CWD guard ──────────────────────────────────────────────────────────────
    if not directory:
        return entries   # مسار فارغ → تخطِّ (لا تُحمِّل من CWD)
    dirpath = Path(directory)
    # منع تحميل CWD نفسه حتى لو صودف أنه صريح في الوسيطة
    if dirpath.resolve() == Path.cwd().resolve():
        return entries   # مسار صريح لـ CWD → تخطِّ
    if not dirpath.exists():
        return entries   # المجلد غير متاح في هذه الجلسة

    for csv_file in sorted(dirpath.glob('*.csv')):
        try:
            with open(csv_file, encoding='utf-8-sig', newline='') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames or []
                for row in reader:
                    # تحديد عمود السطح المشكول بمرونة
                    surface = (
                        row.get('surface_vocalized') or
                        row.get('vocalized')         or
                        row.get('form')              or
                        row.get('surface')           or
                        ''
                    ).strip()
                    if not surface:
                        continue
                    norm = normalize(surface)
                    category = (
                        row.get('category') or
                        row.get('category_ar') or
                        csv_file.stem
                    ).strip()
                    entries.append(MabniEntry(
                        surface_vocalized  = surface,
                        surface_normalized = norm,
                        category_ar        = category,
                        category_en        = '',
                        group_number       = 0,
                        purpose            = row.get('purpose', ''),
                        source             = csv_file.name,
                        is_operator        = False,
                        allows_root_path   = False,
                    ))
        except Exception as e:
            print(f"  ⚠ تعذّر تحميل {csv_file.name}: {e}")

    return entries


# ══════════════════════════════════════════════════════════════════════════════
# MabniInventory
# ══════════════════════════════════════════════════════════════════════════════

class MabniInventory:
    """
    كتالوج موحَّد للمبنيات من المصدرين.

    البحث يعمل على مستويين:
      1. السطح المشكول كما أُدخل (بعد تطبيع الهمزة)
      2. السطح المُطبَّع (normalize كاملاً)
    """

    def __init__(self):
        self._entries:     list[MabniEntry]        = []
        self._by_surface:  dict[str, list[MabniEntry]] = {}   # مشكول أصلي
        self._by_norm:     dict[str, list[MabniEntry]] = {}   # مطبَّع
        self._by_bare:     dict[str, list[MabniEntry]] = {}   # بدون تشكيل (للمداخل غير المشكولة)

    # ── تحميل ────────────────────────────────────────────────────────────────

    def load_operators(self, path: str) -> 'MabniInventory':
        for e in _load_operators_csv(path):
            self._add(e)
        return self

    def load_mabniyat(self, directory: str) -> 'MabniInventory':
        for e in _load_mabniyat_dir(directory):
            self._add(e)
        return self

    def _add(self, entry: MabniEntry):
        self._entries.append(entry)
        self._by_surface.setdefault(entry.surface_vocalized,  []).append(entry)
        self._by_norm.setdefault(entry.surface_normalized, []).append(entry)
        # _by_bare: مفتاح بحذف كامل للتشكيل (شاملاً الشدة).
        # التمييز بين إِنَّ/إِنْ لا يحتاج إلى حفظ الشدة في المفتاح لأن
        # الحارس unique-surface في Phase 3b يرصد تعدد surface_vocalized
        # تحت نفس المفتاح ويُعيد [] بدلاً من إعلان هوية خاطئة.
        bare = _strip_diacritics(entry.surface_vocalized)
        if bare:
            self._by_bare.setdefault(bare, []).append(entry)

    # ── بحث ──────────────────────────────────────────────────────────────────

    def lookup(self, surface: str) -> list[MabniEntry]:
        """
        ابحث بالسطح المشكول.
        أولاً: تطابق مباشر → ثانياً: تطابق بعد التطبيع.
        """
        if surface in self._by_surface:
            return self._by_surface[surface]
        norm = normalize(surface)
        return self._by_norm.get(norm, [])

    def lookup_canonical(
        self,
        canonical:  str,
        normalized: str,
    ) -> 'tuple[list[MabniEntry], str]':
        """
        بحث ثنائي المرحلة — يُعيد (المداخل، السطح المطابق من الكتالوج).

        Phase 1: تطابق مباشر للسطح الأصلي في _by_surface.
                 يعمل حين تتطابق ترميزات Unicode تمامًا.
        Phase 2: تطابق السطح المُطبَّع في _by_norm.
                 يعمل دائمًا بصرف النظر عن ترتيب الحركات في ملف CSV.

        matched_surface دائمًا = surface_vocalized من الكتالوج
        (أي الشكل المكتوب الأصلي مثل إِنَّ وليس ءِنْنَ).
        """
        # المرحلة 1: تطابق مباشر (يُصاب إن كان ترتيب Unicode متطابقًا)
        if canonical in self._by_surface:
            entries = self._by_surface[canonical]
            return entries, entries[0].surface_vocalized

        # المرحلة 2: تطابق عبر التطبيع (يُصاب دائمًا للأدوات ذات الهمزة/الشدة)
        if normalized in self._by_norm:
            entries = self._by_norm[normalized]
            return entries, entries[0].surface_vocalized

        # المرحلة 3: تطابق الجذع الأصلح (حذف كل التشكيل)
        #   يعمل حين يُخزَّن مدخل الكتالوج بلا تشكيل (كم، لو، إذا، أيا...)
        #   بينما يصل المُدخَل مشكولاً (كَمْ، لَوْ، إِذَا...)
        bare = _strip_diacritics(canonical)
        if bare and bare in self._by_surface:
            entries = self._by_surface[bare]
            return entries, entries[0].surface_vocalized

        bare_norm = _strip_diacritics(normalized)
        if bare_norm and bare_norm != bare and bare_norm in self._by_norm:
            entries = self._by_norm[bare_norm]
            return entries, entries[0].surface_vocalized

        # المرحلة 3ب: مدخل غير مشكول (أو جزئي التشكيل) ↔ كتالوج مشكول
        #   يعمل حين يصل المُدخَل بلا تشكيل (أ، كم، كأين...)
        #   أو بتشكيل جزئي (مَهمَا بلا سكون على الهاء) يُطابَق ضد _by_bare
        #
        #   حارس unique-surface:
        #   إذا أعاد الفهرس مداخل تنتمي لأكثر من surface_vocalized مستقل
        #   (مثال: من → مِنْ MIN + مَنْ MAN تحت المفتاح 'من')
        #   فلا يمكن تحديد الأداة بلا تشكيل → يُعاد ([], '') لتمرير الكلمة
        #
        #   حارس التشكيل (_diacritics_compatible):
        #   يمنع مطابقة مُدخَل ذي حركات متعارضة مع الكتالوج
        #   (مثال: هُوِ لا يُطابَق هُوَ لأن الكسرة تعارض الفتحة)
        if bare and bare in self._by_bare:
            entries = self._by_bare[bare]
            unique_surfaces = {e.surface_vocalized for e in entries}
            if len(unique_surfaces) == 1:
                matched = entries[0].surface_vocalized
                if _diacritics_compatible(canonical, matched):
                    return entries, matched
            # تصادم أو تعارض تشكيل → غامض

        if bare_norm and bare_norm != bare and bare_norm in self._by_bare:
            entries = self._by_bare[bare_norm]
            unique_surfaces = {e.surface_vocalized for e in entries}
            if len(unique_surfaces) == 1:
                matched = entries[0].surface_vocalized
                if _diacritics_compatible(canonical, matched):
                    return entries, matched

        return [], ''

    def lookup_exact(self, surface: str) -> MabniEntry | None:
        """أعِد أول تطابق أو None."""
        results = self.lookup(surface)
        return results[0] if results else None

    # ── إحصاء ────────────────────────────────────────────────────────────────

    def stats(self) -> dict:
        sources: dict[str, int] = {}
        for e in self._entries:
            sources[e.source] = sources.get(e.source, 0) + 1
        return {'total': len(self._entries), 'by_source': sources}


# ══════════════════════════════════════════════════════════════════════════════
# Singleton — نُحمِّل مرة واحدة
# ══════════════════════════════════════════════════════════════════════════════

_INVENTORY: MabniInventory | None = None

# ── مسار مجلد 02_mabniyat الافتراضي ─────────────────────────────────────────
# HOKOM-MABNI-FUNCTIONAL-CATALOG-OWNERSHIP-01 (Commit 3):
# تم تحديث القيمة الافتراضية من '' إلى 'data/02_mabniyat' لتحميل:
#   - relative_pronouns_catalog.csv  (موصولات + ضمائر منفصلة)
# هذا يُتيح قراءة المبنيات غير العوامل من مجلد البيانات بدلاً من تركها فارغة.
_DEFAULT_MABNIYAT_DIR = 'data/02_mabniyat'


def get_inventory(
    operators_csv: str  = 'data/operators_catalog_split_vocalized_corrected.csv',
    mabniyat_dir:  str  = _DEFAULT_MABNIYAT_DIR,
) -> MabniInventory:
    global _INVENTORY
    if _INVENTORY is None:
        _INVENTORY = MabniInventory()
        # ── المصدر 1: الأدوات/العوامل ─────────────────────────────────────
        ops_path = Path(operators_csv)
        if not ops_path.is_absolute():
            # Canonical location is <repo_root>/pipeline/p5_lexical/ — resolve the
            # default relative data path against the repository root (parents[2]),
            # preserving the exact file target the root-level module used (R-8).
            ops_path = Path(__file__).resolve().parents[2] / ops_path
        if ops_path.exists():
            _INVENTORY.load_operators(str(ops_path))
        else:
            print(f"  ⚠ operators CSV غير موجود: {ops_path}")
        # ── المصدر 2: 02_mabniyat (موصولات، ضمائر، استفهام) ──────────────
        if mabniyat_dir and not Path(mabniyat_dir).is_absolute():
            _mabniyat_resolved = Path(__file__).resolve().parents[2] / mabniyat_dir
        else:
            _mabniyat_resolved = Path(mabniyat_dir) if mabniyat_dir else Path('')
        _INVENTORY.load_mabniyat(str(_mabniyat_resolved))
    return _INVENTORY


def reset_inventory() -> None:
    """Reset the singleton (for test isolation). Not for production use."""
    global _INVENTORY
    _INVENTORY = None


# ══════════════════════════════════════════════════════════════════════════════
# اختبار
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    inv = get_inventory()
    s   = inv.stats()
    print(f"\n  الكتالوج: {s['total']} مدخل")
    for src, n in s['by_source'].items():
        print(f"    {n:4}  {src}")

    tests = ['مِنْ', 'فِي', 'إِنَّ', 'بِ', 'لِ', 'كَأَنَّ', 'هُوَ', 'غير موجود']
    print()
    for t in tests:
        e = inv.lookup_exact(t)
        if e:
            print(f"  ✓ {t:12} → {e.category_ar:30}  [{e.source}]")
        else:
            print(f"  ✗ {t:12} → غير موجود في الكتالوج")
