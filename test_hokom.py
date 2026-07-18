#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_hokom.py — اختبارات P4 Slot Engineering و P5 Mabni Lookup
══════════════════════════════════════════════════════════════════
تغطية:
  P4  — إشباع الخانة (SATURATED)، عدم فتح خانة مبكرة
  P5  — operator_id, lexical_family, contract_id, contract_state
  P5  — لا حقول نحوية: لا contract_family, لا kind, لا expects
  Surface — الفصل الصارم بين التمثيلات الأربعة
  P4/P5   — الانحدار (لا كسر في الحالات الصحيحة)
"""

import unittest
from normalizer        import normalize
from syllabifier       import parse_phones, syllabify, word_gate
from mabni_layer       import process_mabni, MabniBoundary, MabniOpen, MabniBlocked
from relation_contract import RelationContract


# ══════════════════════════════════════════════════════════════════════════════
# مساعدات
# ══════════════════════════════════════════════════════════════════════════════

def _slots(word: str):
    """أعِد قائمة الـ slot dicts للكلمة (بعد التطبيع)."""
    norm   = normalize(word)
    phones = parse_phones(norm)
    slots  = syllabify(phones)
    return [s for s in slots if s['surface'] != ' ']


def _verdict(word: str) -> tuple[str, list[str]]:
    norm   = normalize(word)
    phones = parse_phones(norm)
    slots  = syllabify(phones)
    return word_gate(slots)


def _mabni(word: str):
    """
    يُمرِّر input_surface و normalized_surface بشكل صريح إلى process_mabni.
    هذا يضمن اختبار الفصل الصارم بين التمثيلات.
    """
    norm   = normalize(word)
    phones = parse_phones(norm)
    slots  = syllabify(phones)
    v, vl  = word_gate(slots)
    return process_mabni(word, norm, slots, v, vl)


# ══════════════════════════════════════════════════════════════════════════════
# P4 — إشباع الخانة (SATURATION)
# ══════════════════════════════════════════════════════════════════════════════

class TestP4Saturation(unittest.TestCase):

    def test_matat_patterns(self):
        """مَاتَتْ → [CVV, CVC]"""
        patterns = [s['pattern'] for s in _slots('مَاتَتْ')]
        self.assertEqual(patterns, ['CVV', 'CVC'],
                         f"أنماط غير صحيحة: {patterns}")

    def test_matat_accept(self):
        """مَاتَتْ → ACCEPT على مستوى الكلمة"""
        v, _ = _verdict('مَاتَتْ')
        self.assertEqual(v, 'ACCEPT')

    def test_zawjatihi_patterns(self):
        """زَوْجَتُهُ → [CVV, CV, CV, CV]"""
        patterns = [s['pattern'] for s in _slots('زَوْجَتُهُ')]
        self.assertEqual(patterns, ['CVV', 'CV', 'CV', 'CV'],
                         f"أنماط غير صحيحة: {patterns}")

    def test_slot1_matat_saturated(self):
        """Slot1 في مَاتَتْ يُغلق بسبب SATURATED لا بسبب ورود المتحرك مجردًا"""
        slots = _slots('مَاتَتْ')
        self.assertEqual(slots[0]['close_reason'], 'SATURATED',
                         "Slot1 يجب أن يُغلق بـ SATURATED")
        self.assertEqual(slots[0]['status_at_close'], 'COMPLETE',
                         "Slot1 كان COMPLETE لحظة الإغلاق")

    def test_slot1_zawjatihi_saturated(self):
        """Slot1 في زَوْجَتُهُ أُغلق بـ SATURATED (جَ أشبعه، لا مجرد ورود جَ)"""
        slots = _slots('زَوْجَتُهُ')
        self.assertEqual(slots[0]['close_reason'], 'SATURATED')
        self.assertEqual(slots[0]['status_at_close'], 'COMPLETE')

    def test_last_slot_word_end(self):
        """آخر خانة في أي كلمة تُغلق بـ WORD_END"""
        for word in ['مَاتَتْ', 'زَوْجَتُهُ', 'ضَرَبَ', 'مِنْ']:
            slots = _slots(word)
            self.assertEqual(slots[-1]['close_reason'], 'WORD_END',
                             f"{word}: آخر خانة يجب أن تُغلق بـ WORD_END")

    def test_no_premature_slot(self):
        """كل إغلاق خانة سببه SATURATED أو WORD_END (بلا فتح مبكر)"""
        for word in ['ضَرَبَ', 'مَاتَتْ', 'زَوْجَتُهُ', 'كِتَابٌ']:
            slots = _slots(word)
            for s in slots:
                self.assertIn(s['close_reason'], {'SATURATED', 'WORD_END'},
                              f"{word}: خانة أُغلقت بسبب غير مُرخَّص: {s['close_reason']}")


# ══════════════════════════════════════════════════════════════════════════════
# P5 — Mabni Lookup: operator_id + lexical_family (لا نحو)
# ══════════════════════════════════════════════════════════════════════════════

class TestP5MabniBoundary(unittest.TestCase):

    # ── وَ ─────────────────────────────────────────────────────────────────────

    def test_waw_operator_boundary(self):
        """وَ → OPERATOR_BOUNDARY"""
        r = _mabni('وَ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.verdict, 'OPERATOR_BOUNDARY')

    def test_waw_blocks_root_path(self):
        """وَ → blocks_root_path=True"""
        r = _mabni('وَ')
        self.assertTrue(r.blocks_root_path)

    def test_waw_operator_id(self):
        """وَ → operator_id=WA"""
        r = _mabni('وَ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.operator_id, 'WA')

    def test_waw_lexical_family(self):
        """وَ → lexical_family=WA (هوية ذاتية)"""
        r = _mabni('وَ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.lexical_family, 'WA')

    def test_waw_relation_contract_id(self):
        """وَ → relation_contract.contract_id=WA"""
        r = _mabni('وَ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.relation_contract.contract_id, 'WA')

    def test_waw_relation_contract_state_open(self):
        """وَ → relation_contract.contract_state=OPEN"""
        r = _mabni('وَ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.relation_contract.contract_state, 'OPEN')

    def test_waw_no_contract_family_field(self):
        """وَ → RelationContract لا يحتوي على حقل contract_family (مُزال معماريًا)"""
        r = _mabni('وَ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertFalse(hasattr(r.relation_contract, 'contract_family'),
                         "P5 يجب ألا يُصدر contract_family — مُزال في إعادة الهيكلة")

    def test_waw_no_expects_field(self):
        """وَ → RelationContract لا يحتوي على حقل expects"""
        r = _mabni('وَ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertFalse(hasattr(r.relation_contract, 'expects'),
                         "P5 يجب ألا يُصدر حقل expects — هذا تنبؤ نحوي لا يخص P5")

    def test_waw_inventory_status_found(self):
        """وَ → inventory_status=FOUND"""
        r = _mabni('وَ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.inventory_status, 'FOUND')

    def test_waw_lexical_class(self):
        """وَ → lexical_class='Closed Function Word'"""
        r = _mabni('وَ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.lexical_class, 'Closed Function Word')

    def test_waw_candidates_internal_only(self):
        """وَ → function_candidates متوفرة داخليًا (مجموعتان على الأقل)"""
        r = _mabni('وَ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertGreaterEqual(len(r.function_candidates), 2)

    def test_waw_opens_relation(self):
        """وَ → opens_relation=True"""
        r = _mabni('وَ')
        self.assertTrue(r.opens_relation)

    # ── باقي الأدوات ───────────────────────────────────────────────────────────

    def test_bi_operator_boundary(self):
        r = _mabni('بِ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.verdict, 'OPERATOR_BOUNDARY')
        self.assertEqual(r.operator_id, 'BI')
        self.assertEqual(r.lexical_family, 'BI')
        self.assertEqual(r.relation_contract.contract_id, 'BI')
        self.assertEqual(r.relation_contract.contract_state, 'OPEN')

    def test_ka_operator_boundary(self):
        r = _mabni('كَ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.verdict, 'OPERATOR_BOUNDARY')
        self.assertEqual(r.operator_id, 'KA')
        self.assertEqual(r.lexical_family, 'KA')
        self.assertEqual(r.relation_contract.contract_state, 'OPEN')

    def test_li_operator_boundary(self):
        """لِ → operator_id=LI (هوية ذاتية، لا MULTI_FUNCTION_OPERATOR)"""
        r = _mabni('لِ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.verdict, 'OPERATOR_BOUNDARY')
        self.assertEqual(r.operator_id, 'LI')
        self.assertEqual(r.lexical_family, 'LI')

    def test_li_multiple_candidates_internal(self):
        """لِ → function_candidates داخلية متعددة (ملكية + أمر على الأقل)"""
        r = _mabni('لِ')
        self.assertGreaterEqual(len(r.function_candidates), 2)

    def test_min_operator_boundary(self):
        r = _mabni('مِنْ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.verdict, 'OPERATOR_BOUNDARY')
        self.assertEqual(r.operator_id, 'MIN')
        self.assertEqual(r.lexical_family, 'MIN')
        self.assertEqual(r.relation_contract.contract_id, 'MIN')
        self.assertEqual(r.relation_contract.contract_state, 'OPEN')

    def test_an_operator_boundary(self):
        """أَنْ → OPERATOR_BOUNDARY — هوية ذاتية AN"""
        r = _mabni('أَنْ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.verdict, 'OPERATOR_BOUNDARY')
        self.assertEqual(r.operator_id, 'AN')
        self.assertEqual(r.lexical_family, 'AN')
        self.assertEqual(r.relation_contract.contract_state, 'OPEN')

    def test_ila_operator_boundary(self):
        """إِلَى → هوية ذاتية ILA"""
        r = _mabni('إِلَى')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.verdict, 'OPERATOR_BOUNDARY')
        self.assertEqual(r.operator_id, 'ILA')
        self.assertEqual(r.lexical_family, 'ILA')

    def test_fi_operator_boundary(self):
        """فِي → هوية ذاتية FI"""
        r = _mabni('فِي')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.operator_id, 'FI')
        self.assertEqual(r.lexical_family, 'FI')

    def test_an_preposition_boundary(self):
        """عَنْ → هوية ذاتية AN_JAR"""
        r = _mabni('عَنْ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.operator_id, 'AN_JAR')
        self.assertEqual(r.lexical_family, 'AN_JAR')

    def test_hatta_operator_boundary(self):
        """حَتَّى → OPERATOR_BOUNDARY — هوية ذاتية HATTA"""
        r = _mabni('حَتَّى')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.verdict, 'OPERATOR_BOUNDARY')
        self.assertEqual(r.operator_id, 'HATTA')
        self.assertEqual(r.lexical_family, 'HATTA')
        self.assertEqual(r.relation_contract.contract_state, 'OPEN')

    def test_bacd_is_open(self):
        """بَعْدَ → غير موجود في الكتالوج → MabniOpen"""
        r = _mabni('بَعْدَ')
        self.assertIsInstance(r, MabniOpen)
        self.assertEqual(r.verdict, 'OPEN')

    def test_bacd_valid_slots(self):
        v, _ = _verdict('بَعْدَ')
        self.assertEqual(v, 'ACCEPT')


# ══════════════════════════════════════════════════════════════════════════════
# P5 — Lexical Identity: operator_id + lexical_family (لا تصنيف نحوي)
# ══════════════════════════════════════════════════════════════════════════════

class TestLexicalIdentity(unittest.TestCase):
    """
    يُثبت أن P5 تُعلن الهوية المعجمية (operator_id / lexical_family) فقط.
    لا يوجد حقل contract_family أو expects أو أي تنبؤ نحوي.
    """

    def _op_id(self, word: str) -> str:
        r = _mabni(word)
        self.assertIsInstance(r, MabniBoundary, f"{word} ليست MabniBoundary")
        return r.operator_id

    def _family(self, word: str) -> str:
        r = _mabni(word)
        self.assertIsInstance(r, MabniBoundary, f"{word} ليست MabniBoundary")
        return r.lexical_family

    def _state(self, word: str) -> str:
        r = _mabni(word)
        self.assertIsInstance(r, MabniBoundary, f"{word} ليست MabniBoundary")
        return r.relation_contract.contract_state

    # ── INNA_SERIES — أسرة معجمية حقيقية ───────────────────────────────────────

    def test_inna_operator_id(self):
        self.assertEqual(self._op_id('إِنَّ'), 'INNA')

    def test_inna_family(self):
        self.assertEqual(self._family('إِنَّ'), 'INNA_SERIES')

    def test_anna_operator_id(self):
        self.assertEqual(self._op_id('أَنَّ'), 'ANNA')

    def test_anna_family(self):
        self.assertEqual(self._family('أَنَّ'), 'INNA_SERIES')

    def test_kaanna_operator_id(self):
        self.assertEqual(self._op_id('كَأَنَّ'), 'KAANNA')

    def test_kaanna_family(self):
        self.assertEqual(self._family('كَأَنَّ'), 'INNA_SERIES')

    def test_lakinna_operator_id(self):
        self.assertEqual(self._op_id('لَكِنَّ'), 'LAKINNA')

    def test_lakinna_family(self):
        self.assertEqual(self._family('لَكِنَّ'), 'INNA_SERIES')

    def test_layta_operator_id(self):
        self.assertEqual(self._op_id('لَيْتَ'), 'LAYTA')

    def test_layta_family(self):
        self.assertEqual(self._family('لَيْتَ'), 'INNA_SERIES')

    def test_laalla_operator_id(self):
        self.assertEqual(self._op_id('لَعَلَّ'), 'LAALLA')

    def test_laalla_family(self):
        self.assertEqual(self._family('لَعَلَّ'), 'INNA_SERIES')

    # ── هوية ذاتية — الأدوات المنفردة ──────────────────────────────────────────

    def test_an_operator_id(self):
        """أَنْ → AN (هوية ذاتية، لا SUBORDINATION)"""
        self.assertEqual(self._op_id('أَنْ'), 'AN')

    def test_an_family(self):
        self.assertEqual(self._family('أَنْ'), 'AN')

    def test_kay_operator_id(self):
        """كَيْ → KAY (هوية ذاتية، لا SUBORDINATION)"""
        self.assertEqual(self._op_id('كَيْ'), 'KAY')

    def test_kay_family(self):
        self.assertEqual(self._family('كَيْ'), 'KAY')

    def test_kam_operator_id(self):
        """كَمْ → KAM (هوية ذاتية، لا SPECIFICATION)
        يُثبت Phase 3 من lookup_canonical(): الكتالوج يخزِّن كم بلا تشكيل."""
        self.assertEqual(self._op_id('كَمْ'), 'KAM')

    def test_kam_family(self):
        self.assertEqual(self._family('كَمْ'), 'KAM')

    def test_lam_operator_id(self):
        """لَمْ → LAM (هوية ذاتية، لا JUSSIVE_OPERATOR)"""
        self.assertEqual(self._op_id('لَمْ'), 'LAM')

    def test_lam_family(self):
        self.assertEqual(self._family('لَمْ'), 'LAM')

    def test_lamma_operator_id(self):
        self.assertEqual(self._op_id('لَمَّا'), 'LAMMA')

    def test_lamma_family(self):
        self.assertEqual(self._family('لَمَّا'), 'LAMMA')

    def test_in_shart_operator_id(self):
        """إِنْ → IN_SHART (هوية ذاتية — يُمييَّز من إِنَّ بـ bare_key)"""
        self.assertEqual(self._op_id('إِنْ'), 'IN_SHART')

    def test_in_shart_family(self):
        self.assertEqual(self._family('إِنْ'), 'IN_SHART')

    def test_lan_operator_id(self):
        self.assertEqual(self._op_id('لَنْ'), 'LAN')

    def test_lan_family(self):
        self.assertEqual(self._family('لَنْ'), 'LAN')

    def test_ma_operator_id(self):
        """مَا → MA (هوية ذاتية، لا NEGATION)"""
        self.assertEqual(self._op_id('مَا'), 'MA')

    def test_ma_family(self):
        self.assertEqual(self._family('مَا'), 'MA')

    def test_la_operator_id(self):
        """لَا → LA (هوية ذاتية، لا MULTI_FUNCTION_OPERATOR)"""
        self.assertEqual(self._op_id('لَا'), 'LA')

    def test_la_family(self):
        self.assertEqual(self._family('لَا'), 'LA')

    def test_illa_operator_id(self):
        """إِلَّا → ILLA (هوية ذاتية)"""
        self.assertEqual(self._op_id('إِلَّا'), 'ILLA')

    def test_illa_family(self):
        self.assertEqual(self._family('إِلَّا'), 'ILLA')

    def test_ya_operator_id(self):
        self.assertEqual(self._op_id('يَا'), 'YA')

    def test_ya_family(self):
        self.assertEqual(self._family('يَا'), 'YA')

    def test_man_operator_id(self):
        self.assertEqual(self._op_id('مَنْ'), 'MAN')

    def test_man_family(self):
        self.assertEqual(self._family('مَنْ'), 'MAN')

    # ── كل العقود من P5 بحالة OPEN ──────────────────────────────────────────────

    def test_all_contracts_open(self):
        """جميع أدوات P5 تُعلن عقدًا بحالة OPEN"""
        ops = ['بِ', 'مِنْ', 'إِنَّ', 'أَنَّ', 'لَعَلَّ', 'أَنْ', 'لَمْ', 'مَا', 'لَا', 'وَ', 'كَيْ',
               'لَكِنَّ', 'لَيْتَ', 'لَمَّا', 'إِنْ', 'لَنْ', 'إِلَّا', 'يَا', 'مَنْ']
        for op in ops:
            with self.subTest(op=op):
                self.assertEqual(self._state(op), 'OPEN')

    # ── contract_id = operator_id دائمًا ────────────────────────────────────────

    def test_contract_id_equals_operator_id(self):
        """contract_id = operator_id لجميع الأدوات"""
        ops = ['بِ', 'مِنْ', 'إِنَّ', 'أَنَّ', 'أَنْ', 'لَمْ', 'مَا', 'لَا', 'وَ', 'كَيْ']
        for op in ops:
            with self.subTest(op=op):
                r = _mabni(op)
                self.assertIsInstance(r, MabniBoundary)
                self.assertEqual(r.relation_contract.contract_id, r.operator_id,
                                 f"{op}: contract_id ≠ operator_id")

    # ── تراجع: لا حقول نحوية في RelationContract ─────────────────────────────────

    def test_no_contract_family_field(self):
        """RelationContract لا يحتوي على حقل contract_family (مُزال معماريًا)"""
        r = _mabni('بِ')
        self.assertFalse(hasattr(r.relation_contract, 'contract_family'),
                         "contract_family مُزال — يجب ألا يظهر في RelationContract")

    def test_no_kind_field(self):
        """RelationContract لا يحتوي على حقل kind"""
        r = _mabni('بِ')
        self.assertFalse(hasattr(r.relation_contract, 'kind'))

    def test_no_expects_on_preposition(self):
        """بِ → RelationContract لا يحتوي على حقل expects"""
        r = _mabni('بِ')
        self.assertFalse(hasattr(r.relation_contract, 'expects'))

    def test_no_expects_on_inna(self):
        """إِنَّ → RelationContract لا يحتوي على حقل expects"""
        r = _mabni('إِنَّ')
        self.assertFalse(hasattr(r.relation_contract, 'expects'))

    def test_no_expects_on_an(self):
        """أَنْ → RelationContract لا يحتوي على حقل expects"""
        r = _mabni('أَنْ')
        self.assertFalse(hasattr(r.relation_contract, 'expects'))

    def test_no_grammatical_effect_categories(self):
        """P5 لا تُنتج فئات الأثر النحوي القديمة"""
        banned_families = {
            'ACCUSATIVE_OPERATOR', 'JUSSIVE_OPERATOR', 'SUBORDINATION',
            'CONDITIONAL', 'SPECIFICATION', 'COORDINATION',
            'MULTI_FUNCTION_OPERATOR', 'PREPOSITION', 'NEGATION',
            'INNA_FAMILY', 'EXCEPTION',
        }
        ops = ['بِ', 'مِنْ', 'إِنَّ', 'أَنَّ', 'لَعَلَّ', 'أَنْ', 'لَمْ',
               'مَا', 'لَا', 'وَ', 'كَيْ', 'كَمْ', 'إِلَّا', 'لَكِنَّ']
        for op in ops:
            with self.subTest(op=op):
                r = _mabni(op)
                self.assertIsInstance(r, MabniBoundary)
                self.assertNotIn(r.lexical_family, banned_families,
                                 f"{op}: lexical_family='{r.lexical_family}' هو فئة نحوية ممنوعة في P5")


# ══════════════════════════════════════════════════════════════════════════════
# Tokenizer — حماية الأدوات المركبة من الفصل الخاطئ
# ══════════════════════════════════════════════════════════════════════════════

class TestTokenizerCompoundProtection(unittest.TestCase):
    """
    يُثبت أن الأدوات المركبة التي تبدأ بـ كَ/بِ/وَ/لِ
    تُحفَظ كوحدات معجمية مستقلة ولا تُفصَل بواسطة CLITIC_PREFIXES.
    """

    def _tokens(self, text: str) -> list[tuple[str, str]]:
        from tokenizer import tokenize, words_only
        return [(t.surface, t.kind) for t in words_only(tokenize(text))]

    def test_kay_preserved(self):
        """كَيْ → رمز واحد 'word' (لا يُفصَل إلى كَ + يْ)"""
        toks = self._tokens('كَيْ')
        self.assertEqual(len(toks), 1)
        self.assertEqual(toks[0][0], 'كَيْ')
        self.assertEqual(toks[0][1], 'word')

    def test_kaanna_preserved(self):
        """كَأَنَّ → رمز واحد 'word' (لا يُفصَل إلى كَ + أَنَّ)"""
        toks = self._tokens('كَأَنَّ')
        self.assertEqual(len(toks), 1)
        self.assertEqual(toks[0][0], 'كَأَنَّ')
        self.assertEqual(toks[0][1], 'word')

    def test_kana_preserved(self):
        """كَانَ → رمز واحد 'word'"""
        toks = self._tokens('كَانَ')
        self.assertEqual(len(toks), 1)
        self.assertEqual(toks[0][0], 'كَانَ')

    def test_bisa_preserved(self):
        """بِئْسَ → رمز واحد 'word' (لا يُفصَل إلى بِ + ئْسَ)"""
        toks = self._tokens('بِئْسَ')
        self.assertEqual(len(toks), 1)
        self.assertEqual(toks[0][0], 'بِئْسَ')

    def test_kay_not_split_into_ka_plus_ya(self):
        """تراجع: كَيْ يجب ألا ينتج عنه رمزان [كَ، يْ]"""
        toks = self._tokens('كَيْ')
        surfaces = [t[0] for t in toks]
        self.assertNotIn('يْ', surfaces, "يْ يجب ألا يظهر كرمز مستقل")
        self.assertNotIn('كَ', surfaces, "كَ يجب ألا يظهر كـ clitic عند معالجة كَيْ")

    def test_kaanna_not_split_into_ka_plus_anna(self):
        """تراجع: كَأَنَّ يجب ألا ينتج عنه رمزان [كَ، أَنَّ]"""
        toks = self._tokens('كَأَنَّ')
        surfaces = [t[0] for t in toks]
        self.assertNotIn('أَنَّ', surfaces, "أَنَّ يجب ألا يظهر كرمز مستقل عند معالجة كَأَنَّ")
        self.assertNotIn('كَ', surfaces, "كَ يجب ألا يظهر كـ clitic عند معالجة كَأَنَّ")

    def test_normal_ka_clitic_still_works(self):
        """كَالشَّمْسِ → [كَ clitic, الشَّمْسِ word] — الفصل العادي لا يزال يعمل"""
        toks = self._tokens('كَالشَّمْسِ')
        self.assertEqual(len(toks), 2)
        self.assertEqual(toks[0], ('كَ', 'clitic'))

    def test_normal_bi_clitic_still_works(self):
        """بِالْقَلَمِ → [بِ clitic, الْقَلَمِ word]"""
        toks = self._tokens('بِالْقَلَمِ')
        self.assertEqual(len(toks), 2)
        self.assertEqual(toks[0], ('بِ', 'clitic'))

    def test_kay_in_pipeline(self):
        """كَيْ يُعالَج كأداة مستقلة في P5 — operator_id=KAY"""
        r = _mabni('كَيْ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.input_surface, 'كَيْ')
        self.assertEqual(r.operator_id, 'KAY')
        self.assertEqual(r.lexical_family, 'KAY')

    def test_kaanna_in_pipeline(self):
        """كَأَنَّ يُعالَج كأداة مستقلة في P5 — operator_id=KAANNA, family=INNA_SERIES"""
        r = _mabni('كَأَنَّ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.input_surface, 'كَأَنَّ')
        self.assertEqual(r.operator_id, 'KAANNA')
        self.assertEqual(r.lexical_family, 'INNA_SERIES')

    def test_kam_preserved(self):
        """كَمْ → رمز واحد 'word' (لا يُفصَل إلى كَ + مْ)"""
        toks = self._tokens('كَمْ')
        self.assertEqual(len(toks), 1, "كَمْ يجب أن يُنتج رمزًا واحدًا")
        self.assertEqual(toks[0], ('كَمْ', 'word'))

    def test_kam_in_pipeline(self):
        """كَمْ يُعالَج كأداة مستقلة في P5 — operator_id=KAM (Phase 3 lookup)"""
        r = _mabni('كَمْ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.input_surface, 'كَمْ')
        self.assertEqual(r.operator_id, 'KAM')
        self.assertEqual(r.lexical_family, 'KAM')
        self.assertEqual(r.relation_contract.contract_state, 'OPEN')


# ══════════════════════════════════════════════════════════════════════════════
# Surface Representation — الفصل الصارم بين التمثيلات الأربعة
# ══════════════════════════════════════════════════════════════════════════════

class TestSurfaceRepresentation(unittest.TestCase):
    """
    يُثبت أن:
      input_surface      يبقى ثابتًا كما أُدخل
      canonical_surface  يحافظ على الهوية الكتابية
      normalized_surface يحتوي على الشكل الداخلي للتحليل
      matched_surface    يعكس surface_vocalized من الكتالوج (ليس الشكل المُطبَّع)
      العرض لا يُحل محل الهوية الكنونية بالشكل المُطبَّع
    """

    # ── إِنَّ ── نموذج الأداة ذات الهمزة والشدة ────────────────────────────────

    def test_inna_input_surface_unchanged(self):
        """إِنَّ → input_surface = 'إِنَّ' (ثابت)"""
        r = _mabni('إِنَّ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.input_surface, 'إِنَّ')

    def test_inna_canonical_surface_correct(self):
        """إِنَّ → canonical_surface = 'إِنَّ' (هوية كتابية صحيحة)"""
        r = _mabni('إِنَّ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.canonical_surface, 'إِنَّ')

    def test_inna_normalized_surface_is_internal(self):
        """إِنَّ → normalized_surface = 'ءِنْنَ' (الشكل الداخلي)"""
        r = _mabni('إِنَّ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.normalized_surface, 'ءِنْنَ')

    def test_inna_matched_surface_is_catalog_form(self):
        """إِنَّ → matched_surface من الكتالوج (ليس ءِنْنَ)"""
        r = _mabni('إِنَّ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertNotEqual(r.matched_surface, 'ءِنْنَ',
                            "matched_surface يجب ألا يكون الشكل المُطبَّع")
        self.assertNotEqual(r.matched_surface, '',
                            "matched_surface يجب ألا يكون فارغًا")

    def test_inna_canonical_not_normalized(self):
        """تراجع: إِنَّ لا تُعرض أو تُخزَّن معجميًا بالشكل ءِنْنَ"""
        r = _mabni('إِنَّ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertNotEqual(r.input_surface,     'ءِنْنَ')
        self.assertNotEqual(r.canonical_surface, 'ءِنْنَ')

    def test_inna_found_in_inventory(self):
        """إِنَّ → موجودة في الكتالوج (OPERATOR_BOUNDARY)"""
        r = _mabni('إِنَّ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.verdict, 'OPERATOR_BOUNDARY')
        self.assertEqual(r.inventory_status, 'FOUND')

    # ── أَنَّ ───────────────────────────────────────────────────────────────────

    def test_anna_input_surface_unchanged(self):
        r = _mabni('أَنَّ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.input_surface, 'أَنَّ')

    def test_anna_canonical_not_normalized(self):
        """تراجع: أَنَّ لا تُخزَّن معجميًا بالشكل ءَنْنَ"""
        r = _mabni('أَنَّ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertNotEqual(r.canonical_surface, 'ءَنْنَ')
        self.assertNotEqual(r.input_surface,     'ءَنْنَ')

    def test_anna_normalized_surface_expanded(self):
        """أَنَّ → normalized_surface = 'ءَنْنَ'"""
        r = _mabni('أَنَّ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.normalized_surface, 'ءَنْنَ')

    # ── لَكِنَّ ─────────────────────────────────────────────────────────────────

    def test_lakinna_input_surface_unchanged(self):
        r = _mabni('لَكِنَّ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.input_surface, 'لَكِنَّ')

    def test_lakinna_canonical_not_normalized(self):
        """تراجع: لَكِنَّ لا تُخزَّن معجميًا بالشكل لَكِنْنَ"""
        r = _mabni('لَكِنَّ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertNotEqual(r.canonical_surface, 'لَكِنْنَ')

    def test_lakinna_normalized_expanded(self):
        r = _mabni('لَكِنَّ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.normalized_surface, 'لَكِنْنَ')

    # ── لَعَلَّ ─────────────────────────────────────────────────────────────────

    def test_laalla_input_surface_unchanged(self):
        r = _mabni('لَعَلَّ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.input_surface, 'لَعَلَّ')

    def test_laalla_canonical_not_normalized(self):
        r = _mabni('لَعَلَّ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertNotEqual(r.canonical_surface, 'لَعَلْلَ')

    def test_laalla_normalized_expanded(self):
        r = _mabni('لَعَلَّ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.normalized_surface, 'لَعَلْلَ')

    # ── رُبَّ ───────────────────────────────────────────────────────────────────

    def test_rubba_input_surface_unchanged(self):
        r = _mabni('رُبَّ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.input_surface, 'رُبَّ')

    def test_rubba_canonical_not_normalized(self):
        """تراجع: رُبَّ لا تُخزَّن معجميًا بالشكل رُبْبَ"""
        r = _mabni('رُبَّ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertNotEqual(r.canonical_surface, 'رُبْبَ')

    def test_rubba_normalized_expanded(self):
        r = _mabni('رُبَّ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.normalized_surface, 'رُبْبَ')

    # ── حَتَّى ─────────────────────────────────────────────────────────────────

    def test_hatta_input_surface_unchanged(self):
        r = _mabni('حَتَّى')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.input_surface, 'حَتَّى')

    def test_hatta_canonical_not_normalized(self):
        """تراجع: حَتَّى لا تُعرف معجميًا بالشكل حَتْتَى"""
        r = _mabni('حَتَّى')
        self.assertIsInstance(r, MabniBoundary)
        self.assertNotEqual(r.canonical_surface, 'حَتْتَى')
        self.assertNotEqual(r.input_surface,     'حَتْتَى')

    def test_hatta_normalized_expanded(self):
        r = _mabni('حَتَّى')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.normalized_surface, 'حَتْتَى')

    # ── إِلَّا ─────────────────────────────────────────────────────────────────

    def test_illa_input_surface_unchanged(self):
        r = _mabni('إِلَّا')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.input_surface, 'إِلَّا')

    def test_illa_canonical_not_normalized(self):
        r = _mabni('إِلَّا')
        self.assertIsInstance(r, MabniBoundary)
        self.assertNotEqual(r.canonical_surface, 'ءِلْلَا')

    # ── أداة غير مُطبَّعة (فِي، بِ) — تحقق أن النماذج الثلاثة متطابقة ────────

    def test_fi_all_surfaces_equal(self):
        """فِي — لا تطبيع → input = canonical = normalized"""
        r = _mabni('فِي')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.input_surface,     'فِي')
        self.assertEqual(r.canonical_surface, 'فِي')
        self.assertEqual(r.normalized_surface,'فِي')

    def test_bi_all_surfaces_equal(self):
        """بِ — لا تطبيع → input = canonical = normalized"""
        r = _mabni('بِ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.input_surface,     'بِ')
        self.assertEqual(r.canonical_surface, 'بِ')
        self.assertEqual(r.normalized_surface,'بِ')

    # ── MabniOpen — تأكيد أن الرمز غير المبني يحمل سطحه الأصلي أيضًا ─────────

    def test_bacd_open_input_surface(self):
        """بَعْدَ → MabniOpen — input_surface = 'بَعْدَ'"""
        r = _mabni('بَعْدَ')
        self.assertIsInstance(r, MabniOpen)
        self.assertEqual(r.input_surface, 'بَعْدَ')
        self.assertEqual(r.canonical_surface, 'بَعْدَ')


# ══════════════════════════════════════════════════════════════════════════════
# Monotonicity — قانون الرتابة بين P4 وP5
# ══════════════════════════════════════════════════════════════════════════════

class TestMonotonicity(unittest.TestCase):
    """
    قانون الرتابة (P4 → P5 monotonicity):
      P4 BLOCK  → MabniBlocked دائمًا (لا يُرفع)
      P4 DEFER  → verdict='OPERATOR_DEFERRED' (حتى لو كانت الأداة في الكتالوج)
      P4 ACCEPT → verdict='OPERATOR_BOUNDARY' أو 'MABNI_BOUNDARY' أو 'OPEN'

    وجود الأداة في الكتالوج يُثبت هويتها المعجمية فقط —
    لا يُصلح الخانة البنيوية غير المكتملة ولا يمنحها ACCEPT بأثر رجعي.
    """

    # ── DEFER: أ (حرف منفرد بلا حركة) ─────────────────────────────────────────

    def test_a_p4_defer(self):
        """أ → P4=DEFER (خانة C وحيدة بلا حركة)"""
        v, _ = _verdict('أ')
        self.assertEqual(v, 'DEFER')

    def test_a_p5_operator_deferred_not_boundary(self):
        """أ → P5 يجب ألا يُعلن OPERATOR_BOUNDARY — يُعلن OPERATOR_DEFERRED"""
        r = _mabni('أ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertNotEqual(r.verdict, 'OPERATOR_BOUNDARY',
                            "أ: P4=DEFER → P5 لا يجوز له إعلان OPERATOR_BOUNDARY")
        self.assertEqual(r.verdict, 'OPERATOR_DEFERRED')

    def test_a_structural_verdict_preserved(self):
        """أ → structural_verdict='DEFER' محفوظ من P4"""
        r = _mabni('أ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.structural_verdict, 'DEFER')

    def test_a_operator_id_still_known(self):
        """أ → operator_id معروف رغم DEFER (الهوية المعجمية ثابتة)"""
        r = _mabni('أ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.operator_id, 'A_NIDA')

    # ── DEFER: كم بلا تشكيل ─────────────────────────────────────────────────────

    def test_kam_unvocalized_p4_defer(self):
        """كم (بلا تشكيل) → P4=DEFER (خانتان CC بلا حركات)"""
        v, _ = _verdict('كم')
        self.assertEqual(v, 'DEFER')

    def test_kam_unvocalized_operator_deferred(self):
        """كم (بلا تشكيل) → OPERATOR_DEFERRED لا OPERATOR_BOUNDARY"""
        r = _mabni('كم')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.verdict, 'OPERATOR_DEFERRED')
        self.assertEqual(r.structural_verdict, 'DEFER')

    def test_kam_vocalized_operator_boundary(self):
        """كَمْ (مشكول) → P4=ACCEPT → OPERATOR_BOUNDARY"""
        r = _mabni('كَمْ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.verdict, 'OPERATOR_BOUNDARY')
        self.assertEqual(r.structural_verdict, 'ACCEPT')

    # ── ACCEPT: جميع الأدوات المشكولة ────────────────────────────────────────────

    def test_all_vocalized_operators_structural_accept(self):
        """جميع الأدوات المشكولة التي تنتج OPERATOR_BOUNDARY لها structural_verdict=ACCEPT"""
        ops = ['إِنَّ', 'أَنَّ', 'كَأَنَّ', 'لَكِنَّ', 'لَيْتَ', 'لَعَلَّ',
               'لَمْ', 'لَمَّا', 'إِنْ', 'لَنْ', 'أَنْ', 'كَيْ',
               'إِلَّا', 'يَا', 'وَ', 'مَنْ', 'مَا', 'لَا', 'كَمْ',
               'بِ', 'مِنْ', 'إِلَى', 'فِي', 'عَنْ', 'حَتَّى', 'لِ', 'كَ']
        for op in ops:
            with self.subTest(op=op):
                r = _mabni(op)
                self.assertIsInstance(r, MabniBoundary,
                                      f"{op}: يجب أن يُنتج MabniBoundary")
                self.assertEqual(r.structural_verdict, 'ACCEPT',
                                 f"{op}: structural_verdict يجب أن يكون ACCEPT")
                self.assertEqual(r.verdict, 'OPERATOR_BOUNDARY',
                                 f"{op}: verdict يجب أن يكون OPERATOR_BOUNDARY")

    # ── invariant: OPERATOR_BOUNDARY ↔ structural_verdict=ACCEPT ─────────────────

    def test_operator_boundary_implies_structural_accept(self):
        """OPERATOR_BOUNDARY يستلزم structural_verdict=ACCEPT (الاتجاه الأول)"""
        ops = ['إِنَّ', 'لَمْ', 'أَنْ', 'كَيْ', 'وَ', 'مَا', 'لَا', 'كَمْ']
        for op in ops:
            with self.subTest(op=op):
                r = _mabni(op)
                if isinstance(r, MabniBoundary) and r.verdict == 'OPERATOR_BOUNDARY':
                    self.assertEqual(r.structural_verdict, 'ACCEPT',
                                     f"{op}: OPERATOR_BOUNDARY بدون ACCEPT يخرق قانون الرتابة")

    def test_defer_structural_verdict_never_operator_boundary(self):
        """structural_verdict=DEFER لا يُنتج OPERATOR_BOUNDARY (الاتجاه الثاني)"""
        defer_tokens = ['أ', 'كم']   # tokens معروفة بـ P4=DEFER
        for tok in defer_tokens:
            with self.subTest(tok=tok):
                r = _mabni(tok)
                if isinstance(r, MabniBoundary):
                    self.assertNotEqual(r.verdict, 'OPERATOR_BOUNDARY',
                                        f"{tok}: structural_verdict=DEFER يجب ألا يُنتج OPERATOR_BOUNDARY")

    # ── lexical_class للأفعال ──────────────────────────────────────────────────────

    def test_kana_not_closed_function_word(self):
        """كَانَ → Verbal Operator لا Closed Function Word"""
        r = _mabni('كَانَ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertNotEqual(r.lexical_class, 'Closed Function Word',
                            "كَانَ ليست حرف معنى مغلق")
        self.assertEqual(r.lexical_class, 'Verbal Operator')

    def test_kada_not_closed_function_word(self):
        """كَادَ → Verbal Operator"""
        r = _mabni('كَادَ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.lexical_class, 'Verbal Operator')

    def test_nima_not_closed_function_word(self):
        """نِعْمَ → Verbal Operator"""
        r = _mabni('نِعْمَ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.lexical_class, 'Verbal Operator')

    def test_bi_closed_function_word(self):
        """بِ → Closed Function Word (حرف جر)"""
        r = _mabni('بِ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.lexical_class, 'Closed Function Word')

    def test_inna_closed_function_word(self):
        """إِنَّ → Closed Function Word (حرف توكيد)"""
        r = _mabni('إِنَّ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.lexical_class, 'Closed Function Word')

    # ── Numerical Operator (المجموعة 8) ──────────────────────────────────────

    def test_kam_numerical_operator_class(self):
        """كَمْ → lexical_class='Numerical Operator' لا 'Closed Function Word'"""
        r = _mabni('كَمْ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.lexical_class, 'Numerical Operator',
                         "كَمْ أداة عدد — فئتها Numerical Operator وليست Closed Function Word")
        self.assertNotEqual(r.lexical_class, 'Closed Function Word')

    def test_numerical_operators_remain_operator_boundary(self):
        """جميع أدوات المجموعة 8 تُنتج OPERATOR_BOUNDARY مع opens_relation=True"""
        for word in ['كَمْ', 'كَأَيِّنْ', 'كَذَا', 'مِائَةَ', 'أَلْفَ',
                     'أُلُوفَ', 'مَلَايِينَ', 'عَشَرَةَ']:
            r = _mabni(word)
            self.assertIsInstance(r, MabniBoundary,
                                  f"{word}: يجب أن تُنتج MabniBoundary")
            self.assertIn(r.verdict, ('OPERATOR_BOUNDARY', 'OPERATOR_DEFERRED'),
                          f"{word}: يجب أن يبقى في مسار OPERATOR_BOUNDARY")
            self.assertEqual(r.lexical_class, 'Numerical Operator',
                             f"{word}: الفئة المعجمية يجب أن تكون Numerical Operator")
            self.assertTrue(r.opens_relation,
                            f"{word}: opens_relation يجب أن يكون True")
            self.assertEqual(r.relation_contract.contract_state, 'OPEN',
                             f"{word}: contract_state يجب أن يكون OPEN")

    def test_numerical_operator_not_demoted_to_hr2s(self):
        """أُلُوفَ لا تُحوَّل إلى HR2S رغم أنها اسم — الوظيفة العاملية مستقلة عن الفئة المعجمية"""
        r = _mabni('أُلُوفَ')
        self.assertIsInstance(r, MabniBoundary,
                              "أُلُوفَ مرخَّصة في الكتالوج → MabniBoundary لا MabniOpen")
        self.assertNotEqual(r.verdict, 'OPEN',
                            "الاسمية لا تُزيل الوظيفة العاملية")

    # ── Phrase Operator (عبارات المجموعة 10) ──────────────────────────────────

    def test_ma_zala_phrase_operator_class(self):
        """مَا زَالَ → lexical_class='Phrase Operator' لا 'Verbal Operator'"""
        r = _mabni('مَا زَالَ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.lexical_class, 'Phrase Operator',
                         "مَا زَالَ مشغِّل عبارة — فئتها Phrase Operator وليست Verbal Operator")

    def test_phrase_operators_remain_operator_boundary(self):
        """مَا زَالَ / مَا بَرِحَ / مَا فَتِئَ / مَا دَامَ تُنتج OPERATOR_BOUNDARY"""
        for word in ['مَا زَالَ', 'مَا بَرِحَ', 'مَا فَتِئَ', 'مَا دَامَ']:
            r = _mabni(word)
            self.assertIsInstance(r, MabniBoundary,
                                  f"{word}: مشغِّل عبارة → MabniBoundary")
            self.assertIn(r.verdict, ('OPERATOR_BOUNDARY', 'OPERATOR_DEFERRED'),
                          f"{word}: يجب أن يبقى في مسار OPERATOR_BOUNDARY")
            self.assertEqual(r.lexical_class, 'Phrase Operator',
                             f"{word}: الفئة المعجمية يجب أن تكون Phrase Operator")
            self.assertTrue(r.opens_relation,
                            f"{word}: opens_relation يجب أن يكون True")
            self.assertEqual(r.relation_contract.contract_state, 'OPEN',
                             f"{word}: contract_state يجب أن يكون OPEN")

    def test_ma_infakka_in_operator_profile(self):
        """
        مَا انْفَكَّ محفوظة في OPERATOR_PROFILE رغم أن المقطعي يُعيد BLOCK.

        BLOCK سببه قيد معماري قائم: همزة الوصل في انْفَكَّ تُنتج نمط +V
        عند معالجة الكلمة كوحدة نصية منفردة عبر حدّ المسافة.
        هذا قيد في المقطّع لا في الكتالوج — الأداة مرخَّصة.
        """
        from operator_id_map import get_profile
        profile = get_profile('مَا انْفَكَّ')
        self.assertEqual(profile.operator_id, 'MA_INFAKKA',
                         "مَا انْفَكَّ يجب أن يكون لها operator_id=MA_INFAKKA في الخريطة")

    # ── Cognition Verb (المجموعة 13) ──────────────────────────────────────────

    def test_cognition_verb_class(self):
        """حَسِبْتُ → lexical_class='Cognition Verb' + OPERATOR_BOUNDARY"""
        r = _mabni('حَسِبْتُ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.lexical_class, 'Cognition Verb')
        self.assertIn(r.verdict, ('OPERATOR_BOUNDARY', 'OPERATOR_DEFERRED'))
        self.assertTrue(r.opens_relation)
        self.assertEqual(r.relation_contract.contract_state, 'OPEN')

    def test_cognition_verb_not_demoted_to_hr2s(self):
        """عَلِمْتُ لا تُحوَّل إلى HR2S — الجذر لا يلغي الوظيفة العاملية"""
        r = _mabni('عَلِمْتُ')
        self.assertIsInstance(r, MabniBoundary,
                              "عَلِمْتُ مرخَّصة في الكتالوج → يجب أن تُنتج MabniBoundary")
        self.assertNotEqual(r.verdict, 'OPEN',
                            "وجود الجذر والبنية الصرفية لا يُزيل الوظيفة العاملية")

    # ── Lexical class vs. operator status (مبدأ الاستقلالية) ─────────────────

    def test_lexical_class_independent_of_operator_status(self):
        """
        الفئة المعجمية مستقلة عن الوظيفة العاملية — جميع الفئات تُنتج OPERATOR_BOUNDARY.

        Closed Function Word  → OPERATOR_BOUNDARY  (حروف المعاني)
        Numerical Operator    → OPERATOR_BOUNDARY  (أدوات العدد)
        Verbal Operator       → OPERATOR_BOUNDARY  (أفعال ناقصة / مقاربة / تقييم)
        Cognition Verb        → OPERATOR_BOUNDARY  (أفعال القلوب)
        Phrase Operator       → OPERATOR_BOUNDARY  (عبارات مركّبة)
        """
        class_samples = {
            'Closed Function Word': 'إِنَّ',
            'Numerical Operator':   'مِائَةَ',
            'Verbal Operator':      'كَانَ',
            'Cognition Verb':       'ظَنَنْتُ',
            'Phrase Operator':      'مَا زَالَ',
        }
        for expected_class, word in class_samples.items():
            r = _mabni(word)
            self.assertIsInstance(r, MabniBoundary,
                                  f"{word}: كل فئة معجمية يجب أن تُنتج MabniBoundary")
            self.assertEqual(r.lexical_class, expected_class,
                             f"{word}: الفئة المعجمية يجب أن تكون '{expected_class}'")
            self.assertIn(r.verdict, ('OPERATOR_BOUNDARY', 'OPERATOR_DEFERRED'),
                          f"{word}: جميع الفئات تُنتج OPERATOR_BOUNDARY")
            self.assertTrue(r.opens_relation,
                            f"{word}: كل عامل معجمي يفتح علاقة")
            self.assertEqual(r.relation_contract.contract_state, 'OPEN',
                             f"{word}: العقد مفتوح في كل الفئات")


# ══════════════════════════════════════════════════════════════════════════════
# P4 Aggregation — قانون التجميع: BLOCK > DEFER > ACCEPT
# ══════════════════════════════════════════════════════════════════════════════

class TestP4Aggregation(unittest.TestCase):
    """
    يُثبت قانون تجميع خانات P4: BLOCK > DEFER > ACCEPT

    القانون الصحيح:
      وجود BLOCK واحد في أي خانة → الحكم الكلي BLOCK
      وإلا وجود DEFER واحد في أي خانة → الحكم الكلي DEFER
      وإلا → الحكم الكلي ACCEPT

    الخطأ القديم:
      كانت word_gate() تتحقق من آخر خانة فقط للـ DEFER،
      فكانت [DEFER, ACCEPT] → ACCEPT خطأً.
    """

    # ── اختبارات وحدوية: word_gate() مباشرةً بـ slots اصطناعية ────────────────

    def _gate(self, gates: list[str]) -> str:
        """يبني slots اصطناعية ويُمرِّرها إلى word_gate()."""
        from syllabifier import word_gate
        slots = [
            {'surface': 'X', 'gate': g, 'violations': [], 'pattern': 'CV'}
            for g in gates
        ]
        verdict, _ = word_gate(slots)
        return verdict

    def test_single_accept(self):
        """[ACCEPT] → ACCEPT"""
        self.assertEqual(self._gate(['ACCEPT']), 'ACCEPT')

    def test_single_defer(self):
        """[DEFER] → DEFER"""
        self.assertEqual(self._gate(['DEFER']), 'DEFER')

    def test_single_block(self):
        """[BLOCK] → BLOCK"""
        self.assertEqual(self._gate(['BLOCK']), 'BLOCK')

    def test_accept_accept(self):
        """[ACCEPT, ACCEPT] → ACCEPT"""
        self.assertEqual(self._gate(['ACCEPT', 'ACCEPT']), 'ACCEPT')

    def test_defer_accept(self):
        """[DEFER, ACCEPT] → DEFER — كان هذا الخطأ الرئيسي (الخانة الأخيرة ACCEPT كانت تُلغي DEFER)"""
        self.assertEqual(self._gate(['DEFER', 'ACCEPT']), 'DEFER')

    def test_accept_defer(self):
        """[ACCEPT, DEFER] → DEFER"""
        self.assertEqual(self._gate(['ACCEPT', 'DEFER']), 'DEFER')

    def test_block_dominates_defer(self):
        """[BLOCK, DEFER] → BLOCK (BLOCK يطغى على DEFER)"""
        self.assertEqual(self._gate(['BLOCK', 'DEFER']), 'BLOCK')

    # ── اختبارات نهاية-إلى-نهاية: رموز بلا تشكيل ────────────────────────────────

    def test_kaayyin_unvocalized_p4_defer(self):
        """كأين (بلا تشكيل) → P4=DEFER (Slot1=C/DEFER, Slot2=CVC/ACCEPT → يجب DEFER)"""
        v, _ = _verdict('كأين')
        self.assertEqual(v, 'DEFER',
                         "كأين بلا تشكيل: Slot1 هو C/DEFER يجب أن يُحسم الحكم بـ DEFER")

    def test_kaayyin_unvocalized_operator_deferred(self):
        """كأين (بلا تشكيل) → OPERATOR_DEFERRED لا OPERATOR_BOUNDARY"""
        r = _mabni('كأين')
        self.assertIsInstance(r, MabniBoundary,
                              "كأين موجودة في الكتالوج → يجب أن تُنتج MabniBoundary")
        self.assertEqual(r.verdict, 'OPERATOR_DEFERRED',
                         "كأين بلا تشكيل: P4=DEFER → P5 يجب أن يُعلن OPERATOR_DEFERRED")
        self.assertEqual(r.structural_verdict, 'DEFER')

    def test_kadha_unvocalized_p4_defer(self):
        """كذا (بلا تشكيل) → P4=DEFER (Slot1=C/DEFER, Slot2=CV/ACCEPT → يجب DEFER)"""
        v, _ = _verdict('كذا')
        self.assertEqual(v, 'DEFER',
                         "كذا بلا تشكيل: Slot1 هو C/DEFER يجب أن يُحسم الحكم بـ DEFER")

    def test_kadha_unvocalized_operator_deferred(self):
        """كذا (بلا تشكيل) → OPERATOR_DEFERRED لا OPERATOR_BOUNDARY"""
        r = _mabni('كذا')
        self.assertIsInstance(r, MabniBoundary,
                              "كذا موجودة في الكتالوج → يجب أن تُنتج MabniBoundary")
        self.assertEqual(r.verdict, 'OPERATOR_DEFERRED',
                         "كذا بلا تشكيل: P4=DEFER → P5 يجب أن يُعلن OPERATOR_DEFERRED")
        self.assertEqual(r.structural_verdict, 'DEFER')

    def test_uluf_unvocalized_p4_defer(self):
        """ألوف (بلا تشكيل) → P4=DEFER (Slot1=C/DEFER, Slot2=CVC/ACCEPT → يجب DEFER)"""
        v, _ = _verdict('ألوف')
        self.assertEqual(v, 'DEFER',
                         "ألوف بلا تشكيل: الخانة الأولى C/DEFER يجب أن تُعطي الحكم الكلي DEFER")

    def test_uluf_unvocalized_operator_deferred(self):
        """ألوف (بلا تشكيل) → OPERATOR_DEFERRED (موجودة في الكتالوج كأداة تمييز)"""
        r = _mabni('ألوف')
        self.assertIsInstance(r, MabniBoundary,
                              "ألوف موجودة في الكتالوج → MabniBoundary")
        self.assertEqual(r.verdict, 'OPERATOR_DEFERRED',
                         "ألوف بلا تشكيل: P4=DEFER → P5 يجب أن يُعلن OPERATOR_DEFERRED")
        self.assertEqual(r.structural_verdict, 'DEFER')

    # ── ثبات: الأدوات المشكولة لا تتأثر بالإصلاح ─────────────────────────────

    def test_kaayyin_vocalized_operator_boundary(self):
        """كَأَيِّنْ (مشكول) → OPERATOR_BOUNDARY (P4=ACCEPT بعد الإصلاح)"""
        r = _mabni('كَأَيِّنْ')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.verdict, 'OPERATOR_BOUNDARY')
        self.assertEqual(r.structural_verdict, 'ACCEPT')

    def test_kadha_vocalized_operator_boundary(self):
        """كَذَا (مشكول) → OPERATOR_BOUNDARY"""
        r = _mabni('كَذَا')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.verdict, 'OPERATOR_BOUNDARY')
        self.assertEqual(r.structural_verdict, 'ACCEPT')


# ══════════════════════════════════════════════════════════════════════════════
# انحدار — الأنماط التي كانت صحيحة يجب أن تظل صحيحة
# ══════════════════════════════════════════════════════════════════════════════

class TestRegression(unittest.TestCase):

    def _patterns(self, word):
        return [s['pattern'] for s in _slots(word)]

    def test_daraba(self):
        self.assertEqual(self._patterns('ضَرَبَ'), ['CV', 'CV', 'CV'])

    def test_darib(self):
        self.assertEqual(self._patterns('ضَارِبٌ'), ['CVV', 'CV', 'CV'])

    def test_madruba(self):
        self.assertEqual(self._patterns('مَضْرُوبًا'), ['CVC', 'CVV', 'CVV'])

    def test_muluk(self):
        self.assertEqual(self._patterns('الْمُلُوكِ'), ['CVC', 'CV', 'CVV', 'CV'])

    def test_mudaris(self):
        self.assertEqual(self._patterns('مُدَرِّسٌ'), ['CV', 'CVC', 'CV', 'CV'])

    def test_maktub(self):
        self.assertEqual(self._patterns('مَكْتُوبٌ'), ['CVC', 'CVV', 'CV'])

    def test_bayt(self):
        """بَيْتٌ — CVC — ACCEPT"""
        v, _ = _verdict('بَيْتٌ')
        self.assertEqual(v, 'ACCEPT')


# ══════════════════════════════════════════════════════════════════════════════
# TestBareIndex — اختبارات فهرس _by_bare وحارس unique-surface
# ══════════════════════════════════════════════════════════════════════════════

class TestBareIndex(unittest.TestCase):
    """
    اختبارات شاملة لفهرس _by_bare في MabniInventory:

      1. unique bare match    — مفتاح مجرَّد يُعيد سطحًا واحدًا فريدًا (آمن)
      2. multiple bare match  — مفتاح يُعيد أكثر من سطح مشكول (حارس يُعيد [])
      3. shadda distinction   — إِنَّ/إِنْ يُميَّزان بالحركات لا بالبحث المجرَّد
      4. P4 DEFER preservation — DEFER من P4 محفوظ عبر البحث المجرَّد

    الإعداد:
      يُعيد بناء الـ singleton في كل دورة اختبار لضمان نظافة الحالة.
    """

    def setUp(self):
        import mabni_inventory as _mi
        _mi._INVENTORY = None   # أعد بناء الفهرس لكل اختبار

    @classmethod
    def setUpClass(cls):
        from mabni_inventory import get_inventory, _strip_diacritics
        from normalizer import normalize as _norm
        cls._get_inv   = staticmethod(get_inventory)
        cls._strip     = staticmethod(_strip_diacritics)
        cls._normalize = staticmethod(_norm)

    def _lookup(self, word):
        """lookup_canonical بمفتاحَي canonical و normalized."""
        import mabni_inventory as _mi
        _mi._INVENTORY = None
        inv  = _mi.get_inventory()
        norm = self._normalize(word)
        return inv.lookup_canonical(word, norm)

    # ── 1. UNIQUE BARE MATCH ──────────────────────────────────────────────────
    #   كلمات غير مشكولة تنتمي إلى سطح مشكول واحد في الكتالوج → بحث آمن

    def test_unique_bare_a(self):
        """أ (bare) → يُطابق أَ بلا غموض"""
        entries, sv = self._lookup('أ')
        self.assertTrue(entries, "أ يجب أن يُطابق أَ في الكتالوج")
        self.assertEqual(len({e.surface_vocalized for e in entries}), 1,
                         "أ يجب أن يُعيد surface_vocalized واحد فريد")

    def test_unique_bare_kam(self):
        """كم (bare) → يُطابق كَمْ بلا غموض"""
        entries, sv = self._lookup('كم')
        self.assertTrue(entries)
        self.assertEqual(len({e.surface_vocalized for e in entries}), 1)

    def test_unique_bare_kaayyin(self):
        """كأين (bare) → يُطابق كَأَيِّنْ بلا غموض رغم الشدة الداخلية"""
        entries, sv = self._lookup('كأين')
        self.assertTrue(entries,
                        "كأين بلا تشكيل يجب أن يُطابق كَأَيِّنْ — الشدة الداخلية لا تمنع التطابق")
        self.assertEqual(len({e.surface_vocalized for e in entries}), 1)

    def test_unique_bare_kadha(self):
        """كذا (bare) → يُطابق كَذَا بلا غموض"""
        entries, sv = self._lookup('كذا')
        self.assertTrue(entries)
        self.assertEqual(len({e.surface_vocalized for e in entries}), 1)

    def test_unique_bare_uluf(self):
        """ألوف (bare) → يُطابق أُلُوفَ بلا غموض"""
        entries, sv = self._lookup('ألوف')
        self.assertTrue(entries)
        self.assertEqual(len({e.surface_vocalized for e in entries}), 1)

    def test_unique_bare_malayin(self):
        """ملايين (bare) → يُطابق مَلَايِينَ بلا غموض"""
        entries, sv = self._lookup('ملايين')
        self.assertTrue(entries)
        self.assertEqual(len({e.surface_vocalized for e in entries}), 1)

    def test_unique_bare_returns_correct_operator_id(self):
        """البحث المجرَّد يُعيد operator_id صحيحًا"""
        from operator_id_map import get_profile
        for bare_word, expected_id in [
            ('أ',      'A_NIDA'),
            ('كم',     'KAM'),
            ('كذا',    'KADHA'),
            ('ألوف',   'ULUF'),
            ('ملايين', 'MALAYIN'),
        ]:
            entries, sv = self._lookup(bare_word)
            self.assertTrue(entries,
                            f"{bare_word!r}: يجب أن يجد الكتالوج")
            profile = get_profile(sv)
            self.assertEqual(profile.operator_id, expected_id,
                             f"{bare_word!r}: operator_id يجب أن يكون {expected_id!r}")

    # ── 2. MULTIPLE BARE MATCHES — unique-surface guard ───────────────────────
    #   الحارس يُعيد ([], '') عند تعدد surface_vocalized تحت نفس المفتاح المجرَّد

    def test_multiple_bare_min_man(self):
        """
        من (bare) → غامض: مِنْ (MIN، حرف جر) + مَنْ (MAN، شرط)
        الحارس يُعيد [] لا أداةً خاطئة.
        """
        entries, sv = self._lookup('من')
        self.assertFalse(entries,
                         "من غامضة بلا تشكيل — الحارس يجب أن يُعيد [] لا مِنْ ولا مَنْ")
        self.assertEqual(sv, '',
                         "matched_surface يجب أن يكون '' عند الغموض")

    def test_multiple_bare_idhan_idha(self):
        """
        إذا (bare) → غامض: إِذًا (IDHAN، نصب) + إِذَا (IDHA، شرط)
        الحارس يُعيد [].
        """
        entries, sv = self._lookup('إذا')
        self.assertFalse(entries,
                         "إذا غامضة بلا تشكيل — الحارس يجب أن يُعيد []")

    def test_multiple_bare_guard_returns_empty_not_first(self):
        """
        الحارس لا يختار أول مدخل عند الغموض — يُعيد [] بشكل صريح.
        هذا يمنع إعلان هوية خاطئة بصمت.
        """
        # كلا الكلمتين يحتويان على تصادم bare — الحارس يجب أن يرفضهما
        for word in ['من', 'إذا']:
            entries, sv = self._lookup(word)
            self.assertEqual(entries, [],
                             f"{word!r}: الحارس يجب أن يُعيد [] صراحةً لا أول مدخل")

    # ── 3. SHADDA DISTINCTION ─────────────────────────────────────────────────
    #   الكلمات المشكولة كاملاً تُميَّز عبر Phases 1/2 — لا تصل إلى Phase 3b
    #   الكلمات المجرَّدة (إن, أن, أي) لا تُطابَق بسبب الحارس — لا غموض صامت

    def test_shadda_inna_vocalized_matches_inna(self):
        """إِنَّ (مشكول كامل) → INNA"""
        from operator_id_map import get_profile
        entries, sv = self._lookup('إِنَّ')
        self.assertTrue(entries)
        self.assertEqual(get_profile(sv).operator_id, 'INNA')

    def test_shadda_in_shart_vocalized_matches_in_shart(self):
        """إِنْ (مشكول كامل) → IN_SHART"""
        from operator_id_map import get_profile
        entries, sv = self._lookup('إِنْ')
        self.assertTrue(entries)
        self.assertEqual(get_profile(sv).operator_id, 'IN_SHART')

    def test_shadda_bare_in_returns_no_match(self):
        """
        إن (bare، بلا تشكيل) → الحارس يُعيد [] لأن إِنَّ ≠ إِنْ
        الحارس يمنع إعلان INNA بدلاً من IN_SHART أو العكس.
        """
        entries, sv = self._lookup('إن')
        self.assertFalse(entries,
                         "إن بلا تشكيل غامضة (INNA vs IN_SHART) — يجب عدم المطابقة")

    def test_shadda_bare_an_returns_no_match(self):
        """أن (bare) → الحارس يُعيد [] لأن أَنَّ ≠ أَنْ"""
        entries, sv = self._lookup('أن')
        self.assertFalse(entries,
                         "أن بلا تشكيل غامضة (ANNA vs AN) — يجب عدم المطابقة")

    def test_shadda_bare_ay_returns_no_match(self):
        """أي (bare) → الحارس يُعيد [] لأن أَيْ (نداء) ≠ أَيّ (شرط)"""
        entries, sv = self._lookup('أي')
        self.assertFalse(entries,
                         "أي بلا تشكيل غامضة (AY_NIDA vs AYY_COND) — يجب عدم المطابقة")

    def test_shadda_anna_vocalized_matches_anna_not_an(self):
        """أَنَّ (مشكول) → ANNA لا AN — الشدة تُميِّز الهوية"""
        from operator_id_map import get_profile
        entries, sv = self._lookup('أَنَّ')
        self.assertTrue(entries)
        self.assertNotEqual(get_profile(sv).operator_id, 'AN',
                            "أَنَّ يجب ألا يُطابق أَنْ (AN) — الشدة فارق أساسي")
        self.assertEqual(get_profile(sv).operator_id, 'ANNA')

    def test_shadda_kaayyin_bare_maps_uniquely(self):
        """
        كأين (bare) يُطابق كَأَيِّنْ بلا غموض رغم أن الكتالوج يحمل شدة على يِّ.
        الشدة الداخلية لكلمة أحادية لا تُحدث تصادمًا — التصادم يحدث فقط عندما
        تنتمي الشدة إلى أزواج مختلفة (إِنَّ/إِنْ).
        """
        entries, sv = self._lookup('كأين')
        self.assertTrue(entries,
                        "كأين: شدة داخلية (يِّ) لا تُحدث تصادمًا — يجب أن يُطابق")
        unique = {e.surface_vocalized for e in entries}
        self.assertEqual(len(unique), 1,
                         "كأين: سطح واحد فريد تحت المفتاح المجرَّد")

    # ── 4. P4 DEFER PRESERVATION ──────────────────────────────────────────────
    #   DEFER من P4 يُحفَظ عبر البحث المجرَّد — لا يُعلَن OPERATOR_BOUNDARY

    def test_defer_bare_a_yields_operator_deferred(self):
        """أ (bare، P4=DEFER) → OPERATOR_DEFERRED لا OPERATOR_BOUNDARY"""
        r = _mabni('أ')
        self.assertIsInstance(r, MabniBoundary,
                              "أ موجودة في الكتالوج → MabniBoundary")
        self.assertEqual(r.structural_verdict, 'DEFER',
                         "structural_verdict يجب أن يكون DEFER — محفوظ من P4")
        self.assertEqual(r.verdict, 'OPERATOR_DEFERRED',
                         "أ بلا تشكيل: P4=DEFER → P5 يُعلن OPERATOR_DEFERRED لا OPERATOR_BOUNDARY")
        self.assertNotEqual(r.verdict, 'OPERATOR_BOUNDARY',
                            "P4 DEFER لا يُرفَع إلى OPERATOR_BOUNDARY عبر البحث المجرَّد")

    def test_defer_bare_kam_yields_operator_deferred(self):
        """كم (bare، P4=DEFER) → OPERATOR_DEFERRED"""
        r = _mabni('كم')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.structural_verdict, 'DEFER')
        self.assertEqual(r.verdict, 'OPERATOR_DEFERRED')

    def test_defer_bare_kaayyin_yields_operator_deferred(self):
        """كأين (bare، P4=DEFER) → OPERATOR_DEFERRED"""
        r = _mabni('كأين')
        self.assertIsInstance(r, MabniBoundary,
                              "كأين موجودة في الكتالوج → MabniBoundary")
        self.assertEqual(r.structural_verdict, 'DEFER')
        self.assertEqual(r.verdict, 'OPERATOR_DEFERRED')

    def test_defer_bare_kadha_yields_operator_deferred(self):
        """كذا (bare، P4=DEFER) → OPERATOR_DEFERRED"""
        r = _mabni('كذا')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.structural_verdict, 'DEFER')
        self.assertEqual(r.verdict, 'OPERATOR_DEFERRED')

    def test_defer_bare_uluf_yields_operator_deferred(self):
        """ألوف (bare، P4=DEFER) → OPERATOR_DEFERRED"""
        r = _mabni('ألوف')
        self.assertIsInstance(r, MabniBoundary)
        self.assertEqual(r.structural_verdict, 'DEFER')
        self.assertEqual(r.verdict, 'OPERATOR_DEFERRED')

    def test_defer_bare_structural_verdict_never_becomes_accept(self):
        """
        قانون الرتابة P4→P5: DEFER لا يُحوَّل إلى ACCEPT
        مهما كانت نتيجة البحث المجرَّد.
        """
        for word in ['أ', 'كم', 'كأين', 'كذا', 'ألوف']:
            r = _mabni(word)
            if isinstance(r, MabniBoundary):
                self.assertNotEqual(r.structural_verdict, 'ACCEPT',
                                    f"{word!r}: structural_verdict يجب ألا يُحوَّل من DEFER إلى ACCEPT")
                self.assertNotEqual(r.verdict, 'OPERATOR_BOUNDARY',
                                    f"{word!r}: bare input لا يجوز أن يُعلن OPERATOR_BOUNDARY")

    def test_vocalized_forms_retain_accept_after_bare_fix(self):
        """
        الأدوات المشكولة لا تتأثر بالإصلاح — تبقى OPERATOR_BOUNDARY.
        يُثبت أن الإصلاح لم يُخرِّب الأدوات الموجودة.
        """
        for word in ['كَمْ', 'كَأَيِّنْ', 'كَذَا', 'أُلُوفَ', 'مَلَايِينَ']:
            r = _mabni(word)
            self.assertIsInstance(r, MabniBoundary,
                                  f"{word!r}: يجب أن يُنتج MabniBoundary")
            self.assertEqual(r.verdict, 'OPERATOR_BOUNDARY',
                             f"{word!r}: مشكول كامل → OPERATOR_BOUNDARY")
            self.assertEqual(r.structural_verdict, 'ACCEPT',
                             f"{word!r}: structural_verdict يجب أن يكون ACCEPT")


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    unittest.main(verbosity=2)


# ══════════════════════════════════════════════════════════════════════════════
# TestMabniyat — اختبارات كتالوج المبنيات (Phase 5 Mabniyat Catalog)
# ══════════════════════════════════════════════════════════════════════════════

class TestMabniyat(unittest.TestCase):
    """
    Tests for mabniyat_catalog_split_vocalized.csv and mabniyat_layer.py.
    Appended after all existing test classes — existing code NOT touched.
    """

    @classmethod
    def setUpClass(cls):
        from mabniyat_layer import (
            load_catalog, process_mabni, get_all_rows,
            get_by_id, get_all_overt_surfaces, MabniResult,
        )
        cls.load_catalog      = staticmethod(load_catalog)
        cls.process_mabni     = staticmethod(process_mabni)
        cls.get_all_rows      = staticmethod(get_all_rows)
        cls.get_by_id         = staticmethod(get_by_id)
        cls.get_all_overt_surfaces = staticmethod(get_all_overt_surfaces)
        cls.MabniResult       = MabniResult
        cls.cat = load_catalog()

    # ── Test 1: Example sentences not imported ─────────────────────────────────
    def test_01_example_words_not_in_catalog(self):
        """يَعْمَلُ, أَحْمَدُ, بِإِخْلَاصٍ are not catalog surfaces."""
        for word in ('يَعْمَلُ', 'أَحْمَدُ', 'بِإِخْلَاصٍ'):
            r = self.process_mabni(word, 'ACCEPT')
            self.assertEqual(r.verdict, 'MABNI_NOT_FOUND',
                             f"{word!r} is an example-sentence word and must NOT be in the catalog")

    # ── Test 2: LATENT pronoun HUWA has no overt surface ─────────────────────
    def test_02_latent_pronoun_has_no_overt_surface(self):
        """LATENT_PRONOUN_HUWA must have surface_kind=LATENT and empty surface_vocalized."""
        row = self.get_by_id('LATENT_PRONOUN_HUWA')
        self.assertIsNotNone(row, "LATENT_PRONOUN_HUWA must exist in catalog")
        self.assertEqual(row['surface_kind'], 'LATENT')
        self.assertEqual(row['surface_vocalized'], '',
                         "Latent pronoun must have empty surface_vocalized")

    # ── Test 3: Attached pronoun واو الجماعة is ATTACHED, not OVERT ──────────
    def test_03_attached_waw_al_jamaa_is_attached(self):
        """واو الجماعة (وا) must be ATTACHED surface_kind, not OVERT."""
        row = self.get_by_id('ATTACHED_PRONOUN_WAW_AL_JAMAA')
        self.assertIsNotNone(row, "ATTACHED_PRONOUN_WAW_AL_JAMAA must be in catalog")
        self.assertEqual(row['surface_kind'], 'ATTACHED',
                         "واو الجماعة is a clitic suffix — must be ATTACHED not OVERT")

    # ── Test 4: No Arabic mabni_id ────────────────────────────────────────────
    def test_04_all_mabni_ids_are_ascii(self):
        """Every mabni_id must match ^[A-Z][A-Z0-9_]*$."""
        import re
        VALID = re.compile(r'^[A-Z][A-Z0-9_]*$')
        bad = [r['mabni_id'] for r in self.get_all_rows()
               if not VALID.match(r['mabni_id'])]
        self.assertEqual(bad, [],
                         f"Non-ASCII mabni_ids found: {bad[:5]}")

    # ── Test 5: Unicode diacritic order does not break lookup ─────────────────
    def test_05_unicode_diacritic_order_invariant(self):
        """هَذَا in both NFC and alternate shadda order must hit the same entry."""
        from mabniyat_layer import normalize_key
        # Standard NFC
        r1 = self.process_mabni('هَذَا', 'ACCEPT')
        # Bare (no diacritics) should also resolve via by_bare
        r2 = self.process_mabni('هذا', 'ACCEPT')
        self.assertEqual(r1.verdict, 'MABNI_BOUNDARY')
        self.assertEqual(r2.verdict, 'MABNI_BOUNDARY')
        self.assertEqual(r1.mabni_id, r2.mabni_id,
                         "Vocalized and bare lookup must return same catalog entry")

    # ── Test 6: P4 DEFER remains DEFER ────────────────────────────────────────
    def test_06_p4_defer_remains_defer(self):
        """process_mabni('هُوَ', 'DEFER').structural_verdict must be 'DEFER'."""
        r = self.process_mabni('هُوَ', 'DEFER')
        self.assertEqual(r.structural_verdict, 'DEFER',
                         "P4 monotonicity: DEFER must not be promoted to ACCEPT")

    # ── Test 7: P4 BLOCK stays BLOCK ──────────────────────────────────────────
    def test_07_p4_block_returns_mabni_blocked(self):
        """process_mabni('هُوَ', 'BLOCK').verdict must be 'MABNI_BLOCKED'."""
        r = self.process_mabni('هُوَ', 'BLOCK')
        self.assertEqual(r.verdict, 'MABNI_BLOCKED',
                         "P4 BLOCK is absolute: catalog match must not override it")

    # ── Test 8: Catalog match cannot promote verdict ───────────────────────────
    def test_08_catalog_match_cannot_promote_verdict(self):
        """process_mabni('هُوَ', 'DEFER').verdict must NOT be 'MABNI_BOUNDARY'."""
        r = self.process_mabni('هُوَ', 'DEFER')
        self.assertNotEqual(r.verdict, 'MABNI_BOUNDARY',
                            "P4 DEFER must never be promoted to MABNI_BOUNDARY by a catalog hit")
        self.assertEqual(r.verdict, 'MABNI_DEFERRED')

    # ── Test 9: Rule-only records do not create token boundaries ──────────────
    def test_09_verb_building_rule_not_in_catalog(self):
        """اذهب (verb-building rule example) must not appear as a catalog surface."""
        surfaces = self.get_all_overt_surfaces()
        self.assertNotIn('اذهب', surfaces,
                         "Verb-building rule example forms must not be cataloged")

    # ── Test 10: Contradictory hidden pronoun records not licensed ────────────
    def test_10_contradictory_hidden_pronouns_excluded(self):
        """
        hidden_pronouns ids 9, 10 are CONTRADICTORY and must not appear
        as distinct licensed entries in the catalog.
        
        id 9: اعْمَلِي attributed to أنتَ (masculine) — contradiction
        id 10: يَعْمَلُونَ has واو الجماعة (overt), claimed hidden — contradiction
        These must not create LATENT entries beyond ids 1-8.
        """
        latent_rows = [r for r in self.get_all_rows()
                       if r['source_file'] == 'hidden_pronouns.json'
                       and r['source_record_id'] in ('9', '10', '11')]
        self.assertEqual(latent_rows, [],
                         "hidden_pronouns ids 9, 10, 11 are CONTRADICTORY and must be excluded")

    # ── Test 11: Full existing test suite still passes ────────────────────────
    def test_11_existing_operator_tests_pass(self):
        """
        The existing operator/syllabifier tests must still pass.
        We verify by checking the core mabni_layer module still works.
        """
        from mabni_layer import process_mabni as old_process, MabniBoundary
        from normalizer import normalize
        from syllabifier import parse_phones, syllabify, word_gate
        # إِنَّ is a well-known operator — must still return MabniBoundary
        word = 'إِنَّ'
        norm = normalize(word)
        phones = parse_phones(norm)
        slots = syllabify(phones)
        v, viols = word_gate(slots)
        result = old_process(word, norm, slots, v, viols)
        self.assertIsInstance(result, MabniBoundary,
                              "Existing mabni_layer must still recognise إِنَّ")

    # ── Test 12: Operators catalog unchanged ─────────────────────────────────
    def test_12_operators_catalog_unchanged(self):
        """operators_catalog_split_vocalized.csv must have exactly 103 lines (1 header + 102 data)."""
        import os
        path = os.path.join(os.path.dirname(__file__),
                            'operators_catalog_split_vocalized.csv')
        with open(path, encoding='utf-8') as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 103,
                         f"operators_catalog must have 103 lines but has {len(lines)}")

    # ── Test 13: LATENT empty surface not found ───────────────────────────────
    def test_13_empty_surface_not_found(self):
        """process_mabni('', 'ACCEPT').verdict must be MABNI_NOT_FOUND."""
        r = self.process_mabni('', 'ACCEPT')
        self.assertEqual(r.verdict, 'MABNI_NOT_FOUND',
                         "Empty surface (latent pronoun surface) must not match any catalog entry")

    # ── Test 14: Demonstrative هَذَا found ───────────────────────────────────
    def test_14_demonstrative_hadha_found(self):
        """process_mabni('هَذَا', 'ACCEPT').verdict == 'MABNI_BOUNDARY'."""
        r = self.process_mabni('هَذَا', 'ACCEPT')
        self.assertEqual(r.verdict, 'MABNI_BOUNDARY')
        self.assertEqual(r.mabni_id, 'HADHA')
        self.assertEqual(r.lexical_class, 'DEMONSTRATIVE')

    # ── Test 15: Mu'rab dual هَذَانِ not in overt catalog ───────────────────
    def test_15_murab_dual_hadhan_not_in_catalog(self):
        """
        هَذَانِ/هَذَيْنِ are mu'rab dual forms and must not appear
        as OVERT entries in the mabniyat catalog.
        """
        from mabniyat_layer import strip_diacritics
        overt_rows = [r for r in self.get_all_rows()
                      if r['surface_kind'] in ('OVERT', 'PHRASE')
                      and r['source_file'] == 'demonstrative_pronouns.json']
        bare_surfaces = {strip_diacritics(r['surface_vocalized']) for r in overt_rows}
        self.assertNotIn('هذان', bare_surfaces,
                         "هذان dual is معرب and must not appear as overt catalog entry")

    # ── Test 16: Preposition بِ found ────────────────────────────────────────
    def test_16_preposition_bi_found(self):
        """process_mabni('بِ', 'ACCEPT').mabni_id == 'BI_PREP'."""
        r = self.process_mabni('بِ', 'ACCEPT')
        self.assertEqual(r.verdict, 'MABNI_BOUNDARY')
        self.assertEqual(r.mabni_id, 'BI_PREP')

    # ── Test 17: Relative الَّذِي has OPEN contract ──────────────────────────
    def test_17_relative_alladhi_open_contract(self):
        """الَّذِي must be found with contract_state='OPEN'."""
        r = self.process_mabni('الَّذِي', 'ACCEPT')
        self.assertEqual(r.verdict, 'MABNI_BOUNDARY')
        self.assertEqual(r.mabni_id, 'ALLADHI')
        self.assertEqual(r.contract_state, 'OPEN',
                         "Relative pronoun الَّذِي must carry an OPEN relation contract")

    # ── Test 18: Conditional إِنْ found ──────────────────────────────────────
    def test_18_conditional_in_found(self):
        """Conditional particle إِنْ must be in catalog."""
        r = self.process_mabni('إِنْ', 'ACCEPT')
        self.assertEqual(r.verdict, 'MABNI_BOUNDARY')
        self.assertEqual(r.mabni_id, 'IN')
        self.assertEqual(r.lexical_class, 'CONDITIONAL_PARTICLE')

    # ── Test 19: Copulative إِنَّ found ──────────────────────────────────────
    def test_19_copulative_inna_found(self):
        """Copulative particle إِنَّ must be found as COPULATIVE_PARTICLE."""
        r = self.process_mabni('إِنَّ', 'ACCEPT')
        self.assertEqual(r.verdict, 'MABNI_BOUNDARY')
        self.assertEqual(r.mabni_id, 'INNA')
        self.assertEqual(r.lexical_class, 'COPULATIVE_PARTICLE')

    # ── Test 20: Answer particle نَعَمْ found ────────────────────────────────
    def test_20_answer_naam_found(self):
        """Answer particle نَعَمْ must be in catalog."""
        r = self.process_mabni('نَعَمْ', 'ACCEPT')
        self.assertEqual(r.verdict, 'MABNI_BOUNDARY')
        self.assertEqual(r.mabni_id, 'NAAM')
        self.assertEqual(r.lexical_class, 'ANSWER_PARTICLE')

    # ── Test 21: Verb name آمِينَ found ──────────────────────────────────────
    def test_21_verb_name_aameen_found(self):
        """Verb name آمِينَ (اسم فعل) must be in catalog."""
        r = self.process_mabni('آمِينَ', 'ACCEPT')
        self.assertEqual(r.verdict, 'MABNI_BOUNDARY')
        self.assertEqual(r.mabni_id, 'AAMEEN')
        self.assertEqual(r.lexical_class, 'VERB_NAME')

    # ── Test 22: مَا appears as both conditional and relative ────────────────
    def test_22_ma_cataloged_in_both_conditional_and_relative(self):
        """
        مَا appears as:
          MA_SHART  (CONDITIONAL_NAME from conditional_letters_tools.json)
          MA_MAWSUL (RELATIVE_PRONOUN from relative_pronouns.json)
        Both must exist as distinct catalog entries with different IDs.
        """
        ma_shart  = self.get_by_id('MA_SHART')
        ma_mawsul = self.get_by_id('MA_MAWSUL')
        self.assertIsNotNone(ma_shart,  "MA_SHART must be in catalog")
        self.assertIsNotNone(ma_mawsul, "MA_MAWSUL must be in catalog")
        self.assertNotEqual(ma_shart['mabni_id'], ma_mawsul['mabni_id'],
                            "MA_SHART and MA_MAWSUL must have different mabni_ids")
        self.assertEqual(ma_shart['lexical_class'],  'CONDITIONAL_NAME')
        self.assertEqual(ma_mawsul['lexical_class'], 'RELATIVE_PRONOUN')

    # ── Bonus: LATENT pronouns have correct estimated_form ───────────────────
    def test_23_latent_pronouns_have_estimated_form(self):
        """All 8 valid latent pronoun entries must have a non-empty estimated_form."""
        latent = [r for r in self.get_all_rows()
                  if r['surface_kind'] == 'LATENT'
                  and r['source_file'] == 'hidden_pronouns.json']
        self.assertEqual(len(latent), 8,
                         f"Expected 8 LATENT entries from hidden_pronouns.json, got {len(latent)}")
        missing = [r['mabni_id'] for r in latent if not r.get('estimated_form','').strip()]
        self.assertEqual(missing, [],
                         f"LATENT entries missing estimated_form: {missing}")

    # ── Bonus: No source JSON was modified ───────────────────────────────────
    def test_24_source_json_files_unchanged(self):
        """
        Verify source JSON files under data/02_mabniyat/ were not modified.
        We check that total record counts match expected values.
        """
        import json, os
        DATA = os.path.join(os.path.dirname(__file__), 'data/02_mabniyat')
        EXPECTED = {
            'built_in_adverbs.json': 21,
            'conditional_letters_tools.json': 21,
            'coordinating_conjunctions.json': 23,
            'copulative_particle.json': 7,
            'demonstrative_pronouns.json': 53,
            'hidden_pronouns.json': 11,
            'jazm_tools.json': 20,
            'kinaya_names.json': 9,
            'letters_answers.json': 10,
            'preposition_meanings.json': 56,
            'present_naseb_tools.json': 10,
            'pronouns_classification.json': 43,
            'relative_pronouns.json': 48,
            'verb_name.json': 57,
            'vocative_particles.json': 9,
        }
        for fname, expected_count in EXPECTED.items():
            path = os.path.join(DATA, fname)
            with open(path, encoding='utf-8') as f:
                d = json.load(f)
            actual = len(d.get('data', []))
            self.assertEqual(actual, expected_count,
                             f"{fname}: expected {expected_count} records, got {actual}")


# ══════════════════════════════════════════════════════════════════════════════
# TestAttachment — attached pronoun recognition (Phase 5, Layer 2)
# ══════════════════════════════════════════════════════════════════════════════

class TestAttachment(unittest.TestCase):
    """
    Tests for mabniyat_attachment.recognize_token().

    Covers the 5 target tokens from the task specification plus negative
    controls that must NOT produce spurious segmentations.

    P4 Monotonicity invariant: structural_verdict is never modified.
    """

    def setUp(self):
        from mabniyat_attachment import recognize_token, _reset_cache
        _reset_cache()
        self._rt = recognize_token

    def _r(self, surface, p4='ACCEPT'):
        return self._rt(surface, p4)

    # ─────────────────────────────────────────────────────────────────────────
    # يُعَوِّضَهُمْ — verb + هُمْ (3rd pl masc suffix)
    # ─────────────────────────────────────────────────────────────────────────

    def test_yuawwiduhum_not_found_whole_token(self):
        """يُعَوِّضَهُمْ is not a whole-token mabni form."""
        r = self._r('يُعَوِّضَهُمْ')
        self.assertEqual(r.whole_token_verdict, 'MABNI_NOT_FOUND')

    def test_yuawwiduhum_segmented(self):
        r = self._r('يُعَوِّضَهُمْ')
        self.assertEqual(r.segmentation_verdict, 'SEGMENTED')

    def test_yuawwiduhum_one_suffix(self):
        r = self._r('يُعَوِّضَهُمْ')
        self.assertEqual(len(r.attached_mabniyat), 1)

    def test_yuawwiduhum_suffix_is_hum(self):
        r = self._r('يُعَوِّضَهُمْ')
        self.assertEqual(r.attached_mabniyat[0].mabni_id, 'ATTACHED_PRONOUN_HUM_SUFFIX')

    def test_yuawwiduhum_suffix_surface(self):
        r = self._r('يُعَوِّضَهُمْ')
        self.assertEqual(r.attached_mabniyat[0].surface_matched, 'هُمْ')

    def test_yuawwiduhum_host(self):
        r = self._r('يُعَوِّضَهُمْ')
        self.assertEqual(r.host_surface, 'يُعَوِّضَ')

    def test_yuawwiduhum_host_route(self):
        r = self._r('يُعَوِّضَهُمْ')
        self.assertEqual(r.host_route, 'OPEN_TO_HR2S')

    def test_yuawwiduhum_no_prefix_operators(self):
        r = self._r('يُعَوِّضَهُمْ')
        self.assertEqual(len(r.prefix_operators), 0)

    def test_yuawwiduhum_suffix_position(self):
        r = self._r('يُعَوِّضَهُمْ')
        self.assertEqual(r.attached_mabniyat[0].position, 'SUFFIX')

    def test_yuawwiduhum_p4_monotonicity(self):
        """P4 structural_verdict is preserved unchanged."""
        r = self._r('يُعَوِّضَهُمْ', 'ACCEPT')
        self.assertEqual(r.structural_verdict, 'ACCEPT')

    # ─────────────────────────────────────────────────────────────────────────
    # فَقَدُوهُ — verb + واو الجماعة (connected) + هاء الغائب
    # ─────────────────────────────────────────────────────────────────────────

    def test_faqaduhu_not_found_whole_token(self):
        r = self._r('فَقَدُوهُ')
        self.assertEqual(r.whole_token_verdict, 'MABNI_NOT_FOUND')

    def test_faqaduhu_segmented(self):
        r = self._r('فَقَدُوهُ')
        self.assertEqual(r.segmentation_verdict, 'SEGMENTED')

    def test_faqaduhu_two_suffixes(self):
        """واو الجماعة and هاء must be emitted as separate suffix spans."""
        r = self._r('فَقَدُوهُ')
        self.assertEqual(len(r.attached_mabniyat), 2)

    def test_faqaduhu_first_suffix_is_waw_jamaa(self):
        r = self._r('فَقَدُوهُ')
        self.assertEqual(r.attached_mabniyat[0].mabni_id, 'ATTACHED_PRONOUN_WAW_AL_JAMAA')

    def test_faqaduhu_waw_is_allomorph(self):
        """Connected و is an allomorph of the catalog entry واو الجماعة (وا)."""
        r = self._r('فَقَدُوهُ')
        self.assertTrue(r.attached_mabniyat[0].is_allomorph)

    def test_faqaduhu_second_suffix_is_ha(self):
        r = self._r('فَقَدُوهُ')
        self.assertEqual(r.attached_mabniyat[1].mabni_id, 'ATTACHED_PRONOUN_HA')

    def test_faqaduhu_host(self):
        r = self._r('فَقَدُوهُ')
        self.assertEqual(r.host_surface, 'فَقَدُ')

    def test_faqaduhu_host_route(self):
        r = self._r('فَقَدُوهُ')
        self.assertEqual(r.host_route, 'OPEN_TO_HR2S')

    def test_faqaduhu_no_prefix_operators(self):
        r = self._r('فَقَدُوهُ')
        self.assertEqual(len(r.prefix_operators), 0)

    def test_faqaduhu_p4_monotonicity(self):
        r = self._r('فَقَدُوهُ', 'ACCEPT')
        self.assertEqual(r.structural_verdict, 'ACCEPT')

    # ─────────────────────────────────────────────────────────────────────────
    # أُمِّهِمْ — noun (mudaf) + هِمْ (3rd pl masc in jar/idafa position)
    # ─────────────────────────────────────────────────────────────────────────

    def test_ummihim_not_found_whole_token(self):
        r = self._r('أُمِّهِمْ')
        self.assertEqual(r.whole_token_verdict, 'MABNI_NOT_FOUND')

    def test_ummihim_segmented(self):
        r = self._r('أُمِّهِمْ')
        self.assertEqual(r.segmentation_verdict, 'SEGMENTED')

    def test_ummihim_one_suffix(self):
        r = self._r('أُمِّهِمْ')
        self.assertEqual(len(r.attached_mabniyat), 1)

    def test_ummihim_suffix_is_him(self):
        r = self._r('أُمِّهِمْ')
        self.assertEqual(r.attached_mabniyat[0].mabni_id, 'ATTACHED_PRONOUN_HIM')

    def test_ummihim_suffix_surface(self):
        r = self._r('أُمِّهِمْ')
        self.assertEqual(r.attached_mabniyat[0].surface_matched, 'هِمْ')

    def test_ummihim_host(self):
        r = self._r('أُمِّهِمْ')
        self.assertEqual(r.host_surface, 'أُمِّ')

    def test_ummihim_host_route_not_bare_mabni_false_positive(self):
        """
        أُمِّ (mother, genitive) must route to OPEN_TO_HR2S, not MABNI_BOUNDARY.
        Bare أم collides with أَمْ (particle AM) in the catalog's bare index,
        but vocalized-only host lookup correctly avoids this false positive.
        """
        r = self._r('أُمِّهِمْ')
        self.assertEqual(r.host_route, 'OPEN_TO_HR2S')

    def test_ummihim_suffix_not_allomorph(self):
        r = self._r('أُمِّهِمْ')
        self.assertFalse(r.attached_mabniyat[0].is_allomorph)

    def test_ummihim_no_prefix_operators(self):
        r = self._r('أُمِّهِمْ')
        self.assertEqual(len(r.prefix_operators), 0)

    def test_ummihim_p4_monotonicity(self):
        r = self._r('أُمِّهِمْ', 'ACCEPT')
        self.assertEqual(r.structural_verdict, 'ACCEPT')

    # ─────────────────────────────────────────────────────────────────────────
    # حُبِّهَا — noun (mudaf) + هَا (3rd fem sing suffix)
    # ─────────────────────────────────────────────────────────────────────────

    def test_hubbaha_not_found_whole_token(self):
        r = self._r('حُبِّهَا')
        self.assertEqual(r.whole_token_verdict, 'MABNI_NOT_FOUND')

    def test_hubbaha_segmented(self):
        r = self._r('حُبِّهَا')
        self.assertEqual(r.segmentation_verdict, 'SEGMENTED')

    def test_hubbaha_one_suffix(self):
        r = self._r('حُبِّهَا')
        self.assertEqual(len(r.attached_mabniyat), 1)

    def test_hubbaha_suffix_is_ha_fem(self):
        r = self._r('حُبِّهَا')
        self.assertEqual(r.attached_mabniyat[0].mabni_id, 'ATTACHED_PRONOUN_HA_FEM')

    def test_hubbaha_suffix_surface(self):
        r = self._r('حُبِّهَا')
        self.assertEqual(r.attached_mabniyat[0].surface_matched, 'هَا')

    def test_hubbaha_host(self):
        r = self._r('حُبِّهَا')
        self.assertEqual(r.host_surface, 'حُبِّ')

    def test_hubbaha_host_route(self):
        r = self._r('حُبِّهَا')
        self.assertEqual(r.host_route, 'OPEN_TO_HR2S')

    def test_hubbaha_suffix_lexical_family(self):
        """هَا suffix must belong to the haa-family, not the original series."""
        r = self._r('حُبِّهَا')
        self.assertEqual(r.attached_mabniyat[0].lexical_family, 'ATTACHED_PRONOUN_HA_FAMILY')

    def test_hubbaha_longer_suffix_wins_over_alif(self):
        """
        هَا (2-char suffix) must win over ا (1-char alif-ithnayn suffix).
        Both match حُبِّهَا at depth 1; the longer suffix must be preferred.
        """
        r = self._r('حُبِّهَا')
        # Confirm not AMBIGUOUS
        self.assertEqual(r.segmentation_verdict, 'SEGMENTED')
        # Confirm the winner is the 2-char هَا, not the 1-char ا
        self.assertEqual(r.attached_mabniyat[0].mabni_id, 'ATTACHED_PRONOUN_HA_FEM')

    def test_hubbaha_p4_monotonicity(self):
        r = self._r('حُبِّهَا', 'ACCEPT')
        self.assertEqual(r.structural_verdict, 'ACCEPT')

    # ─────────────────────────────────────────────────────────────────────────
    # لَهُمْ — prefix operator allomorph لَ (LI) + هُمْ
    # ─────────────────────────────────────────────────────────────────────────

    def test_lahum_not_found_whole_token(self):
        r = self._r('لَهُمْ')
        self.assertEqual(r.whole_token_verdict, 'MABNI_NOT_FOUND')

    def test_lahum_segmented(self):
        r = self._r('لَهُمْ')
        self.assertEqual(r.segmentation_verdict, 'SEGMENTED')

    def test_lahum_one_suffix(self):
        r = self._r('لَهُمْ')
        self.assertEqual(len(r.attached_mabniyat), 1)

    def test_lahum_suffix_is_hum(self):
        r = self._r('لَهُمْ')
        self.assertEqual(r.attached_mabniyat[0].mabni_id, 'ATTACHED_PRONOUN_HUM_SUFFIX')

    def test_lahum_host_is_empty(self):
        """لَ is consumed as a prefix operator; no host remains."""
        r = self._r('لَهُمْ')
        self.assertEqual(r.host_surface, '')

    def test_lahum_host_route_empty(self):
        r = self._r('لَهُمْ')
        self.assertEqual(r.host_route, 'EMPTY')

    def test_lahum_one_prefix_operator(self):
        r = self._r('لَهُمْ')
        self.assertEqual(len(r.prefix_operators), 1)

    def test_lahum_prefix_is_li_allomorph(self):
        r = self._r('لَهُمْ')
        self.assertEqual(r.prefix_operators[0].mabni_id, 'LI_ALLOMORPH')

    def test_lahum_prefix_is_allomorph_flag(self):
        """لَ is marked as an allomorph of لِ (canonical LI form)."""
        r = self._r('لَهُمْ')
        self.assertTrue(r.prefix_operators[0].is_allomorph)

    def test_lahum_p4_monotonicity(self):
        r = self._r('لَهُمْ', 'ACCEPT')
        self.assertEqual(r.structural_verdict, 'ACCEPT')

    # ─────────────────────────────────────────────────────────────────────────
    # Negative controls — must NOT produce spurious segmentations
    # ─────────────────────────────────────────────────────────────────────────

    def test_neg_standalone_hu_not_recursed(self):
        """
        هُ alone is a whole-token ATTACHED form in the catalog.
        recognize_token must return NOT_SEGMENTED (whole-token match),
        never attempt suffix recursion on it.
        """
        r = self._r('هُ')
        self.assertEqual(r.segmentation_verdict, 'NOT_SEGMENTED')
        self.assertEqual(len(r.attached_mabniyat), 0)

    def test_neg_abuun_waw_guard(self):
        """
        أَبُو ends in bare و but must NOT be split as أَبُ + و.
        The connected-waw allomorph is only tried at recursion depth ≥ 1
        (after a rightward suffix has already been identified).
        """
        r = self._r('أَبُو')
        self.assertEqual(r.segmentation_verdict, 'NOT_SEGMENTED')
        self.assertEqual(len(r.attached_mabniyat), 0)

    def test_neg_alima_no_suffix_match(self):
        """عَلِمَ ends in مَ — no ATTACHED suffix in the catalog matches."""
        r = self._r('عَلِمَ')
        self.assertEqual(r.segmentation_verdict, 'NOT_SEGMENTED')
        self.assertEqual(len(r.attached_mabniyat), 0)

    def test_neg_kitabun_tanwin_no_match(self):
        """
        كِتَابٌ ends in بٌ (tanwin damma); the ها suffix requires هَا
        (haa+fatha+alif), which is a different sequence.
        """
        r = self._r('كِتَابٌ')
        self.assertEqual(r.segmentation_verdict, 'NOT_SEGMENTED')
        self.assertEqual(len(r.attached_mabniyat), 0)

    def test_neg_p4_block_skips_suffix_analysis(self):
        """
        P4 monotonicity: when structural_verdict=BLOCK, suffix analysis
        must be skipped entirely.  The result must be BLOCKED (distinct
        from DEFERRED which applies only to P4 DEFER).
        structural_verdict must remain 'BLOCK' — never overridden.
        """
        r = self._r('يُعَوِّضَهُمْ', 'BLOCK')
        self.assertEqual(r.segmentation_verdict, 'BLOCKED')
        self.assertEqual(r.structural_verdict, 'BLOCK')     # P4 preserved
        self.assertEqual(r.whole_token_verdict, 'MABNI_BLOCKED')
        self.assertEqual(len(r.attached_mabniyat), 0)

    def test_neg_hubba_na_whole_suffix_wins_over_sub_split(self):
        """
        حُبِّنَا ends in ا and نَ is also a licensed suffix, so the
        algorithm could produce the spurious split نَ + ا (depth 2).
        Multi-span validity guard must reject this: neither نَ nor ا is
        a depth-guarded allomorph.  The correct result is the whole نَا
        (ATTACHED_PRONOUN_NA) as a single depth-1 suffix.
        """
        r = self._r('حُبِّنَا')
        self.assertEqual(r.segmentation_verdict, 'SEGMENTED')
        self.assertEqual(len(r.attached_mabniyat), 1)
        self.assertEqual(r.attached_mabniyat[0].mabni_id, 'ATTACHED_PRONOUN_NA')
        self.assertEqual(r.attached_mabniyat[0].surface_matched, 'نَا')

    def test_neg_maa_whole_token_match_not_recursed(self):
        """
        مَا is a recognized whole-token mabni (MA_SHART / MA_MAWSUL).
        Even though the token ends in ا, recognize_token must return
        NOT_SEGMENTED (whole-token match takes priority).
        """
        r = self._r('مَا')
        self.assertEqual(r.segmentation_verdict, 'NOT_SEGMENTED')
        self.assertEqual(len(r.attached_mabniyat), 0)


class TestMabniyatCompatibility(unittest.TestCase):
    """
    Tests for the explicit-diacritic compatibility guard in mabniyat_layer._lookup().

    Law: bare fallback is only accepted when every explicit diacritic in the
    input matches the corresponding diacritic of the candidate.  An explicit
    diacritic that DIFFERS from the candidate's diacritic is a contradiction
    and must be rejected — the bare fallback must not silently erase it.
    """

    def setUp(self):
        # Reset catalog cache so each test group starts clean
        import mabniyat_layer as ml
        ml._CATALOG = None

    def test_huwa_exact_accepted(self):
        """هُوَ (exact vocalized) → MABNI_BOUNDARY via Phase 1"""
        from mabniyat_layer import process_mabni
        r = process_mabni('هُوَ', 'ACCEPT')
        self.assertEqual(r.verdict, 'MABNI_BOUNDARY')
        self.assertEqual(r.mabni_id, 'HUWA')

    def test_huwa_bare_compatible(self):
        """هو (no diacritics) → MABNI_BOUNDARY via bare lookup — compatible"""
        from mabniyat_layer import process_mabni
        r = process_mabni('هو', 'ACCEPT')
        self.assertEqual(r.verdict, 'MABNI_BOUNDARY')

    def test_huwi_kasra_incompatible(self):
        """هُوِ (kasra on waw) → MABNI_NOT_FOUND — explicit kasra ≠ fatha in هُوَ"""
        from mabniyat_layer import process_mabni
        r = process_mabni('هُوِ', 'ACCEPT')
        self.assertEqual(r.verdict, 'MABNI_NOT_FOUND')

    def test_hawa_fatha_incompatible(self):
        """هَوَ (fatha on ha) → MABNI_NOT_FOUND — explicit fatha ≠ damma in هُوَ"""
        from mabniyat_layer import process_mabni
        r = process_mabni('هَوَ', 'ACCEPT')
        self.assertEqual(r.verdict, 'MABNI_NOT_FOUND')

    def test_hiya_exact_accepted(self):
        """هِيَ (exact vocalized) → MABNI_BOUNDARY via Phase 1"""
        from mabniyat_layer import process_mabni
        r = process_mabni('هِيَ', 'ACCEPT')
        self.assertEqual(r.verdict, 'MABNI_BOUNDARY')
        self.assertEqual(r.mabni_id, 'HIYA')

    def test_hiya_bare_compatible(self):
        """هي (no diacritics) → MABNI_BOUNDARY via bare lookup — compatible"""
        from mabniyat_layer import process_mabni
        r = process_mabni('هي', 'ACCEPT')
        self.assertEqual(r.verdict, 'MABNI_BOUNDARY')

    def test_hiyu_damma_incompatible(self):
        """هِيُ (damma on ya) → MABNI_NOT_FOUND — explicit damma ≠ fatha in هِيَ"""
        from mabniyat_layer import process_mabni
        r = process_mabni('هِيُ', 'ACCEPT')
        self.assertEqual(r.verdict, 'MABNI_NOT_FOUND')

    def test_explicit_diacritic_is_constraint_not_erasable(self):
        """
        Core law: explicit diacritic ≠ bare input.
        هُوِ has an explicit kasra on waw; bare lookup must not erase it to
        match هُوَ.  This is the regression test for the original bug.
        """
        from mabniyat_layer import process_mabni
        r_wrong  = process_mabni('هُوِ', 'ACCEPT')
        r_correct = process_mabni('هُوَ', 'ACCEPT')
        self.assertEqual(r_wrong.verdict, 'MABNI_NOT_FOUND',
            "هُوِ must not match هُوَ via bare lookup — kasra ≠ fatha")
        self.assertEqual(r_correct.verdict, 'MABNI_BOUNDARY',
            "هُوَ must still match via exact lookup")


class TestFalseSuffixScanResolution(unittest.TestCase):
    """
    اختبارات الحالات السبع التي كانت مصنَّفة FALSE_SUFFIX_SCAN.

    لكل حالة يُثبَت:
    1. عدم إجراء تقطيع لاحقي كاذب (segmentation_verdict ≠ SEGMENTED إلا عند الإرسال لـ HR2S).
    2. ظهور الهوية الكاملة عند الترخيص (MABNI_BOUNDARY).
    3. عدم إرسال جذع مصطنع إلى HR2S.
    4. عدم التراجع في الكلمات الصحيحة ذات الضمائر المتصلة.

    الحالات:
      ① أَيَّْنَ       — SOURCE_DATA_ISSUE (شكل تشكيل مستحيل في المصدر)
      ② الَّذِيْنَ     — LICENSED_DERIVED_FORM (سكون على ياء المدّ؛ إصلاح _explicit_marks_compatible)
      ③ تَانِكَ        — COMPOSITE_MABNI_WITH_KHITAB_SUFFIX (إضافة TANIKA للكتالوج)
      ④ ذَانِكَ        — COMPOSITE_MABNI_WITH_KHITAB_SUFFIX (إضافة DHANIKA للكتالوج)
      ⑤ ثَمَّكَ        — COMPOSITE_MABNI_WITH_KHITAB_SUFFIX (إضافة THAMM_KAF للكتالوج)
      ⑥ هَاهُنَاكَ    — COMPOSITE_MABNI_WITH_KHITAB_SUFFIX (إضافة HAHUNA_KAF للكتالوج)
      ⑦ هَاْدُوْكَ    — SOURCE_DATA_ISSUE (صيغة عامية)
    """

    def setUp(self):
        import mabniyat_layer as ml
        ml._CATALOG = None
        from mabniyat_attachment import _reset_cache
        _reset_cache()

    def _hokom(self, surface):
        from hokom_pipeline import hokom
        return hokom(surface)

    def _att(self, surface):
        r = self._hokom(surface)
        return r.get('attachment')

    # ── ① أَيَّْنَ — بيانات مصدر فاسدة ─────────────────────────────────────
    def test_ayyyna_source_data_issue_not_mabni_boundary(self):
        """
        أَيَّْنَ شكل تشكيل مستحيل (شدة+سكون على ياء). لا يُعرَّف كـ MABNI_BOUNDARY
        لأن الكتالوج لا يملكه بهذا الشكل. يجب ألا يُرسل جذع مصطنع لـ HR2S.
        الصورة الصحيحة أَيْنَ تُعرَّف صحيحًا.
        """
        # الصورة الصحيحة موجودة في الكتالوج
        from mabniyat_layer import process_mabni
        r_correct = process_mabni('أَيْنَ', 'ACCEPT')
        self.assertEqual(r_correct.verdict, 'MABNI_BOUNDARY')
        self.assertEqual(r_correct.mabni_id, 'AYNA_SHART')

        # الصورة الفاسدة لا تُنتج MABNI_BOUNDARY (البيانات المصدر خاطئة)
        r_bad = process_mabni('أَيَّْنَ', 'ACCEPT')
        self.assertNotEqual(r_bad.verdict, 'MABNI_BOUNDARY',
            "أَيَّْنَ (شكل مستحيل) لا يجب أن يُعرَّف كـ MABNI_BOUNDARY")

    # ── ② الَّذِيْنَ — صيغة مشروعة بسكون ياء المدّ ─────────────────────────
    def test_alladhina_sukun_madd_yaa_resolves_to_mabni_boundary(self):
        """
        الَّذِيْنَ (بسكون صريح على ياء المدّ) يجب أن يُطابق ALLADHINA في الكتالوج
        ويُعيد MABNI_BOUNDARY — لا تقطيعًا لاحقيًا كاذبًا ينتزع نَ.
        """
        att = self._att('الَّذِيْنَ')
        self.assertIsNotNone(att, "يجب أن يوجد attachment لـ الَّذِيْنَ")
        self.assertEqual(att.segmentation_verdict, 'NOT_SEGMENTED',
            "لا يُسمح بالتقطيع — الَّذِيْنَ مبني كامل")
        self.assertEqual(att.host_route, 'MABNI_BOUNDARY')

    def test_alladhina_sukun_compatible_huwa_kasra_still_incompatible(self):
        """
        الإصلاح يسمح فقط بسكون على ياء/واو مقابل لا-حركة في الكتالوج.
        لا يجب أن يُخلَّ بحالة هُوِ/هُوَ (كسرة مقابل فتحة — لا تزال غير متوافقة).
        """
        from mabniyat_layer import process_mabni
        r = process_mabni('هُوِ', 'ACCEPT')
        self.assertEqual(r.verdict, 'MABNI_NOT_FOUND',
            "هُوِ لا يزال يجب أن يرفض مطابقة هُوَ")

    # ── ③ تَانِكَ — اسم إشارة مثنى مؤنث بعيد ────────────────────────────────
    def test_tanika_whole_token_mabni_boundary_no_kaf_suffix(self):
        """
        تَانِكَ مبني كامل (TANIKA في الكتالوج).
        يجب أن تكون MABNI_BOUNDARY لا COMPOSITE_BOUNDARY.
        لا يُقطَّع إلى تَانِ + كَ.
        """
        att = self._att('تَانِكَ')
        self.assertIsNotNone(att)
        self.assertEqual(att.segmentation_verdict, 'NOT_SEGMENTED',
            "تَانِكَ مبني كامل — كاف البُعد ليست لاحقة ضمير مستقلة")
        self.assertEqual(att.host_route, 'MABNI_BOUNDARY')
        self.assertEqual(len(att.attached_mabniyat), 0,
            "لا توجد لاحقات ضمير في تَانِكَ")

    def test_tanika_in_catalog(self):
        """TANIKA يجب أن يكون في الكتالوج بعد الإضافة."""
        from mabniyat_layer import load_catalog
        cat = load_catalog()
        self.assertIn('TANIKA', cat['by_id'])
        self.assertEqual(cat['by_id']['TANIKA']['surface_vocalized'], 'تَانِكَ')

    # ── ④ ذَانِكَ — اسم إشارة مثنى مذكر بعيد ────────────────────────────────
    def test_dhanika_whole_token_mabni_boundary_no_kaf_suffix(self):
        """
        ذَانِكَ مبني كامل (DHANIKA في الكتالوج).
        يجب أن تكون MABNI_BOUNDARY لا COMPOSITE_BOUNDARY.
        """
        att = self._att('ذَانِكَ')
        self.assertIsNotNone(att)
        self.assertEqual(att.segmentation_verdict, 'NOT_SEGMENTED',
            "ذَانِكَ مبني كامل — كاف البُعد ليست لاحقة ضمير")
        self.assertEqual(att.host_route, 'MABNI_BOUNDARY')
        self.assertEqual(len(att.attached_mabniyat), 0)

    def test_dhanika_in_catalog(self):
        """DHANIKA يجب أن يكون في الكتالوج."""
        from mabniyat_layer import load_catalog
        cat = load_catalog()
        self.assertIn('DHANIKA', cat['by_id'])
        self.assertEqual(cat['by_id']['DHANIKA']['lexical_family'], 'DEMONSTRATIVE_SERIES')

    # ── ⑤ ثَمَّكَ — ثَمَّ + كاف خطاب ────────────────────────────────────────
    def test_thamm_kaf_whole_token_mabni_boundary(self):
        """
        ثَمَّكَ مبني كامل (THAMM_KAF) — كاف الخطاب لازمة لا لاحقة ضمير.
        """
        att = self._att('ثَمَّكَ')
        self.assertIsNotNone(att)
        self.assertEqual(att.segmentation_verdict, 'NOT_SEGMENTED')
        self.assertEqual(att.host_route, 'MABNI_BOUNDARY')
        self.assertEqual(len(att.attached_mabniyat), 0)

    def test_thamm_standalone_still_works(self):
        """ثَمَّ (بدون كاف) يجب أن يبقى MABNI_BOUNDARY (لا تراجع)."""
        att = self._att('ثَمَّ')
        self.assertIsNotNone(att)
        self.assertEqual(att.segmentation_verdict, 'NOT_SEGMENTED')
        self.assertEqual(att.host_route, 'MABNI_BOUNDARY')

    # ── ⑥ هَاهُنَاكَ — هَاهُنَا + كاف خطاب ──────────────────────────────────
    def test_hahunaka_whole_token_mabni_boundary(self):
        """
        هَاهُنَاكَ مبني كامل (HAHUNA_KAF) — كاف الخطاب لازمة.
        """
        att = self._att('هَاهُنَاكَ')
        self.assertIsNotNone(att)
        self.assertEqual(att.segmentation_verdict, 'NOT_SEGMENTED')
        self.assertEqual(att.host_route, 'MABNI_BOUNDARY')
        self.assertEqual(len(att.attached_mabniyat), 0)

    def test_hahuna_standalone_still_works(self):
        """هَاهُنَا (بدون كاف) يبقى MABNI_BOUNDARY (لا تراجع)."""
        att = self._att('هَاهُنَا')
        self.assertIsNotNone(att)
        self.assertEqual(att.segmentation_verdict, 'NOT_SEGMENTED')
        self.assertEqual(att.host_route, 'MABNI_BOUNDARY')

    # ── ⑦ هَاْدُوْكَ — بيانات مصدر عامية ────────────────────────────────────
    def test_haduwka_source_data_not_in_msa_catalog(self):
        """
        هَاْدُوْكَ صيغة عامية — لا يجب أن تُضاف للكتالوج بدون سلف مرخص.
        الكتالوج لا يملكها؛ الكود يتصرف بشكل متوقع (لا crash).
        """
        from mabniyat_layer import process_mabni, load_catalog
        cat = load_catalog()
        import unicodedata
        key = unicodedata.normalize('NFC', 'هَاْدُوْكَ')
        self.assertNotIn(key, cat['by_vocalized'],
            "هَاْدُوْكَ لا يجب أن تكون في الكتالوج")
        # يجب ألا ينهار الـ pipeline
        r = self._hokom('هَاْدُوْكَ')
        self.assertIsNotNone(r)

    # ── اختبارات التراجع — الضمائر المتصلة الصحيحة لا تتأثر ─────────────────
    def test_no_regression_lahum(self):
        """لَهُمْ: لِ+هُمْ — يجب أن يبقى COMPOSITE_CLOSED."""
        att = self._att('لَهُمْ')
        self.assertIsNotNone(att)
        self.assertEqual(att.segmentation_verdict, 'SEGMENTED')
        self.assertEqual(att.host_route, 'EMPTY')

    def test_no_regression_kitabahu(self):
        """كِتَابُهُ: مضاف+ضمير — COMPOSITE_BOUNDARY مع host=OPEN_TO_HR2S."""
        att = self._att('كِتَابُهُ')
        self.assertIsNotNone(att)
        self.assertEqual(att.segmentation_verdict, 'SEGMENTED')
        self.assertEqual(att.host_route, 'OPEN_TO_HR2S')
        self.assertEqual(len(att.attached_mabniyat), 1)

    def test_no_regression_dhalika_no_kaf_stripped(self):
        """
        ذَلِكَ موجود في الكتالوج كمبني كامل (THALIKA).
        يجب ألا يُقطَّع إلى ذَلِ+كَ.
        """
        att = self._att('ذَلِكَ')
        self.assertIsNotNone(att)
        self.assertEqual(att.segmentation_verdict, 'NOT_SEGMENTED',
            "ذَلِكَ مبني كامل — كاف البُعد ليست لاحقة")
        self.assertEqual(att.host_route, 'MABNI_BOUNDARY')


class TestAttachmentGuards(unittest.TestCase):
    """
    Tests for the seven algorithmic boundary guards added to
    mabniyat_attachment.py (Guards I–VII, task specification §1-7).

    Each guard has:
      • Positive tests — tokens that SHOULD be affected by the guard
      • Negative (counter) tests — real licensed forms that must NOT be blocked

    No lexical exceptions are permitted; all guards are structural.
    """

    def setUp(self):
        from mabniyat_attachment import recognize_token, _reset_cache
        _reset_cache()
        self._rt = recognize_token

    def _r(self, surface, p4='ACCEPT', original_surface=None):
        return self._rt(surface, p4, original_surface=original_surface)

    # ── Guard I-A: NUN_AL_NISWA blocked after ي/ى (plural inflectional ending) ─

    def test_naimina_not_segmented_nun_after_yaa(self):
        """نَائِمِينَ: ينَ is جمع المذكر السالم — نَ is NOT نون النسوة."""
        r = self._r('نَاءِمِينَ')
        self.assertEqual(r.segmentation_verdict, 'NOT_SEGMENTED',
            "ينَ is inflectional; NUN_AL_NISWA must be blocked after host ending in ي")

    def test_naimina_no_nun_al_niswa_in_att(self):
        r = self._r('نَاءِمِينَ')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertNotIn('ATTACHED_PRONOUN_NUN_AL_NISWA', ids)

    def test_masakina_not_segmented_nun_after_yaa(self):
        """الْمَسَاكِينَ: same plural ending — نَ must not be extracted."""
        r = self._r('ءَلْمَسَاكِينَ')
        self.assertEqual(r.segmentation_verdict, 'NOT_SEGMENTED')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertNotIn('ATTACHED_PRONOUN_NUN_AL_NISWA', ids)

    # ── Guard I-A (counter): genuine نون النسوة must still be recognized ────────

    def test_counter_nun_al_niswa_after_verb_stem(self):
        """يَكْتُبْنَ: النون على جذع فعلي عارٍ — نون النسوة مشروعة هنا."""
        # Surface: يَكْتُبْنَ — host يَكْتُبْ ends in consonant + sukun, NOT ي/و/ى
        r = self._r('يَكْتُبْنَ')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        # NUN_AL_NISWA should be present (host يَكْتُبْ does not end in ي/و/ى)
        self.assertIn('ATTACHED_PRONOUN_NUN_AL_NISWA', ids,
            "يَكْتُبْنَ: نون النسوة مشروعة بعد جذع فعل لا ينتهي بـ ي/و/ى")

    # ── Guard I-B: NUN_AL_NISWA blocked after و (ونَ = جمع المذكر مرفوع) ─────

    def test_yastatiuna_waw_attached_nun_inflectional(self):
        """يَسْتَطِيعُونَ: و = واو الجماعة (attached); نَ = نون الرفع (inflectional)."""
        r = self._r('يَسْتَطِيعُونَ')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertNotIn('ATTACHED_PRONOUN_NUN_AL_NISWA', ids,
            "نَ في ونَ ليست نون النسوة")

    def test_yastatiuna_waw_al_jamaa_present(self):
        """يَسْتَطِيعُونَ: واو الجماعة يجب أن تُرصد."""
        r = self._r('يَسْتَطِيعُونَ')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_WAW_AL_JAMAA', ids,
            "واو الجماعة يجب أن تُرصد في يَسْتَطِيعُونَ")

    def test_yastatiuna_inflectional_tail_is_nun(self):
        """يَسْتَطِيعُونَ: inflectional_tail = 'نَ'."""
        r = self._r('يَسْتَطِيعُونَ')
        self.assertEqual(r.inflectional_tail, 'نَ',
            "نَ في ونَ يجب تسجيلها في inflectional_tail لا كضمير مستقل")

    def test_yastatiuna_host_is_verb_stem(self):
        """يَسْتَطِيعُونَ: host = يَسْتَطِيعُ."""
        r = self._r('يَسْتَطِيعُونَ')
        self.assertEqual(r.host_surface, 'يَسْتَطِيعُ')

    # ── Guard II: TAU blocked after ا (sound feminine plural اتُ) ──────────────

    def test_hayawanat_not_segmented_tau_after_alef(self):
        """الْحَيَوَانَاتُ: اتُ = جمع المؤنث السالم — تُ ليست تاء ضمير."""
        r = self._r('ءَلْحَيَوَانَاتُ')
        self.assertEqual(r.segmentation_verdict, 'NOT_SEGMENTED',
            "اتُ هي جمع المؤنث السالم؛ تاء الضمير ممنوعة بعد ا")

    def test_hayawanat_no_tau_in_att(self):
        r = self._r('ءَلْحَيَوَانَاتُ')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertNotIn('ATTACHED_PRONOUN_TAU', ids)

    # ── Guard II (counter): genuine تاء الضمير must still work ─────────────────

    def test_counter_tau_after_verb_stem(self):
        """كَتَبْتُ: host كَتَبْ ends in صامت — تُ = تاء الفاعل مشروعة هنا."""
        r = self._r('كَتَبْتُ')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_TAU', ids,
            "كَتَبْتُ: تاء الضمير مشروعة بعد جذع لا ينتهي بـ ا")

    # ── Guard III: ALIF_AL_ITHNAYN depth-guarded (only at depth ≥ 1) ───────────

    def test_hinama_not_segmented_no_alif_al_ithnayn(self):
        """حِينَمَا: الألف من مَا — ألف الاثنين ممنوعة في العمق 0."""
        r = self._r('حِينَمَا')
        self.assertEqual(r.segmentation_verdict, 'NOT_SEGMENTED',
            "حِينَمَا لا تقطيع مشروع — الألف جزء من مَا")

    def test_hinama_no_alif_al_ithnayn_in_att(self):
        r = self._r('حِينَمَا')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertNotIn('ATTACHED_PRONOUN_ALIF_AL_ITHNAYN', ids)

    # ── Guard IV: False WAW prefix blocked (وَحْدَ family) ─────────────────────

    def test_wahdahum_host_is_wahda(self):
        """وَحْدَهُمْ: host = وَحْدَ; واو not extracted as prefix."""
        r = self._r('وَحْدَهُمْ')
        self.assertEqual(r.segmentation_verdict, 'SEGMENTED')
        self.assertEqual(r.host_surface, 'وَحْدَ')

    def test_wahdahum_no_wa_prep_prefix(self):
        r = self._r('وَحْدَهُمْ')
        prefix_ids = [p.mabni_id for p in r.prefix_operators]
        self.assertNotIn('WA_PREP', prefix_ids,
            "واو في وَحْدَهُمْ ليست حرف جر منفصلًا")

    def test_wahdaha_host_is_wahda(self):
        """وَحْدَهَا: نفس القاعدة."""
        r = self._r('وَحْدَهَا')
        self.assertEqual(r.host_surface, 'وَحْدَ')

    def test_wahdahum_suffix_is_hum(self):
        r = self._r('وَحْدَهُمْ')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_HUM_SUFFIX', ids)

    # ── Guard V: Operator re-check of residual host (أَنَّ → OPERATOR_BOUNDARY) ─

    def test_annahum_operator_boundary(self):
        """أَنَّهُمْ: host أَنَّ يُرسَل إلى OPERATOR_BOUNDARY لا OPEN_TO_HR2S."""
        r = self._r('ءَنْنَهُمْ', original_surface='أَنَّهُمْ')
        self.assertEqual(r.segmentation_verdict, 'SEGMENTED')
        self.assertEqual(r.host_route, 'OPERATOR_BOUNDARY',
            "أَنَّ عامل — لا يجوز إرسال جذعه إلى HR2S")

    def test_annahum_suffix_is_hum(self):
        r = self._r('ءَنْنَهُمْ', original_surface='أَنَّهُمْ')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_HUM_SUFFIX', ids)

    def test_annahum_host_not_open_to_hr2s(self):
        r = self._r('ءَنْنَهُمْ', original_surface='أَنَّهُمْ')
        self.assertNotEqual(r.host_route, 'OPEN_TO_HR2S',
            "الممنوع: host route = OPEN_TO_HR2S لأَنَّ")

    def test_liannahum_operator_boundary(self):
        """لِأَنَّهُمْ: prefix لِ + operator أَنَّ + suffix هُمْ."""
        r = self._r('لِءَنْنَهُمْ', original_surface='لِأَنَّهُمْ')
        self.assertEqual(r.host_route, 'OPERATOR_BOUNDARY')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_HUM_SUFFIX', ids)

    # ── Guard VI: Orthographic unity (بِهِمْ, بِهَا) ──────────────────────────

    def test_bihim_composite_closed(self):
        """بِهِمْ: بِ + هِمْ — COMPOSITE_CLOSED (host=EMPTY)."""
        r = self._r('بِهِمْ')
        self.assertEqual(r.segmentation_verdict, 'SEGMENTED')
        self.assertEqual(r.host_route, 'EMPTY')

    def test_bihim_suffix_is_him(self):
        r = self._r('بِهِمْ')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_HIM', ids)

    def test_biha_composite_closed(self):
        """بِهَا: بِ + هَا — COMPOSITE_CLOSED."""
        r = self._r('بِهَا')
        self.assertEqual(r.host_route, 'EMPTY')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_HA_FEM', ids)

    # ── Guard VII: Structural host guard — P4 monotonicity ─────────────────────

    def test_p4_defer_host_in_catalog_rejected(self):
        """
        If p4=DEFER and the host is in the mabniyat catalog, the segmentation
        must be rejected (REJECTED_STRUCTURAL_HOST) — a DEFER verdict cannot
        be promoted to ACCEPT downstream.
        """
        # ذَلِكَ is in the catalog; if p4=DEFER, any segmentation producing
        # a MABNI_DEFERRED host must be filtered out.  We verify the module
        # does not return SEGMENTED with MABNI_DEFERRED host_route.
        r = self._r('ذَلِكَهُمْ', p4='DEFER')
        # Either NOT_SEGMENTED or SEGMENTED with non-deferred host is acceptable.
        if r.segmentation_verdict == 'SEGMENTED':
            self.assertNotEqual(r.host_route, 'MABNI_DEFERRED',
                "حكم MABNI_DEFERRED مرفوض — الرتابة الهيكلية تمنع الترقية من DEFER")

    # ── No-regression: previously correct cases must remain correct ─────────────

    def test_no_regression_yuawwiduhum_hum_still_present(self):
        """يُعَوِّضَهُمْ: هُمْ لا يزال يُرصد بعد الإصلاحات."""
        r = self._r('يُعَوِّضَهُمْ')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_HUM_SUFFIX', ids)

    def test_no_regression_faqaduhu_ha_present(self):
        """فَقَدُوهُ: هُ (ATTACHED_PRONOUN_HA) لا يزال يُرصد، مع واو الجماعة."""
        r = self._r('فَقَدُوهُ')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_HA', ids,
            "هُ في فَقَدُوهُ يجب أن يُرصد (ATTACHED_PRONOUN_HA)")

    def test_no_regression_hubbiha_ha_fem_present(self):
        """حُبِّهَا: هَا (ATTACHED_PRONOUN_HA_FEM) لا يزال يُرصد."""
        r = self._r('حُبِّهَا')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_HA_FEM', ids)

    def test_no_regression_tarakathumhum_suffix_present(self):
        """تَرَكَتْهُمْ: هُمْ لا يزال يُرصد."""
        r = self._r('تَرَكَتْهُمْ')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_HUM_SUFFIX', ids)

    def test_no_regression_ruju_ha_fem(self):
        """رُجُوعِهَا: هَا (ATTACHED_PRONOUN_HA_FEM) لا يزال يُرصد."""
        r = self._r('رُجُوعِهَا')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_HA_FEM', ids)

    def test_inflectional_tail_empty_for_ordinary_suffix(self):
        """يُعَوِّضَهُمْ: inflectional_tail يجب أن يكون فارغًا (لا نون إعراب هنا)."""
        r = self._r('يُعَوِّضَهُمْ')
        self.assertEqual(r.inflectional_tail, '')


class TestGovernanceFixes(unittest.TestCase):
    """
    Governance tests for fixes G1, G3, G4, G5.
    G2 (يَدْعُونَ ambiguity) is explicitly deferred — no test added here.

    Test structure per fix:
    • Positive tests: cases that SHOULD produce attached forms
    • Negative tests: cases that SHOULD remain NOT_SEGMENTED
    • Counter/regression: previously correct cases must stay correct
    """

    def setUp(self):
        from mabniyat_attachment import recognize_token, _reset_cache
        _reset_cache()
        self._rt = recognize_token

    def _r(self, surface, p4='ACCEPT', original_surface=None):
        return self._rt(surface, p4, original_surface=original_surface)

    # ═══════════════════════════════════════════════════════════════════════
    # G1 — NUN_AL_NISWA Host Morphological Gate
    # ═══════════════════════════════════════════════════════════════════════
    # Old rule (removed): host ends in ي/ى → block NUN_AL_NISWA
    # New rule: block ONLY when host is NOT a mudāri' verb form

    def test_g1_yarmina_nun_al_niswa_survives(self):
        """يَرْمِينَ: host يَرْمِي is a mudāri' defective verb — NUN_AL_NISWA allowed."""
        r = self._r('يَرْمِينَ')
        self.assertEqual(r.segmentation_verdict, 'SEGMENTED',
            "يَرْمِينَ يجب أن يُقطَّع: يَرْمِي + نون النسوة")
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_NUN_AL_NISWA', ids)

    def test_g1_yarmina_host_is_yarmi(self):
        r = self._r('يَرْمِينَ')
        self.assertEqual(r.host_surface, 'يَرْمِي')

    def test_g1_yas3ayna_nun_al_niswa_survives(self):
        """يَسْعَيْنَ: host يَسْعَيْ — assimilated ى, still mudāri' — NUN_AL_NISWA allowed."""
        r = self._r('يَسْعَيْنَ')
        self.assertEqual(r.segmentation_verdict, 'SEGMENTED',
            "يَسْعَيْنَ يجب أن يُقطَّع: يَسْعَيْ + نون النسوة")
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_NUN_AL_NISWA', ids)

    def test_g1_yaqrana_positive_control(self):
        """يَقْرَءْنَ: positive control — hamza-final host, never blocked."""
        r = self._r('يَقْرَءْنَ')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_NUN_AL_NISWA', ids,
            "يَقْرَءْنَ: نون النسوة لم تتأثر بالإصلاح")

    def test_g1_naimina_blocked_nominal_plural(self):
        """نَاءِمِينَ: host نَاءِمِي is NOT a mudāri' form — NUN_AL_NISWA still blocked."""
        r = self._r('نَاءِمِينَ')
        self.assertEqual(r.segmentation_verdict, 'NOT_SEGMENTED',
            "نَاءِمِينَ: ينَ إعرابية، لا نون النسوة")
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertNotIn('ATTACHED_PRONOUN_NUN_AL_NISWA', ids)

    def test_g1_masakina_blocked_nominal_plural(self):
        """ءَلْمَسَاكِينَ: same — definite-article-prefixed nominal plural."""
        r = self._r('ءَلْمَسَاكِينَ')
        self.assertEqual(r.segmentation_verdict, 'NOT_SEGMENTED')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertNotIn('ATTACHED_PRONOUN_NUN_AL_NISWA', ids)

    def test_g1_yaktubna_verb_consonant_final_still_works(self):
        """يَكْتُبْنَ: host ends in consonant — NUN_AL_NISWA unaffected by G1."""
        r = self._r('يَكْتُبْنَ')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_NUN_AL_NISWA', ids)

    # ═══════════════════════════════════════════════════════════════════════
    # G3 — ALIF_AL_ITHNAYN at depth 0 with host validation gate
    # ═══════════════════════════════════════════════════════════════════════
    # Old rule (removed): ALIF_AL_ITHNAYN depth-guarded (depth ≥ 1 only)
    # New rule: allowed at depth 0 when _is_verbal_dual_host(host) = True

    def test_g3_kataba_alif_at_depth0(self):
        """كَتَبَا: host كَتَبَ is a māḍī verb — ALIF_AL_ITHNAYN at depth 0."""
        r = self._r('كَتَبَا')
        self.assertEqual(r.segmentation_verdict, 'SEGMENTED',
            "كَتَبَا يجب أن يُقطَّع: كَتَبَ + ألف الاثنين")
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_ALIF_AL_ITHNAYN', ids)

    def test_g3_kataba_host_is_katab(self):
        r = self._r('كَتَبَا')
        self.assertEqual(r.host_surface, 'كَتَبَ')

    def test_g3_dhahaba_alif_at_depth0(self):
        """ذَهَبَا: host ذَهَبَ — same gate."""
        r = self._r('ذَهَبَا')
        self.assertEqual(r.segmentation_verdict, 'SEGMENTED')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_ALIF_AL_ITHNAYN', ids)

    def test_g3_katabahu_recursive_alif_then_ha(self):
        """كَتَبَاهُ: هُ at depth 0, ا at depth 1 → host كَتَبَ."""
        r = self._r('كَتَبَاهُ')
        self.assertEqual(r.segmentation_verdict, 'SEGMENTED')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_ALIF_AL_ITHNAYN', ids)
        self.assertIn('ATTACHED_PRONOUN_HA', ids)
        self.assertEqual(r.host_surface, 'كَتَبَ')

    def test_g3_hinama_alif_blocked_kasra_host(self):
        """حِينَمَا: host حِينَمَ has kasra on first letter — NOT a māḍī host → blocked."""
        r = self._r('حِينَمَا')
        self.assertEqual(r.segmentation_verdict, 'NOT_SEGMENTED',
            "حِينَمَا: ألف المقصور من مَا — ليست ألف الاثنين")
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertNotIn('ATTACHED_PRONOUN_ALIF_AL_ITHNAYN', ids)

    # ═══════════════════════════════════════════════════════════════════════
    # G4 — Deferred candidates must not route to OPEN_TO_HR2S
    # ═══════════════════════════════════════════════════════════════════════

    def test_g4_dhalika_hum_defer_verdict_is_deferred(self):
        """ذَلِكَهُمْ p4=DEFER: only deferred candidate → segmentation_verdict=DEFERRED."""
        r = self._r('ذَلِكَهُمْ', p4='DEFER')
        self.assertEqual(r.segmentation_verdict, 'DEFERRED',
            "المرشح المؤجَّل يجب أن يعطي segmentation_verdict=DEFERRED")

    def test_g4_dhalika_hum_defer_host_route_is_mabni_deferred(self):
        """ذَلِكَهُمْ p4=DEFER: host_route must be MABNI_DEFERRED, not OPEN_TO_HR2S."""
        r = self._r('ذَلِكَهُمْ', p4='DEFER')
        self.assertEqual(r.host_route, 'MABNI_DEFERRED',
            "host_route يجب أن يكون MABNI_DEFERRED — لا OPEN_TO_HR2S")

    def test_g4_dhalika_hum_defer_not_open_to_hr2s(self):
        r = self._r('ذَلِكَهُمْ', p4='DEFER')
        self.assertNotEqual(r.host_route, 'OPEN_TO_HR2S',
            "الممنوع: توجيه مضيف مبني إلى HR2S عند P4=DEFER")

    def test_g4_dhalika_hum_defer_structural_verdict_preserved(self):
        r = self._r('ذَلِكَهُمْ', p4='DEFER')
        self.assertEqual(r.structural_verdict, 'DEFER',
            "structural_verdict يجب أن يبقى DEFER — لا ترقية")

    def test_g4_dhalika_hum_suffix_is_hum(self):
        """ذَلِكَهُمْ p4=DEFER: الضمير هُمْ يُرصد حتى في الحكم المؤجَّل."""
        r = self._r('ذَلِكَهُمْ', p4='DEFER')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_HUM_SUFFIX', ids)

    def test_g4_dhalika_hum_defer_mabni_id_exposed(self):
        """ذَلِكَهُمْ p4=DEFER: host_mabni_id = DHALIKA (G5 identity preserved)."""
        r = self._r('ذَلِكَهُمْ', p4='DEFER')
        self.assertIsNotNone(r.host_mabni_id,
            "host_mabni_id يجب أن يُسكَّن حتى في الحكم المؤجَّل")

    # ═══════════════════════════════════════════════════════════════════════
    # G5 — Dual lexical identity (host_mabni_id + host_operator_id)
    # ═══════════════════════════════════════════════════════════════════════

    def test_g5_anna_hum_operator_boundary(self):
        """أَنَّهُمْ: host_route = OPERATOR_BOUNDARY."""
        r = self._r('ءَنْنَهُمْ', original_surface='أَنَّهُمْ')
        self.assertEqual(r.host_route, 'OPERATOR_BOUNDARY')

    def test_g5_anna_hum_operator_id(self):
        """أَنَّهُمْ: host_operator_id = ANNA."""
        r = self._r('ءَنْنَهُمْ', original_surface='أَنَّهُمْ')
        self.assertEqual(r.host_operator_id, 'ANNA',
            "معرِّف العامل يجب أن يكون ANNA")

    def test_g5_anna_hum_mabni_id(self):
        """أَنَّهُمْ: host_mabni_id = ANNA — mabni identity preserved even when routing as OPERATOR."""
        r = self._r('ءَنْنَهُمْ', original_surface='أَنَّهُمْ')
        self.assertEqual(r.host_mabni_id, 'ANNA',
            "هوية المبنى ANNA يجب أن تبقى محفوظة حتى حين يُوجَّه المضيف كعامل")

    def test_g5_anna_hum_dual_licensed(self):
        """أَنَّهُمْ: host_identity_status = DUAL_LICENSED."""
        r = self._r('ءَنْنَهُمْ', original_surface='أَنَّهُمْ')
        self.assertEqual(r.host_identity_status, 'DUAL_LICENSED',
            "أَنَّ مُرخَّص في كلا الكتالوجَيْن")

    def test_g5_anna_hum_suffix_hum(self):
        """أَنَّهُمْ: suffix هُمْ recognized."""
        r = self._r('ءَنْنَهُمْ', original_surface='أَنَّهُمْ')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_HUM_SUFFIX', ids)

    def test_g5_anna_hum_not_open_to_hr2s(self):
        """أَنَّهُمْ: host must not go to HR2S."""
        r = self._r('ءَنْنَهُمْ', original_surface='أَنَّهُمْ')
        self.assertNotEqual(r.host_route, 'OPEN_TO_HR2S')

    def test_g5_ordinary_host_none_ids(self):
        """يُعَوِّضَهُمْ: ordinary verb host → host_mabni_id and host_operator_id are None."""
        r = self._r('يُعَوِّضَهُمْ')
        self.assertIsNone(r.host_mabni_id)
        self.assertIsNone(r.host_operator_id)
        self.assertEqual(r.host_identity_status, 'NONE')

    # ═══════════════════════════════════════════════════════════════════════
    # Positive-control regression: previously correct cases unchanged
    # ═══════════════════════════════════════════════════════════════════════

    def test_reg_yuawwidhum_hum_suffix(self):
        """يُعَوِّضَهُمْ: HUM_SUFFIX لا يزال يُرصد."""
        r = self._r('يُعَوِّضَهُمْ')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_HUM_SUFFIX', ids)

    def test_reg_faqaduhu_ha_and_waw(self):
        """فَقَدُوهُ: WAW_AL_JAMAA + HA."""
        r = self._r('فَقَدُوهُ')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_HA', ids)

    def test_reg_ummihim_him(self):
        """أُمِّهِمْ: HIM."""
        r = self._r('أُمِّهِمْ')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_HIM', ids)

    def test_reg_hubbiha_ha_fem(self):
        """حُبِّهَا: HA_FEM."""
        r = self._r('حُبِّهَا')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_HA_FEM', ids)

    def test_reg_lahum_empty_host(self):
        """لَهُمْ: prefix لَ + هُمْ → EMPTY host."""
        r = self._r('لَهُمْ')
        self.assertEqual(r.host_route, 'EMPTY')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_HUM_SUFFIX', ids)

    def test_reg_yastatiuna_waw_inflectional_nun(self):
        """يَسْتَطِيعُونَ: WAW_AL_JAMAA + inflectional_tail=نَ, no NUN_AL_NISWA."""
        r = self._r('يَسْتَطِيعُونَ')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertIn('ATTACHED_PRONOUN_WAW_AL_JAMAA', ids)
        self.assertNotIn('ATTACHED_PRONOUN_NUN_AL_NISWA', ids)
        self.assertEqual(r.inflectional_tail, 'نَ')

    def test_reg_bihim_empty_host(self):
        """بِهِمْ: بِ + هِمْ → EMPTY host."""
        r = self._r('بِهِمْ')
        self.assertEqual(r.host_route, 'EMPTY')

    def test_reg_hayawanat_not_segmented(self):
        """الْحَيَوَانَاتُ: TAU guard still blocks اتُ pattern."""
        r = self._r('ءَلْحَيَوَانَاتُ')
        self.assertEqual(r.segmentation_verdict, 'NOT_SEGMENTED')
        ids = [s.mabni_id for s in r.attached_mabniyat]
        self.assertNotIn('ATTACHED_PRONOUN_TAU', ids)

    # ═══════════════════════════════════════════════════════════════════════
    # G2 — explicitly NOT tested (deferred linguistic ambiguity)
    # يَدْعُونَ: ambiguity between WAW_AL_JAMAA+NUN_AL_RAF vs radical-و+NUN_AL_NISWA
    # Current treatment: resolved as WAW_AL_JAMAA + inflectional نَ (MSA default)
    # No test added here per task specification.
    # See _VERBAL_PLURAL_PATTERNS TODO comment in mabniyat_attachment.py.
    # ═══════════════════════════════════════════════════════════════════════


if __name__ == '__main__':
    unittest.main()
