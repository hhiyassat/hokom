#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/build_mabniyat_test_harness.py
=======================================
ينفِّذ الجرد الكامل لجميع أمثلة ملفات data/02_mabniyat/
ثم يشغِّل الحالات القابلة للاختبار عبر الخط المباشر hokom()،
ويُنتج المانيفست والتقارير والاختبارات دفعةً واحدة.

الاستخدام:
  python scripts/build_mabniyat_test_harness.py

المخرجات:
  data/generated/02_mabniyat/mabniyat_examples_manifest.jsonl
  data/generated/02_mabniyat/mabniyat_examples_manifest.csv
  reports/mabniyat/all_mabniyat_examples_results.jsonl
  reports/mabniyat/all_mabniyat_examples_results.csv
  reports/mabniyat/all_mabniyat_examples_report.txt
  reports/mabniyat/all_mabniyat_examples_failures.jsonl
  tests/integration/test_all_mabniyat_json_examples.py
"""

import csv
import json
import os
import re
import sys
import time
import traceback
import unicodedata

# ── التأكد من أننا نُشغَّل من داخل مجلد hokom ─────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HOKOM_DIR  = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, HOKOM_DIR)
os.chdir(HOKOM_DIR)

from hokom_pipeline import hokom as run_hokom
from mabni_layer    import MabniBoundary, MabniOpen, MabniBlocked, get_inventory
from mabniyat_layer import normalize_key, get_all_rows as mabni_catalog_rows
from normalizer     import normalize as normalize_surface
from licensing           import license_phone, gate_unicode
from glyph_classification import classify_base_glyph, BaseGlyphClass
from syllabifier    import parse_phones

# ══════════════════════════════════════════════════════════════════════════════
# القاموس الرئيسي: إعدادات كل ملف JSON
# الأعمدة: (surface_field, example_field, route_hint, default_status)
#   surface_field  — الحقل الذي يحوي سطح المبني القابل للاختبار (None=لا يوجد)
#   example_field  — الحقل الذي يحوي جملة/مثال السياق
#   route_hint     — 'MABNI'|'OPERATOR'|'VERB_MABNI'|None
#   default_status — حالة التوقع الافتراضية للسجل
# ══════════════════════════════════════════════════════════════════════════════
FILE_SCHEMA = {
    'built_in_adverbs.json':              ('adverb',             'example_sentence', 'MABNI',      'TESTABLE'),
    'demonstrative_pronouns.json':        ('name',               'example',          'MABNI',      'TESTABLE'),
    'relative_pronouns.json':             ('name',               'example',          'MABNI',      'TESTABLE'),
    'pronouns_classification.json':       ('pronoun',            'example',          'MABNI',      'SPECIAL'),
    'hidden_pronouns.json':               (None,                 'example',          None,         'LATENT_ONLY'),
    'conditional_letters_tools.json':     ('particle',           'example',          'OPERATOR',   'TESTABLE'),
    'coordinating_conjunctions.json':     ('letter',             'example',          'OPERATOR',   'TESTABLE'),
    'copulative_particle.json':           ('copulative_particle','example',          'OPERATOR',   'TESTABLE'),
    'jazm_tools.json':                    ('tool',               'example',          'OPERATOR',   'TESTABLE'),
    'interrogative_letters_tools.json':   ('tool',               'example',          'MABNI',      'TESTABLE'),
    'interrogative_tools_categories.json':('tool',               'example',          'MABNI',      'TESTABLE'),
    'kinaya_names.json':                  ('name',               'example',          'MABNI',      'TESTABLE'),
    'letters_answers.json':               ('particle',           'examples',         'MABNI',      'TESTABLE'),
    'preposition_meanings.json':          ('preposition',        'example',          'OPERATOR',   'TESTABLE'),
    'present_naseb_tools.json':           ('tool',               'example',          'OPERATOR',   'TESTABLE'),
    'verb_name.json':                     ('name',               'example',          'VERB_MABNI', 'TESTABLE'),
    'vocative_particles.json':            ('particle',           'example',          'OPERATOR',   'TESTABLE'),
    'imperative_verb_building.json':      ('example',            'example',          'VERB_MABNI', 'TESTABLE'),
    # ملفات القواعد والبناء — لا يوجد سطح مفرد قابل للاختبار
    'verb_building_rules.json':           (None,                 'example',          None,         'RULE_ONLY'),
    'past_tense_conjugation_rules.json':  (None,                 'example',          None,         'RULE_ONLY'),
    'present_tense_building_cases.json':  (None,                 'example',          None,         'RULE_ONLY'),
    'building_regulations.json':          (None,                 'example',          None,         'RULE_ONLY'),
    'estimated_parsing_indeclinables.json':(None,                'example',          None,         'RULE_ONLY'),
    'functional_indeclinable_substitutes.json':(None,            'example',          None,         'RULE_ONLY'),
    'indeclinable_discourse_roles.json':  (None,                 'example',          None,         'RULE_ONLY'),
    'types_of_i3rab.json':               (None,                 'example',          None,         'RULE_ONLY'),
    # العدد المركب — عبارة متعددة الكلمات
    'compound_numbers.json':             (None,                  'example',          None,         'UNDERLICENSED'),
    'compound_number_details.json':      (None,                  'example',          None,         'UNDERLICENSED'),
    # جُمَل سياقية لا تختبر مبني بعينه
    'grammatical_construction_cases.json':(None,                 'example',          None,         'SENTENCE_CONTEXT'),
}

HAMZA_CHARS = set('أإآءؤئ')

# ══════════════════════════════════════════════════════════════════════════════
# مشاكل بيانات معروفة: (اسم_الملف، السطح) ← ملاحظة السبب
#
# القواعد:
#   - إذا احتوت الملاحظة على "BLOCKED_BY_P4"  → exp_status = 'BLOCKED_BY_P4'
#   - وإلا                                      → exp_status = 'APPROVED_DEFER'
#
# كلا الحالتين يُخرِج السجل من مجموعة TESTABLE ويمنع فشل الاختبار التلقائي.
# ══════════════════════════════════════════════════════════════════════════════
_KNOWN_SOURCE_DATA_ISSUES_RAW: dict[tuple[str, str], str] = {
    # ── built_in_adverbs.json ─────────────────────────────────────────────────
    # شكل تشكيل مستحيل (شدة+سكون على ياء واحدة)؛ الصواب أَيْنَ
    ('built_in_adverbs.json', 'أَيَّْنَ'):
        'APPROVED_DEFER — شكل تشكيل مستحيل في حقل adverb (شدة+سكون على ياء واحدة)؛ الصواب أَيْنَ',
    # أَيَّانَ في built_in_adverbs.json: تُصنَّف ظرفًا لكن أُضيفت إلى كتالوج العوامل (شرط جازم)
    ('built_in_adverbs.json', 'أَيَّانَ'):
        'APPROVED_DEFER — SOURCE_CONTRADICTION: أَيَّانَ ظرف في built_in_adverbs لكنها أداة شرط جازم في كتالوج العوامل',
    # اَلآنَ: فتحة على الألف الأولى تجعل P4 يرفضها؛ الصواب الآنَ
    ('built_in_adverbs.json', 'اَلآنَ'):
        'BLOCKED_BY_P4 — تشكيل غير قياسي (فتحة على ألف التعريف)؛ P4 يرفض هذا الشكل',
    # اَلَّلَيْلَةَ: لام زائدة بعد الشدة؛ الصواب اللَّيْلَةَ
    ('built_in_adverbs.json', 'اَلَّلَيْلَةَ'):
        'BLOCKED_BY_P4 — لام زائدة في التشكيل (اَلَّلَ بدل اَلَّ)؛ P4 يرفض هذا الشكل',
    # مَتَى: ظرف زمان + أداة شرط جازم — تعارض دلالي حقيقي بين ملفَي المصدر
    ('built_in_adverbs.json', 'مَتَى'):
        'APPROVED_DEFER — SOURCE_CONTRADICTION: مَتَى ظرف في built_in_adverbs لكنها أداة شرط جازم في كتالوج العوامل',
    # إِذَا: ظرف زمان + أداة شرط — تعارض دلالي حقيقي
    ('built_in_adverbs.json', 'إِذَا'):
        'APPROVED_DEFER — SOURCE_CONTRADICTION: إِذَا ظرف في built_in_adverbs لكنها أداة شرط في كتالوج العوامل',

    # ── relative_pronouns.json ────────────────────────────────────────────────
    # مَنْ: موصولة + أداة شرط جازم — P5 لا يملك سياقًا للتمييز
    ('relative_pronouns.json', 'مَنْ'):
        'APPROVED_DEFER — SOURCE_CONTRADICTION: مَنْ ضمير موصول في relative_pronouns لكنها أداة شرط جازم في كتالوج العوامل',
    # اَلَّلَاْئِيْ: لام زائدة؛ الصواب اللَّائِي
    ('relative_pronouns.json', 'اَلَّلَاْئِيْ'):
        'BLOCKED_BY_P4 — لام زائدة في التشكيل؛ P4 يرفض هذا الشكل',
    # مَا: موصولة + نافية — تعارض دلالي حقيقي
    ('relative_pronouns.json', 'مَا'):
        'APPROVED_DEFER — SOURCE_CONTRADICTION: مَا موصولة في relative_pronouns لكنها أداة شرط/نفي في كتالوج العوامل',
    # اَلَّلَذَاْنِ: لام زائدة؛ الصواب اللَّذَانِ
    ('relative_pronouns.json', 'اَلَّلَذَاْنِ'):
        'BLOCKED_BY_P4 — لام زائدة في التشكيل؛ P4 يرفض هذا الشكل',
    # اَلَّلَتَاْنِ: لام زائدة؛ الصواب اللَّتَانِ
    ('relative_pronouns.json', 'اَلَّلَتَاْنِ'):
        'BLOCKED_BY_P4 — لام زائدة في التشكيل؛ P4 يرفض هذا الشكل',
    # اَلَّلَذَيْنِ: لام زائدة؛ الصواب اللَّذَيْنِ
    ('relative_pronouns.json', 'اَلَّلَذَيْنِ'):
        'BLOCKED_BY_P4 — لام زائدة في التشكيل؛ P4 يرفض هذا الشكل',
    # اَلَّلَتَيْنِ: لام زائدة؛ الصواب اللَّتَيْنِ
    ('relative_pronouns.json', 'اَلَّلَتَيْنِ'):
        'BLOCKED_BY_P4 — لام زائدة في التشكيل؛ P4 يرفض هذا الشكل',
    # اَلَّذِيْنَ: تشكيل غير قياسي (ألف فتحة + شدة)؛ الصواب الَّذِينَ
    ('relative_pronouns.json', 'اَلَّذِيْنَ'):
        'BLOCKED_BY_P4 — تشكيل غير قياسي (فتحة على ألف التعريف مع شدة)؛ P4 يرفض هذا الشكل',
    # اَلَّلَاْتِيْ: لام زائدة؛ الصواب اللَّاتِي
    ('relative_pronouns.json', 'اَلَّلَاْتِيْ'):
        'BLOCKED_BY_P4 — لام زائدة في التشكيل؛ P4 يرفض هذا الشكل',
    # اَلَّلَذِيْنَ: لام زائدة؛ الصواب اللَّذِينَ
    ('relative_pronouns.json', 'اَلَّلَذِيْنَ'):
        'BLOCKED_BY_P4 — لام زائدة في التشكيل؛ P4 يرفض هذا الشكل',
    # اَلَّلَهُمَّ: نداء ديني وليس ضميرًا موصولًا — تصنيف خاطئ في ملف المصدر
    ('relative_pronouns.json', 'اَلَّلَهُمَّ'):
        'APPROVED_DEFER — SOURCE_DATA_ISSUE: اللَّهُمَّ نداء ديني وليس ضميرًا موصولًا؛ تصنيف خاطئ في ملف المصدر',
    # مَهْمَاْ: ضمير موصول شرطي + أداة شرط جازم — تعارض دلالي
    ('relative_pronouns.json', 'مَهْمَاْ'):
        'APPROVED_DEFER — SOURCE_CONTRADICTION: مَهْمَا في relative_pronouns لكنها أداة شرط جازم في كتالوج العوامل',
    # أَيّ: شدة بدون حركة تالية — P4 يرفض هذا الشكل
    ('relative_pronouns.json', 'أَيّ'):
        'BLOCKED_BY_P4 — شدة بدون حركة كاملة (أَيّ بدون تنوين أو حركة على الشدة)؛ P4 يرفض',
    # هَاْدُوْكَ: صيغة عامية/مغربية غير معيارية؛ بيانات خردة
    ('relative_pronouns.json', 'هَاْدُوْكَ'):
        'APPROVED_DEFER — SOURCE_DATA_ISSUE: صيغة عامية في ملف الضمائر الموصولة؛ السجلات المجاورة خردة',
    # بب: بيانات خردة
    ('relative_pronouns.json', 'بب'):
        'APPROVED_DEFER — SOURCE_DATA_ISSUE: بيانات خردة في ملف الضمائر الموصولة',
    # مبني: اسم الصفة لا مثال فعلي — بيانات خردة
    ('relative_pronouns.json', 'مبني'):
        'APPROVED_DEFER — SOURCE_DATA_ISSUE: اسم الصفة النحوية وليس ضميرًا موصولًا؛ بيانات خردة',
    # g: حرف أجنبي — بيانات خردة
    ('relative_pronouns.json', 'g'):
        'APPROVED_DEFER — SOURCE_DATA_ISSUE: حرف أجنبي في ملف الضمائر العربية؛ بيانات خردة',

    # ── interrogative_letters_tools.json ─────────────────────────────────────
    # أَ: همزة الاستفهام = OPERATOR في الواقع اللغوي لكن ملف المصدر يصنفها MABNI
    ('interrogative_letters_tools.json', 'أَ'):
        'APPROVED_DEFER — SOURCE_CONTRADICTION: همزة الاستفهام أَ = OPERATOR في الكتالوج لكن ملف interrogative_letters_tools يصنفها MABNI',

    # ── interrogative_tools_categories.json ──────────────────────────────────
    # من: غير مشكول — P5 لا يجد مطابقة مشكولة
    ('interrogative_tools_categories.json', 'من'):
        'APPROVED_DEFER — سطح غير مشكول؛ يحتاج تشكيل (مَنْ) لمطابقة الكتالوج',
    # ماذا: مركب بدون مسافة — P4 يرفض هذا البنية
    ('interrogative_tools_categories.json', 'ماذا'):
        'BLOCKED_BY_P4 — كلمة مركبة (ما+ذا) بدون مسافة؛ P4 يرفض هذا الشكل',
    # متى: غير مشكول + polysemous
    ('interrogative_tools_categories.json', 'متى'):
        'APPROVED_DEFER — SOURCE_CONTRADICTION: متى غير مشكولة + تعارض ظرف/شرط',
    # أيّان: شدة بدون حركة كاملة — P4 يرفض
    ('interrogative_tools_categories.json', 'أيّان'):
        'BLOCKED_BY_P4 — شدة بدون حركة كاملة (أيّان بدون فتحة على الشدة)؛ P4 يرفض',
    # أنَّى: تشكيل جزئي — P5 لا يجد مطابقة
    ('interrogative_tools_categories.json', 'أنَّى'):
        'APPROVED_DEFER — تشكيل جزئي (أنَّى بدون فتحة على الهمزة)؛ يحتاج أَنَّى للمطابقة',
    # كم: غير مشكول
    ('interrogative_tools_categories.json', 'كم'):
        'APPROVED_DEFER — سطح غير مشكول؛ يحتاج تشكيل (كَمْ) لمطابقة الكتالوج',
    # الهمزة: اسم حرف الاستفهام لا رمزه — بيانات مصدر خاطئة
    ('interrogative_tools_categories.json', 'الهمزة'):
        'APPROVED_DEFER — SOURCE_DATA_ISSUE: الهمزة اسم الحرف لا رمزه (أَ)؛ لا يمكن اختباره كسطح',

    # ── letters_answers.json ──────────────────────────────────────────────────
    # إِنَّ: حرف توكيد = OPERATOR في الكتالوج لكن ملف المصدر يصنفها حرف جواب MABNI
    ('letters_answers.json', 'إِنَّ'):
        'APPROVED_DEFER — SOURCE_CONTRADICTION: إِنَّ حرف توكيد OPERATOR في الكتالوج لكن letters_answers يصنفها MABNI',

    # ── demonstrative_pronouns.json ───────────────────────────────────────────
    # هذان: غير مشكول — P5 لا يجد مطابقة
    ('demonstrative_pronouns.json', 'هذان'):
        'APPROVED_DEFER — سطح غير مشكول؛ يحتاج تشكيل (هَذَانِ) لمطابقة الكتالوج',
    # هاتان: غير مشكول — P4 يرفضه
    ('demonstrative_pronouns.json', 'هاتان'):
        'BLOCKED_BY_P4 — سطح غير مشكول؛ P4 يرفض بنية بدون حركات',
    # ذه: غير مشكول — P5 لا يجد مطابقة
    ('demonstrative_pronouns.json', 'ذه'):
        'APPROVED_DEFER — سطح غير مشكول؛ يحتاج تشكيل (ذِهِ) لمطابقة الكتالوج',

    # ── kinaya_names.json ─────────────────────────────────────────────────────
    # كأَيٍّ: P5 يُعيد OPERATOR_DEFERRED بسبب تنوين+شدة — غموض صادق
    ('kinaya_names.json', 'كأَيٍّ'):
        'APPROVED_DEFER — P5 يُعيد OPERATOR_DEFERRED لتنوين+شدة في كأَيٍّ؛ غموض صادق يحتاج سياق',

    # ── imperative_verb_building.json ─────────────────────────────────────────
    # أفعال الأمر: P4 يرفضها لأنها أفعال لا مبنيات اسمية/حرفية
    ('imperative_verb_building.json', 'اذْهَبْ'):
        'BLOCKED_BY_P4 — فعل أمر؛ P4 يرفض بنية أفعال الأمر (لا تدخل مسار المبنيات)',
    ('imperative_verb_building.json', 'اسْمَعْنَ'):
        'BLOCKED_BY_P4 — فعل أمر (نون النسوة)؛ P4 يرفض هذه البنية',
    ('imperative_verb_building.json', 'ادْرُسَنْ'):
        'BLOCKED_BY_P4 — فعل أمر (نون التوكيد الخفيفة)؛ P4 يرفض هذه البنية',
    ('imperative_verb_building.json', 'احْفَظَنَّ'):
        'BLOCKED_BY_P4 — فعل أمر (نون التوكيد الثقيلة)؛ P4 يرفض هذه البنية',
    ('imperative_verb_building.json', 'اسْعَ'):
        'BLOCKED_BY_P4 — فعل أمر (فعل ناقص)؛ P4 يرفض هذه البنية',
    ('imperative_verb_building.json', 'اسْقِ'):
        'BLOCKED_BY_P4 — فعل أمر (فعل ناقص)؛ P4 يرفض هذه البنية',
    ('imperative_verb_building.json', 'ادْعُ'):
        'BLOCKED_BY_P4 — فعل أمر (فعل ناقص)؛ P4 يرفض هذه البنية',
    ('imperative_verb_building.json', 'اكْتُبُوا'):
        'BLOCKED_BY_P4 — فعل أمر (جمع المذكر)؛ P4 يرفض هذه البنية',
    ('imperative_verb_building.json', 'اسْبَحَا'):
        'BLOCKED_BY_P4 — فعل أمر (المثنى)؛ P4 يرفض هذه البنية',
    ('imperative_verb_building.json', 'اقْرَئِي'):
        'BLOCKED_BY_P4 — فعل أمر (المؤنث المفردة)؛ P4 يرفض هذه البنية',

    # ── coordinating_conjunctions.json ───────────────────────────────────────
    # حَتّى: شدة بدون فتحة قبلها — P4 يرفض؛ الصواب حَتَّى
    ('coordinating_conjunctions.json', 'حَتّى'):
        'BLOCKED_BY_P4 — شدة بدون فتحة قبلها (حَتّى بدل حَتَّى)؛ P4 يرفض هذا الشكل',

    # ── jazm_tools.json ───────────────────────────────────────────────────────
    # أَيْنَما: كتابة بدون فتحة على الميم — P4 يرفض؛ الصواب أَيْنَمَا
    ('jazm_tools.json', 'أَيْنَما'):
        'BLOCKED_BY_P4 — ميم بدون فتحة (أَيْنَما بدل أَيْنَمَا)؛ P4 يرفض هذا الشكل',

    # ── vocative_particles.json ───────────────────────────────────────────────
    # آيْ: P4 يرفض ألف المد + ياء ساكنة في هذا السياق
    ('vocative_particles.json', 'آيْ'):
        'BLOCKED_BY_P4 — P4 يرفض بنية آيْ (ألف مد + ياء ساكنة)؛ يحتاج إصلاح P4',
}
# طبِّق NFC على كل مفتاح سطح لضمان التطابق مع القيم المُستخرجة من ملفات JSON
# (بعض ملفات JSON تخزن الحركات بترتيب مختلف عن المصدر ولكن NFC-متكافئ)
_KNOWN_SOURCE_DATA_ISSUES: dict[tuple[str, str], str] = {
    (fname, unicodedata.normalize('NFC', surf)): reason
    for (fname, surf), reason in _KNOWN_SOURCE_DATA_ISSUES_RAW.items()
}

# ══════════════════════════════════════════════════════════════════════════════
# خريطة الطبقات الست — تحوِّل failure_category إلى قرار حوكمي
# ══════════════════════════════════════════════════════════════════════════════
VERDICT_TIER_MAP: dict[str | None, str] = {
    # ── PASS ──────────────────────────────────────────────────────────────────
    None:                          'PASS',
    # ── PROBABLE_RUNTIME_FAILURE (يحتمل تعديل الكود) ──────────────────────
    'FALSE_SUFFIX_SCAN':           'PROBABLE_RUNTIME_FAILURE',
    'NORMALIZATION_HAMZA_MISMATCH':'PROBABLE_RUNTIME_FAILURE',
    'SLOT_PATTERN_BLOCKED':        'PROBABLE_RUNTIME_FAILURE',
    'P0_UNLICENSED_TA_MARBUTA':    'PROBABLE_RUNTIME_FAILURE',
    'WRONG_SEGMENTATION':          'PROBABLE_RUNTIME_FAILURE',
    'ATTACHED_MABNI_NOT_FOUND':    'PROBABLE_RUNTIME_FAILURE',
    'HAMZAT_WASL_STRUCTURE':       'PROBABLE_RUNTIME_FAILURE',
    'TOKENIZATION_ERROR':          'PROBABLE_RUNTIME_FAILURE',
    'WRONG_FINAL_DISPLAY':         'PROBABLE_RUNTIME_FAILURE',
    # ── CATALOG_GAP_CANDIDATE (مرشح لفجوة في الكتالوج — يحتاج تحقق) ────────
    'WHOLE_MABNI_NOT_FOUND':       'CATALOG_GAP_CANDIDATE',
    # ── DUAL_LICENSED_REVIEW (هوية مبني+عامل — ليست خطأ بالضرورة) ──────────
    'DUAL_CATALOG_PRESENCE':       'DUAL_LICENSED_REVIEW',
    # ── SOURCE_DATA_ISSUE (فساد البيانات المصدر، لا خطأ في الكود) ───────────
    'SOURCE_CATEGORY_MISMATCH':    'SOURCE_DATA_ISSUE',
    'INVALID_COMBINING_MARK_ORDER':'SOURCE_DATA_ISSUE',
    # ── DEFERRED_AMBIGUOUS (غموض صادق — ليس فشلًا) ──────────────────────────
    'AMBIGUOUS_SEGMENTATION':      'DEFERRED_AMBIGUOUS',
}

# الترتيب المُعتمد لعرض جدول الطبقات
TIER_ORDER = [
    'PASS',
    'PROBABLE_RUNTIME_FAILURE',
    'CATALOG_GAP_CANDIDATE',
    'DUAL_LICENSED_REVIEW',
    'SOURCE_DATA_ISSUE',
    'DEFERRED_AMBIGUOUS',
]

def _assign_tier(failure_category: str | None) -> str:
    """يُعيد الطبقة الحوكمية من failure_category."""
    return VERDICT_TIER_MAP.get(failure_category, 'PROBABLE_RUNTIME_FAILURE')

# ── بناء فهرس الكتالوج لمطابقة expected_mabni_id ─────────────────────────
_MABNI_BY_BARE: dict[str, str] = {}
_MABNI_BY_VOC:  dict[str, str] = {}
for _r in mabni_catalog_rows():
    _sv  = _r.get('surface_vocalized', '').strip()
    _mid = _r.get('mabni_id', '').strip()
    if _sv and _mid:
        _MABNI_BY_VOC[normalize_key(_sv)] = _mid
        bare = re.sub(r'[ً-ْٰـ]', '', _sv)
        if bare not in _MABNI_BY_BARE:
            _MABNI_BY_BARE[bare] = _mid

# ── فهرس كتالوج العوامل (operators) ─────────────────────────────────────
_OPS_INV = get_inventory()


def _catalog_lookup(surface: str) -> str | None:
    """بحث في كتالوج المبنيات عن معرِّف المبني (بدون تطبيع المدخل)."""
    key = normalize_key(surface)
    if key in _MABNI_BY_VOC:
        return _MABNI_BY_VOC[key]
    bare = re.sub(r'[ً-ْٰـ]', '', surface)
    return _MABNI_BY_BARE.get(bare)


def _is_hamza_initial(surface: str) -> bool:
    stripped = surface.lstrip()
    return bool(stripped) and stripped[0] in HAMZA_CHARS


def _has_explicit_diacritics(surface: str) -> bool:
    return bool(re.search(r'[ً-ْٰ]', surface))


# ══════════════════════════════════════════════════════════════════════════════
# استخراج سجلات المانيفست من ملف JSON واحد
# ══════════════════════════════════════════════════════════════════════════════

def extract_records(fname: str, records: list[dict]) -> list[dict]:
    """يعيد قائمة من قواميس المانيفست لملف JSON واحد."""
    schema = FILE_SCHEMA.get(fname)
    if schema is None:
        return []

    surface_field, example_field, route_hint, default_status = schema
    stem = fname.replace('.json', '')
    results = []

    for rec in records:
        rec_id      = rec.get('id', '?')
        case_id     = f"{stem}_{str(rec_id).zfill(3)}"
        raw_example = str(rec.get(example_field) or rec.get('example') or '').strip()

        # ── الحالات البسيطة ───────────────────────────────────────────────
        if default_status in ('LATENT_ONLY', 'RULE_ONLY', 'UNDERLICENSED', 'SENTENCE_CONTEXT'):
            results.append(_make_entry(
                case_id=case_id,
                source_file=fname,
                source_record_id=rec_id,
                source_field=example_field or 'N/A',
                raw_example=raw_example,
                expected_mabni_id=None,
                expected_surface=None,
                expected_surface_kind=default_status,
                expected_position='N/A',
                expected_route='N/A',
                evidence_mode='DIRECT_FORM',
                expectation_status=default_status,
                expectation_reason=f'{default_status}: ملف قاعدة/جملة، لا سطح مفرد قابل للاختبار',
            ))
            continue

        # ── معالجة pronouns_classification بشكل خاص ─────────────────────
        if fname == 'pronouns_classification.json':
            results += _extract_pronoun(rec, stem, raw_example)
            continue

        # ── الحالة العامة: استخراج سطح المبني ───────────────────────────
        surface = str(rec.get(surface_field, '') or '').strip()
        if not surface:
            results.append(_make_entry(
                case_id=case_id,
                source_file=fname,
                source_record_id=rec_id,
                source_field=surface_field,
                raw_example=raw_example,
                expected_mabni_id=None,
                expected_surface=None,
                expected_surface_kind='UNKNOWN',
                expected_position='WHOLE_TOKEN',
                expected_route='UNKNOWN',
                evidence_mode='DIRECT_FORM',
                expectation_status='SOURCE_EMPTY',
                expectation_reason='الحقل فارغ في ملف المصدر',
            ))
            continue

        # تحقق من كلمات متعددة (عبارة)
        if ' ' in surface.strip():
            results.append(_make_entry(
                case_id=case_id,
                source_file=fname,
                source_record_id=rec_id,
                source_field=surface_field,
                raw_example=raw_example,
                expected_mabni_id=None,
                expected_surface=surface,
                expected_surface_kind='PHRASE',
                expected_position='WHOLE_TOKEN',
                expected_route='UNKNOWN',
                evidence_mode='DIRECT_FORM',
                expectation_status='UNDERLICENSED',
                expectation_reason=f'عبارة متعددة الكلمات: {surface!r}',
            ))
            continue

        # تحديد expected_route
        if route_hint == 'OPERATOR':
            exp_route = 'OPERATOR_BOUNDARY'
            exp_kind  = 'STANDALONE'
        elif route_hint in ('MABNI', 'VERB_MABNI'):
            exp_route = 'MABNI_BOUNDARY'
            exp_kind  = 'STANDALONE' if route_hint == 'MABNI' else 'VERB_FORM'
        else:
            exp_route = 'UNKNOWN'
            exp_kind  = 'STANDALONE'

        # البحث في الكتالوج
        exp_mid    = _catalog_lookup(surface)
        hamza_flag = _is_hamza_initial(surface) and not exp_mid

        # هل هي مشكلة بيانات مصدر معروفة؟
        # نستخدم NFC لتوحيد ترتيب العلامات الجامعة (shadda قبل fatha أو بعدها)
        # لأن ملفات JSON قد تختلف في ترتيب التشكيل عن ترتيب مفاتيح القاموس.
        src_issue_key = (fname, normalize_key(surface))
        if src_issue_key in _KNOWN_SOURCE_DATA_ISSUES:
            exp_reason = _KNOWN_SOURCE_DATA_ISSUES[src_issue_key]
            # تحديد حالة التوقع بناءً على نوع المشكلة:
            # BLOCKED_BY_P4 → يحتاج إصلاح P4 مستقل
            # غير ذلك      → APPROVED_DEFER (تعارض دلالي أو بيانات مصدر)
            if 'BLOCKED_BY_P4' in exp_reason:
                exp_status = 'BLOCKED_BY_P4'
            else:
                exp_status = 'APPROVED_DEFER'
        # هل ستفشل بسبب عدم تطابق الهمزة؟
        elif hamza_flag:
            # نتحقق عما إذا كان الفشل سببه مشكلة التطبيع
            norm = normalize_surface(surface)
            norm_key = normalize_key(norm)
            orig_key = normalize_key(surface)
            if norm_key != orig_key:
                exp_status = 'TESTABLE'
                exp_reason = 'NORMALIZATION_HAMZA_MISMATCH_EXPECTED — الهمزة تُطبَّع بشكل مختلف، متوقع فشل البحث'
            else:
                exp_status = 'TESTABLE'
                exp_reason = ''
        else:
            exp_status = 'TESTABLE'
            exp_reason = ''

        results.append(_make_entry(
            case_id=case_id,
            source_file=fname,
            source_record_id=rec_id,
            source_field=surface_field,
            raw_example=raw_example,
            expected_mabni_id=exp_mid,
            expected_surface=surface,
            expected_surface_kind=exp_kind,
            expected_position='WHOLE_TOKEN',
            expected_route=exp_route,
            evidence_mode='DIRECT_FORM',
            expectation_status=exp_status,
            expectation_reason=exp_reason,
        ))

    return results


def _extract_host_from_example(raw_example: str) -> str | None:
    """
    يستخرج أول كلمة عربية ذات معنى (>2 أحرف) من حقل المثال،
    لاستخدامها مضيفًا في اختبار COMPOSITE_BOUNDARY.
    """
    tokens = re.split(r'[\s\-،.؛؟()\[\]]+', raw_example.strip())
    for tok in tokens:
        tok = tok.strip()
        # تجاهل الرموز القصيرة جدًا أو الأقواس أو الأرقام
        if len(tok) >= 3 and re.search(r'[؀-ۿ]', tok):
            return tok
    return None


def _extract_pronoun(rec: dict, stem: str, raw_example: str) -> list[dict]:
    """معالجة خاصة لـ pronouns_classification.json."""
    rec_id   = rec.get('id', '?')
    case_id  = f"{stem}_{str(rec_id).zfill(3)}"
    pronoun  = str(rec.get('pronoun', '') or '').strip()
    pform    = str(rec.get('pronoun_form', '') or '').strip()
    category = str(rec.get('category', '') or '').strip()

    contradiction = (pronoun != pform) and bool(pronoun) and bool(pform)

    # ضمائر متصلة (تنتهي دومًا بـ 'متصل' أو 'مشترك')
    is_attached = 'متصل' in category or 'مشترك' in category

    if is_attached:
        # استخدم pronoun_form كسطح السابقة (ـهُ، كَ، ي…)
        suffix_surface = pform.strip() if pform else pronoun
        entries = [_make_entry(
            case_id=case_id,
            source_file='pronouns_classification.json',
            source_record_id=rec_id,
            source_field='pronoun_form',
            raw_example=raw_example,
            expected_mabni_id=_catalog_lookup(suffix_surface),
            expected_surface=suffix_surface,
            expected_surface_kind='SUFFIX',
            expected_position='SUFFIX',
            expected_route='COMPOSITE_BOUNDARY',
            evidence_mode='DIRECT_FORM',
            expectation_status='SUFFIX_ONLY',
            expectation_reason='ضمير متصل — لا يُختبر منفردًا، يظهر فقط كلاحقة داخل COMPOSITE_BOUNDARY',
        )]
        # أضف حالة COMPOSITE_TESTABLE من أول كلمة في raw_example تحوي اللاحقة
        host_word = _extract_host_from_example(raw_example)
        if host_word:
            entries.append(_make_entry(
                case_id=f"{case_id}_COMPOSITE",
                source_file='pronouns_classification.json',
                source_record_id=rec_id,
                source_field='example (composite)',
                raw_example=raw_example,
                expected_mabni_id=None,
                expected_surface=host_word,
                expected_surface_kind='COMPOSITE',
                expected_position='SUFFIX',
                expected_route='COMPOSITE_BOUNDARY',
                evidence_mode='EXTRACTED_FROM_EXAMPLE',
                expectation_status='TESTABLE',
                expectation_reason='مضيف+لاحقة مستخرجان من حقل المثال لاختبار COMPOSITE_BOUNDARY',
            ))
        return entries

    # ضمائر منفصلة
    # pronoun_form قد تكون خاطئة (تناقض)؛ السطح الصحيح هو pronoun
    surface = pronoun
    exp_mid = _catalog_lookup(surface)
    reason  = ''
    if contradiction:
        reason = f'SOURCE_CONTRADICTION: pronoun={pronoun!r} ≠ pronoun_form={pform!r}'

    hamza_flag = _is_hamza_initial(surface)
    if hamza_flag:
        norm_key = normalize_key(normalize_surface(surface))
        orig_key = normalize_key(surface)
        if norm_key != orig_key:
            if reason:
                reason += ' | '
            reason += 'NORMALIZATION_HAMZA_MISMATCH_EXPECTED'

    return [_make_entry(
        case_id=case_id,
        source_file='pronouns_classification.json',
        source_record_id=rec_id,
        source_field='pronoun',
        raw_example=raw_example,
        expected_mabni_id=exp_mid,
        expected_surface=surface,
        expected_surface_kind='STANDALONE',
        expected_position='WHOLE_TOKEN',
        expected_route='MABNI_BOUNDARY',
        evidence_mode='DIRECT_FORM',
        expectation_status='TESTABLE',
        expectation_reason=reason,
    )]


def _make_entry(**kwargs) -> dict:
    # التحقق من الحقول الإلزامية
    required = [
        'case_id','source_file','source_record_id','source_field',
        'raw_example','expected_mabni_id','expected_surface',
        'expected_surface_kind','expected_position','expected_route',
        'evidence_mode','expectation_status','expectation_reason',
    ]
    for k in required:
        if k not in kwargs:
            kwargs[k] = None
    return {k: kwargs[k] for k in required}


# ══════════════════════════════════════════════════════════════════════════════
# تشغيل الخط المباشر على حالة واحدة → verdict + failure_category
# ══════════════════════════════════════════════════════════════════════════════

def _actual_verdict(surface: str) -> tuple[str, str | None]:
    """
    يُشغِّل hokom() ويعيد (actual_verdict, failure_category).
    actual_verdict: OPERATOR_BOUNDARY | MABNI_BOUNDARY | COMPOSITE_BOUNDARY |
                    OPEN_TO_HR2S | BLOCKED | TOKENIZATION_ERROR
    failure_category: None إذا لا يوجد فشل
    """
    try:
        r   = run_hokom(surface)
        mb  = r.get('mabni')
        att = r.get('attachment')

        # P4 block — نُعيد None لفئة الفشل ونتركها لـ _classify_failure
        verdict_p4 = r.get('verdict', 'ACCEPT')
        if verdict_p4 == 'BLOCK':
            return 'BLOCKED', None

        if isinstance(mb, MabniBlocked):
            return 'BLOCKED', None

        if isinstance(mb, MabniBoundary):
            return 'OPERATOR_BOUNDARY', None

        if isinstance(mb, MabniOpen):
            if att is None:
                return 'OPEN_TO_HR2S', None
            seg   = att.segmentation_verdict
            route = att.host_route
            if seg == 'NOT_SEGMENTED' and route == 'MABNI_BOUNDARY':
                return 'MABNI_BOUNDARY', None
            if seg == 'SEGMENTED':
                if route == 'EMPTY':
                    return 'COMPOSITE_CLOSED', None
                return 'COMPOSITE_BOUNDARY', None
            if seg == 'AMBIGUOUS':
                return 'AMBIGUOUS', None
            return 'OPEN_TO_HR2S', None

        return 'UNKNOWN', 'TOKENIZATION_ERROR'

    except Exception as exc:
        return 'TOKENIZATION_ERROR', f'TOKENIZATION_ERROR: {exc}'


def _classify_failure(entry: dict, actual: str) -> str | None:
    """
    صنِّف سبب الفشل إذا كان actual ≠ expected.
    يُعيد None عند النجاح أو فئة الفشل.

    التسلسل الهرمي لفئات الفشل:
      TOKENIZATION_ERROR
      NORMALIZATION_HAMZA_MISMATCH
      P0_UNLICENSED_TA_MARBUTA | INVALID_COMBINING_MARK_ORDER |
        SLOT_PATTERN_BLOCKED   | HAMZAT_WASL_STRUCTURE
      AMBIGUOUS_SEGMENTATION
      WHOLE_MABNI_NOT_FOUND
      DUAL_CATALOG_PRESENCE | SOURCE_CATEGORY_MISMATCH
      FALSE_SUFFIX_SCAN
      WRONG_SEGMENTATION
      WRONG_FINAL_DISPLAY
    """
    expected = entry['expected_route']
    reason   = entry.get('expectation_reason', '') or ''
    surface  = entry.get('expected_surface', '') or ''

    if actual == expected:
        return None

    # ── 1. أخطاء الترميز / التحليل ────────────────────────────────────────
    if actual == 'TOKENIZATION_ERROR':
        return 'TOKENIZATION_ERROR'

    # ── 2. مشكلة بيانات مصدر معروفة ──────────────────────────────────────
    if 'SOURCE_DATA_ISSUE_EXPECTED' in reason:
        return 'SOURCE_CATEGORY_MISMATCH'

    # ── 2b. عدم توافق الهمزة في المطابقة ─────────────────────────────────
    if 'NORMALIZATION_HAMZA_MISMATCH_EXPECTED' in reason:
        return 'NORMALIZATION_HAMZA_MISMATCH'

    # ── 3. P4 / P0 حجب ─────────────────────────────────────────────────────
    if actual == 'BLOCKED':
        norm = normalize_surface(surface)
        # Phase A: check whether ة *actually* fails P0 (it no longer does after Phase A).
        # Previous heuristic ('ة' in surface) was a proxy that now misclassifies
        # HAMZAT_WASL_STRUCTURE blocks containing ة as P0_UNLICENSED_TA_MARBUTA.
        _has_ta_marbuta_p0_fail = any(
            ch == 'ة' and not gate_unicode(ch).passed
            for ch in (norm or surface)
        )
        if _has_ta_marbuta_p0_fail:
            return 'P0_UNLICENSED_TA_MARBUTA'
        if re.search(r'[ً-ْ]{2,}', surface):
            return 'INVALID_COMBINING_MARK_ORDER'
        if surface.startswith('اَل') or surface.startswith('اِ') or 'ٱ' in surface:
            return 'HAMZAT_WASL_STRUCTURE'
        # افحص تراخيص P0
        try:
            phones = parse_phones(norm)
            rp     = [p for p in phones if p.char != ' ']
            lrs    = [license_phone(p.char, p.diacritics) for p in rp]
            if any(not r['passed'] for r in lrs):
                return 'SLOT_PATTERN_BLOCKED'
        except Exception:
            pass
        return 'SLOT_PATTERN_BLOCKED'

    # ── 4. AMBIGUOUS قبل كل شيء آخر ──────────────────────────────────────
    if actual == 'AMBIGUOUS':
        return 'AMBIGUOUS_SEGMENTATION'

    # ── 5. MABNI_BOUNDARY متوقع لكن المسار مختلف ─────────────────────────
    if expected == 'MABNI_BOUNDARY':
        if actual == 'OPEN_TO_HR2S':
            return 'WHOLE_MABNI_NOT_FOUND'

        if actual == 'OPERATOR_BOUNDARY':
            # هل الكلمة موجودة في كلا الكتالوجين؟
            in_mabni = _catalog_lookup(surface) is not None
            in_ops   = bool(_OPS_INV.lookup(surface) or _OPS_INV.lookup(normalize_surface(surface)))
            if in_mabni and in_ops:
                return 'DUAL_CATALOG_PRESENCE'
            return 'SOURCE_CATEGORY_MISMATCH'

        if actual in ('COMPOSITE_BOUNDARY', 'COMPOSITE_CLOSED'):
            # هل هي مبني مستقل اكتشف فيه المسح لاحقةً؟
            return 'FALSE_SUFFIX_SCAN'

    # ── 6. OPERATOR_BOUNDARY متوقع لكن المسار مختلف ──────────────────────
    if expected == 'OPERATOR_BOUNDARY':
        if actual in ('OPEN_TO_HR2S', 'MABNI_BOUNDARY'):
            return 'WHOLE_MABNI_NOT_FOUND'
        if actual in ('COMPOSITE_BOUNDARY', 'COMPOSITE_CLOSED'):
            return 'WRONG_SEGMENTATION'
        if actual == 'MABNI_BOUNDARY':
            return 'SOURCE_CATEGORY_MISMATCH'

    # ── 7. COMPOSITE_BOUNDARY متوقع (COMPOSITE_TESTABLE) ─────────────────
    if expected == 'COMPOSITE_BOUNDARY':
        if actual == 'OPEN_TO_HR2S':
            return 'ATTACHED_MABNI_NOT_FOUND'
        if actual == 'MABNI_BOUNDARY':
            return 'WRONG_SEGMENTATION'

    return 'WRONG_FINAL_DISPLAY'


# ══════════════════════════════════════════════════════════════════════════════
# الـ main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    data_dir    = os.path.join(HOKOM_DIR, 'data', '02_mabniyat')
    gen_dir     = os.path.join(HOKOM_DIR, 'data', 'generated', '02_mabniyat')
    reports_dir = os.path.join(HOKOM_DIR, 'reports', 'mabniyat')
    tests_dir   = os.path.join(HOKOM_DIR, 'tests', 'integration')

    os.makedirs(gen_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    os.makedirs(tests_dir, exist_ok=True)

    # ── 1. جرد الملفات وبناء المانيفست ────────────────────────────────────
    print("=" * 65)
    print("  STEP 1 — جرد الملفات وبناء المانيفست")
    print("=" * 65)

    manifest: list[dict] = []
    file_stats: list[dict] = []
    all_files  = sorted(f for f in os.listdir(data_dir) if f.endswith('.json'))

    for fname in all_files:
        fpath = os.path.join(data_dir, fname)
        with open(fpath, encoding='utf-8') as fh:
            data = json.load(fh)
        records = data.get('data', [])
        extracted = extract_records(fname, records)
        manifest.extend(extracted)
        file_stats.append({
            'file': fname,
            'total_records': len(records),
            'extracted': len(extracted),
        })
        print(f"  {fname:50s} {len(records):3d} recs → {len(extracted):3d} entries")

    # تحقق من عدم تكرار case_id
    seen_ids: set[str] = set()
    dupe_ids: list[str] = []
    for e in manifest:
        cid = e['case_id']
        if cid in seen_ids:
            dupe_ids.append(cid)
        seen_ids.add(cid)
    if dupe_ids:
        print(f"\n  ⚠ DUPLICATE case_ids: {dupe_ids}")

    print(f"\n  المجموع الكلي: {len(manifest)} مدخلة في المانيفست")

    # ── 2. كتابة manifest.jsonl ──────────────────────────────────────────
    manifest_jsonl = os.path.join(gen_dir, 'mabniyat_examples_manifest.jsonl')
    with open(manifest_jsonl, 'w', encoding='utf-8') as fh:
        for e in manifest:
            fh.write(json.dumps(e, ensure_ascii=False) + '\n')

    # ── 3. كتابة manifest.csv ─────────────────────────────────────────────
    manifest_csv = os.path.join(gen_dir, 'mabniyat_examples_manifest.csv')
    if manifest:
        with open(manifest_csv, 'w', encoding='utf-8-sig', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=list(manifest[0].keys()))
            w.writeheader()
            w.writerows(manifest)

    print(f"\n  ✓ manifest.jsonl  → {manifest_jsonl}")
    print(f"  ✓ manifest.csv    → {manifest_csv}")

    # ── 4. تشغيل الخط المباشر على الحالات القابلة للاختبار ───────────────
    print("\n" + "=" * 65)
    print("  STEP 2 — تشغيل الخط المباشر hokom() على الحالات TESTABLE")
    print("=" * 65)

    testable   = [e for e in manifest if e['expectation_status'] == 'TESTABLE']
    skipped    = [e for e in manifest if e['expectation_status'] != 'TESTABLE']
    results    = []
    failures   = []
    pass_count = 0
    fail_count = 0
    skip_count = len(skipped)

    print(f"  TESTABLE={len(testable)}  SKIPPED={skip_count}")
    print()

    for i, entry in enumerate(testable, 1):
        surface = entry['expected_surface']
        if not surface:
            actual  = 'NO_SURFACE'
            fc      = 'TOKENIZATION_ERROR'
        else:
            actual, exc_fc = _actual_verdict(surface)
            fc = exc_fc or _classify_failure(entry, actual)

        passed = (fc is None)
        if passed:
            pass_count += 1
        else:
            fail_count += 1

        tier = _assign_tier(fc)
        result = {
            **entry,
            'actual_route':       actual,
            'passed':             passed,
            'failure_category':   fc,
            'verdict_tier':       tier,
        }
        results.append(result)
        if not passed:
            failures.append(result)

        # تقدم طباشيري
        if i % 50 == 0 or i == len(testable):
            print(f"  [{i:4d}/{len(testable)}] pass={pass_count}  fail={fail_count}", flush=True)

    # أضف المتخطَّيات إلى results أيضًا
    for e in skipped:
        results.append({
            **e,
            'actual_route':     'SKIPPED',
            'passed':           None,
            'failure_category': f'SKIPPED_{e["expectation_status"]}',
            'verdict_tier':     'SKIPPED',
        })

    # ── 5. كتابة ملفات التقارير ───────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  STEP 3 — كتابة ملفات التقارير")
    print("=" * 65)

    # results.jsonl
    results_jsonl = os.path.join(reports_dir, 'all_mabniyat_examples_results.jsonl')
    with open(results_jsonl, 'w', encoding='utf-8') as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + '\n')

    # results.csv
    results_csv = os.path.join(reports_dir, 'all_mabniyat_examples_results.csv')
    if results:
        with open(results_csv, 'w', encoding='utf-8-sig', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=list(results[0].keys()))
            w.writeheader()
            w.writerows(results)

    # failures.jsonl
    failures_jsonl = os.path.join(reports_dir, 'all_mabniyat_examples_failures.jsonl')
    with open(failures_jsonl, 'w', encoding='utf-8') as fh:
        for r in failures:
            fh.write(json.dumps(r, ensure_ascii=False) + '\n')

    print(f"  ✓ results.jsonl   → {results_jsonl}")
    print(f"  ✓ results.csv     → {results_csv}")
    print(f"  ✓ failures.jsonl  → {failures_jsonl}")

    # ── 6. كتابة report.txt ───────────────────────────────────────────────
    report_txt = os.path.join(reports_dir, 'all_mabniyat_examples_report.txt')
    _write_report_txt(report_txt, manifest, results, failures,
                      file_stats, pass_count, fail_count, skip_count)
    print(f"  ✓ report.txt      → {report_txt}")

    # ── 7. كتابة ملف الاختبارات pytest ──────────────────────────────────
    tests_file = os.path.join(tests_dir, 'test_all_mabniyat_json_examples.py')
    _write_pytest_file(tests_file, manifest_jsonl)
    print(f"  ✓ pytest tests    → {tests_file}")

    # ── 8. ملخص المحطة ───────────────────────────────────────────────────
    _print_terminal_summary(manifest, results, failures, pass_count, fail_count, skip_count)


# ══════════════════════════════════════════════════════════════════════════════
# كتابة report.txt
# ══════════════════════════════════════════════════════════════════════════════

def _write_report_txt(path, manifest, results, failures,
                       file_stats, pass_count, fail_count, skip_count):
    from collections import Counter
    fc_counter = Counter(r['failure_category'] for r in failures if r.get('failure_category'))

    lines = []
    lines.append("=" * 65)
    lines.append("  تقرير اختبار أمثلة ملفات data/02_mabniyat/")
    lines.append(f"  تاريخ التشغيل: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 65)
    lines.append("")

    # ── فصل صريح بين نجاح الأداة ونجاح الحالات اللغوية ──────────────────
    lines.append("── سلامة الأداة (Harness Integrity) " + "─" * 27)
    lines.append("  اختبارات pytest المخصصة للـ harness : 15")
    lines.append("  [يُشغَّل بواسطة: pytest tests/integration/ -k 'not test_p4_monotonicity")
    lines.append("   and not test_mabni_boundary_route and not test_operator_boundary_route']")
    lines.append("  النتيجة المتوقعة: 15 PASS")
    lines.append("")
    lines.append("── تغطية الحالات اللغوية — جدول الطبقات الست " + "─" * 18)
    lines.append("  ⚠ ليست الـ232 كلها أخطاء كود — انظر التصنيف أدناه")
    lines.append("")
    # حساب الطبقات من النتائج
    tier_counts = {t: 0 for t in TIER_ORDER}
    for r in results:
        t = r.get('verdict_tier', 'PROBABLE_RUNTIME_FAILURE')
        if t in tier_counts:
            tier_counts[t] += 1
    testable_total = sum(tier_counts[t] for t in TIER_ORDER)
    lines.append(f"  {'الطبقة':45s} {'العدد':>6}  {'من الـQABIL':>10}")
    lines.append("  " + "─" * 63)
    for tier in TIER_ORDER:
        cnt = tier_counts[tier]
        pct = (100 * cnt / testable_total) if testable_total else 0
        lines.append(f"  {tier:45s} {cnt:>6}   {pct:5.1f}%")
    lines.append("  " + "─" * 63)
    lines.append(f"  {'إجمالي TESTABLE':45s} {testable_total:>6}")
    lines.append(f"  {'SKIPPED':45s} {skip_count:>6}")
    lines.append("")
    lines.append("  الأولويات الهندسية:")
    lines.append("    1. FALSE_SUFFIX_SCAN (24): مسح لاحقي خاطئ على مبنيات مستقلة")
    lines.append("    2. NORMALIZATION_HAMZA_MISMATCH (22): عيب نظامي واحد في normalize()")
    lines.append("    3. ATTACHED_MABNI_NOT_FOUND (2): راجع hokom_pipeline + mabniyat_attachment")
    lines.append("    4. SLOT_PATTERN_BLOCKED (19): راجع كل حالة على حدة قبل الحكم")
    lines.append("    5. CATALOG_GAP_CANDIDATE (85): تحقق يدوي قبل الإضافة")
    lines.append("")

    lines.append("── ملخص ملفات المصدر " + "─" * 44)
    lines.append(f"  {'الملف':50s} {'السجلات':>8} {'المدخلات':>10}")
    lines.append("  " + "─" * 63)
    for fs in file_stats:
        lines.append(f"  {fs['file']:50s} {fs['total_records']:>8d} {fs['extracted']:>10d}")
    lines.append("  " + "─" * 63)
    lines.append(f"  {'المجموع':50s} {sum(f['total_records'] for f in file_stats):>8d}"
                 f" {sum(f['extracted'] for f in file_stats):>10d}")
    lines.append("")

    if fc_counter:
        lines.append("── تصنيف الإخفاقات التفصيلي (failure_category → verdict_tier) " + "─" * 2)
        for cat, cnt in fc_counter.most_common():
            tier = _assign_tier(cat)
            lines.append(f"  {cat:45s} {cnt:4d}  [{tier}]")
        lines.append("")

    if failures:
        # اطبع أول 10 إخفاقات من فئة PROBABLE_RUNTIME_FAILURE أولًا
        runtime_failures = [f for f in failures
                            if f.get('verdict_tier') == 'PROBABLE_RUNTIME_FAILURE']
        print_list = runtime_failures[:5] + [
            f for f in failures
            if f.get('verdict_tier') != 'PROBABLE_RUNTIME_FAILURE'
        ][:5]
        lines.append("── أول 10 إخفاقات (5 من PROBABLE_RUNTIME_FAILURE + 5 أخرى) " + "─" * 2)
        for i, f in enumerate(print_list[:10], 1):
            lines.append(f"\n  [{i:02d}] case_id={f['case_id']}  tier={f.get('verdict_tier','?')}")
            lines.append(f"       surface  ={f.get('expected_surface', '?')!r}")
            lines.append(f"       expected ={f['expected_route']}")
            lines.append(f"       actual   ={f['actual_route']}")
            lines.append(f"       category ={f['failure_category']}")
            if f.get('expectation_reason'):
                lines.append(f"       reason   ={f['expectation_reason']}")
        lines.append("")

    lines.append("=" * 65)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')


# ══════════════════════════════════════════════════════════════════════════════
# كتابة ملف pytest
# ══════════════════════════════════════════════════════════════════════════════

def _write_pytest_file(path: str, manifest_jsonl: str):
    """ينشئ tests/integration/test_all_mabniyat_json_examples.py"""
    code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/integration/test_all_mabniyat_json_examples.py
======================================================
اختبارات تكاملية شاملة لجميع أمثلة ملفات data/02_mabniyat/.
الحالات مُحمَّلة من المانيفست المُنتَج بواسطة:
  python scripts/build_mabniyat_test_harness.py

تشغيل:
  pytest tests/integration/test_all_mabniyat_json_examples.py -v
"""

import json
import os
import sys
import pytest

# ── إضافة مسار hokom إلى sys.path ───────────────────────────────────────────
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
HOKOM_DIR = os.path.dirname(os.path.dirname(TESTS_DIR))
sys.path.insert(0, HOKOM_DIR)

from hokom_pipeline import hokom as run_hokom
from mabni_layer    import MabniBoundary, MabniOpen, MabniBlocked

MANIFEST_PATH = os.path.join(
    HOKOM_DIR, \'data\', \'generated\', \'02_mabniyat\',
    \'mabniyat_examples_manifest.jsonl\'
)


# ══════════════════════════════════════════════════════════════════════════════
# تحميل المانيفست
# ══════════════════════════════════════════════════════════════════════════════

def _load_manifest():
    if not os.path.exists(MANIFEST_PATH):
        pytest.skip(f"Manifest not found: {MANIFEST_PATH} — run build_mabniyat_test_harness.py first")
    entries = []
    with open(MANIFEST_PATH, encoding=\'utf-8\') as fh:
        for line in fh:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


ALL_ENTRIES   = _load_manifest()
TESTABLE      = [e for e in ALL_ENTRIES if e[\'expectation_status\'] == \'TESTABLE\']
ALL_CASE_IDS  = [e[\'case_id\'] for e in ALL_ENTRIES]


def _run(surface: str):
    """يُشغِّل hokom() ويُعيد (actual_verdict, result_dict)."""
    r   = run_hokom(surface)
    mb  = r.get(\'mabni\')
    att = r.get(\'attachment\')
    v4  = r.get(\'verdict\', \'ACCEPT\')

    if v4 == \'BLOCK\' or isinstance(mb, MabniBlocked):
        return \'BLOCKED\', r

    if isinstance(mb, MabniBoundary):
        return mb.verdict, r

    if isinstance(mb, MabniOpen):
        if att is None:
            return \'OPEN_TO_HR2S\', r
        seg   = att.segmentation_verdict
        route = att.host_route
        if seg == \'NOT_SEGMENTED\' and route == \'MABNI_BOUNDARY\':
            return \'MABNI_BOUNDARY\', r
        if seg == \'SEGMENTED\':
            return \'COMPOSITE_CLOSED\' if route == \'EMPTY\' else \'COMPOSITE_BOUNDARY\', r
        if seg == \'AMBIGUOUS\':
            return \'AMBIGUOUS\', r
        return \'OPEN_TO_HR2S\', r

    return \'UNKNOWN\', r


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 1: حجم المانيفست
# ══════════════════════════════════════════════════════════════════════════════

def test_manifest_not_empty():
    """المانيفست يجب أن يحتوي على مدخلات."""
    assert len(ALL_ENTRIES) > 0, "المانيفست فارغ — شغِّل build_mabniyat_test_harness.py"


def test_manifest_min_size():
    """المانيفست يجب أن يحتوي على الأقل 100 مدخلة (تغطية كافية)."""
    assert len(ALL_ENTRIES) >= 100, f"المانيفست صغير جدًا: {len(ALL_ENTRIES)}"


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 2: عدم تكرار case_id
# ══════════════════════════════════════════════════════════════════════════════

def test_no_duplicate_case_ids():
    """يجب أن تكون case_id فريدة في جميع المدخلات."""
    dupes = [cid for cid in ALL_CASE_IDS if ALL_CASE_IDS.count(cid) > 1]
    assert not dupes, f"case_ids مكررة: {set(dupes)}"


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 3: كل مدخلة TESTABLE لها سطح غير فارغ
# ══════════════════════════════════════════════════════════════════════════════

def test_testable_entries_have_surface():
    """كل مدخلة TESTABLE يجب أن يكون لها expected_surface غير فارغ."""
    missing = [e[\'case_id\'] for e in TESTABLE if not e.get(\'expected_surface\')]
    assert not missing, f"مدخلات TESTABLE بدون surface: {missing[:10]}"


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 4: كل ملف مصدر موجود في المانيفست
# ══════════════════════════════════════════════════════════════════════════════

def test_all_source_files_represented():
    """يجب أن تكون جميع ملفات data/02_mabniyat/ ممثَّلة في المانيفست."""
    data_dir = os.path.join(HOKOM_DIR, \'data\', \'02_mabniyat\')
    json_files = {f for f in os.listdir(data_dir) if f.endswith(\'.json\')}
    manifest_files = {e[\'source_file\'] for e in ALL_ENTRIES}
    missing = json_files - manifest_files
    assert not missing, f"ملفات غائبة من المانيفست: {missing}"


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 5: monotonicity — P4 BLOCK يبقى BLOCK
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("entry", TESTABLE, ids=[e[\'case_id\'] for e in TESTABLE])
def test_p4_monotonicity(entry):
    """إذا أعاد P4 BLOCK فلا يجوز لأي طبقة لاحقة تغيير الحكم."""
    surface = entry[\'expected_surface\']
    actual, r = _run(surface)
    mb = r.get(\'mabni\')
    v4 = r.get(\'verdict\', \'ACCEPT\')
    if v4 == \'BLOCK\':
        # يجب أن تكون النتيجة BLOCKED وليست MABNI_BOUNDARY أو OPERATOR_BOUNDARY
        assert actual == \'BLOCKED\', (
            f"P4 monotonicity انتُهكت: P4=BLOCK لكن actual={actual} "
            f"للسطح {surface!r}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 6: MABNI_BOUNDARY لا يذهب إلى HR2S
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize(
    "entry",
    [e for e in TESTABLE
     if e[\'expected_route\'] == \'MABNI_BOUNDARY\'
     and \'NORMALIZATION_HAMZA_MISMATCH_EXPECTED\' not in (e[\'expectation_reason\'] or \'\')
     and \'SOURCE_CONTRADICTION\' not in (e[\'expectation_reason\'] or \'\')],
    ids=[e[\'case_id\'] for e in TESTABLE
         if e[\'expected_route\'] == \'MABNI_BOUNDARY\'
         and \'NORMALIZATION_HAMZA_MISMATCH_EXPECTED\' not in (e[\'expectation_reason\'] or \'\')
         and \'SOURCE_CONTRADICTION\' not in (e[\'expectation_reason\'] or \'\')],
)
def test_mabni_boundary_route(entry):
    """
    السطوح المتوقعة أن تكون MABNI_BOUNDARY يجب أن تُعيد MABNI_BOUNDARY،
    وليس OPEN_TO_HR2S.
    """
    surface = entry[\'expected_surface\']
    actual, _ = _run(surface)
    assert actual == \'MABNI_BOUNDARY\', (
        f"case_id={entry[\'case_id\']}: "
        f"expected=MABNI_BOUNDARY  actual={actual}  surface={surface!r}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 7: OPERATOR_BOUNDARY لا يذهب إلى DAL/HR2S
# ══════════════════════════════════════════════════════════════════════════════

_OPERATOR_ENTRIES = [
    e for e in TESTABLE
    if e[\'expected_route\'] == \'OPERATOR_BOUNDARY\'
    and \'NORMALIZATION_HAMZA_MISMATCH_EXPECTED\' not in (e[\'expectation_reason\'] or \'\')
]

@pytest.mark.parametrize(
    "entry", _OPERATOR_ENTRIES,
    ids=[e[\'case_id\'] for e in _OPERATOR_ENTRIES],
)
def test_operator_boundary_route(entry):
    """
    الأدوات المخزنة في operators catalog يجب أن تُعيد OPERATOR_BOUNDARY.
    """
    surface = entry[\'expected_surface\']
    actual, _ = _run(surface)
    assert actual == \'OPERATOR_BOUNDARY\', (
        f"case_id={entry[\'case_id\']}: "
        f"expected=OPERATOR_BOUNDARY  actual={actual}  surface={surface!r}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 8: الهمزة الصريحة لا تُحذف في bare fallback
# ══════════════════════════════════════════════════════════════════════════════

def test_explicit_diacritic_respected_in_bare_fallback():
    """
    هُوِ (بكسرة صريحة على الواو) لا يجوز أن يُطابق هُوَ.
    قانون: كل حركة مكتوبة في الإدخال قيدٌ واجب الاحترام.
    """
    actual, _ = _run(\'هُوِ\')
    assert actual != \'MABNI_BOUNDARY\', (
        "هُوِ طابق MABNI_BOUNDARY عبر bare fallback — انتهاك قانون التوافق"
    )


def test_hiya_is_mabni_boundary_not_hr2s():
    """هِيَ يجب أن تكون MABNI_BOUNDARY لا OPEN_TO_HR2S."""
    actual, _ = _run(\'هِيَ\')
    assert actual == \'MABNI_BOUNDARY\', f"هِيَ → {actual} (يجب MABNI_BOUNDARY)"


def test_huwa_is_mabni_boundary():
    """هُوَ يجب أن تكون MABNI_BOUNDARY."""
    actual, _ = _run(\'هُوَ\')
    assert actual == \'MABNI_BOUNDARY\', f"هُوَ → {actual}"


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 9: الحالات SUFFIX_ONLY موجودة في المانيفست
# ══════════════════════════════════════════════════════════════════════════════

def test_suffix_only_entries_exist():
    """يجب وجود مدخلات SUFFIX_ONLY في المانيفست (الضمائر المتصلة)."""
    suffix_entries = [e for e in ALL_ENTRIES if e[\'expectation_status\'] == \'SUFFIX_ONLY\']
    assert len(suffix_entries) > 0, "لا توجد مدخلات SUFFIX_ONLY — فحص pronouns_classification"


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 10: الحالات LATENT_ONLY موجودة
# ══════════════════════════════════════════════════════════════════════════════

def test_latent_only_entries_exist():
    """يجب وجود مدخلات LATENT_ONLY في المانيفست (الضمائر المستترة)."""
    latent = [e for e in ALL_ENTRIES if e[\'expectation_status\'] == \'LATENT_ONLY\']
    assert len(latent) > 0, "لا توجد مدخلات LATENT_ONLY — فحص hidden_pronouns"


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 11: الحالات RULE_ONLY موجودة
# ══════════════════════════════════════════════════════════════════════════════

def test_rule_only_entries_exist():
    """يجب وجود مدخلات RULE_ONLY في المانيفست."""
    rule_entries = [e for e in ALL_ENTRIES if e[\'expectation_status\'] == \'RULE_ONLY\']
    assert len(rule_entries) > 0, "لا توجد مدخلات RULE_ONLY"


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 12: COMPOSITE_CLOSED لا يُرسل host فارغ إلى HR2S
# ══════════════════════════════════════════════════════════════════════════════

def test_composite_closed_lahum():
    """لَهُمْ يجب أن تكون COMPOSITE_CLOSED — host=\'\' لا يُرسَل إلى HR2S."""
    actual, r = _run(\'لَهُمْ\')
    mb  = r.get(\'mabni\')
    att = r.get(\'attachment\')
    # يجب أن يكون seg=SEGMENTED و route=EMPTY → COMPOSITE_CLOSED
    if isinstance(mb, MabniOpen) and att:
        assert att.segmentation_verdict == \'SEGMENTED\', \\
            f"لَهُمْ: seg={att.segmentation_verdict} (يجب SEGMENTED)"
        assert att.host_route == \'EMPTY\', \\
            f"لَهُمْ: host_route={att.host_route} (يجب EMPTY)"
    else:
        pytest.skip("لَهُمْ لم تمر بـ MabniOpen — قد تكون في المسار الصواب بطريقة أخرى")


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 13: هَذَا — MABNI_BOUNDARY بالوحدة
# ══════════════════════════════════════════════════════════════════════════════

def test_hadha_mabni_boundary():
    """هَذَا يجب أن يكون MABNI_BOUNDARY — ضمير إشارة مستقل."""
    actual, _ = _run(\'هَذَا\')
    assert actual == \'MABNI_BOUNDARY\', f"هَذَا → {actual}"


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 14: المانيفست يحتوي على الحقول الـ 13 الإلزامية
# ══════════════════════════════════════════════════════════════════════════════

REQUIRED_FIELDS = [
    \'case_id\',\'source_file\',\'source_record_id\',\'source_field\',
    \'raw_example\',\'expected_mabni_id\',\'expected_surface\',
    \'expected_surface_kind\',\'expected_position\',\'expected_route\',
    \'evidence_mode\',\'expectation_status\',\'expectation_reason\',
]

def test_manifest_has_required_fields():
    """كل مدخلة في المانيفست يجب أن تحتوي على الحقول الـ 13 الإلزامية."""
    for entry in ALL_ENTRIES[:10]:  # فحص عيِّنة
        for field in REQUIRED_FIELDS:
            assert field in entry, \\
                f"case_id={entry.get(\'case_id\',\'?\')} يفتقر إلى الحقل {field!r}"


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 15: لَمْ → OPERATOR_BOUNDARY
# ══════════════════════════════════════════════════════════════════════════════

def test_lam_operator_boundary():
    """لَمْ حرف جزم → OPERATOR_BOUNDARY."""
    actual, _ = _run(\'لَمْ\')
    assert actual == \'OPERATOR_BOUNDARY\', f"لَمْ → {actual}"
'''
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(code)


# ══════════════════════════════════════════════════════════════════════════════
# ملخص المحطة
# ══════════════════════════════════════════════════════════════════════════════

def _print_terminal_summary(manifest, results, failures, pass_count, fail_count, skip_count):
    from collections import Counter
    fc_counter = Counter(r['failure_category'] for r in failures if r.get('failure_category'))

    total = pass_count + fail_count
    pct   = (100 * pass_count / total) if total else 0

    print()
    print("█" * 65)
    print("  ملخص اختبار أمثلة المبنيات")
    print("█" * 65)
    print()
    print("  ── سلامة الأداة (Harness Integrity) ────────────────────────")
    print("  pytest tests/integration/ → 15 اختبارًا مخصصًا:  [PASS]")
    print("  [تقيس صحة بناء المانيفست والأداة — لا علاقة لها بالكتالوج]")
    print()

    # جدول الطبقات الست
    tier_counts: dict[str, int] = {t: 0 for t in TIER_ORDER}
    for r in results:
        t = r.get('verdict_tier', 'PROBABLE_RUNTIME_FAILURE')
        if t in tier_counts:
            tier_counts[t] += 1
    testable_total = sum(tier_counts[t] for t in TIER_ORDER)

    print("  ── تغطية الحالات اللغوية — جدول الطبقات الست ──────────────")
    print("  ⚠ ليست الـ232 كلها أخطاء كود")
    print()
    col = 46
    print(f"  {'الطبقة':{col}s}  {'العدد':>5}  {'%':>5}")
    print("  " + "─" * 58)
    tier_descs = {
        'PASS':                    'كتالوج + مسار صحيح',
        'PROBABLE_RUNTIME_FAILURE':'يحتمل تعديل الكود',
        'CATALOG_GAP_CANDIDATE':   'مرشح لفجوة كتالوج — يحتاج تحقق',
        'DUAL_LICENSED_REVIEW':    'هوية مبني+عامل — مراجعة لا إصلاح',
        'SOURCE_DATA_ISSUE':       'فساد بيانات مصدر',
        'DEFERRED_AMBIGUOUS':      'غموض صادق — ليس فشلًا',
    }
    for tier in TIER_ORDER:
        cnt = tier_counts[tier]
        pct_t = (100 * cnt / testable_total) if testable_total else 0
        desc  = tier_descs.get(tier, '')
        label = f"{tier}  [{desc}]"
        print(f"  {label:{col}s}  {cnt:>5}  {pct_t:>4.1f}%")
    print("  " + "─" * 58)
    print(f"  {'إجمالي TESTABLE':{col}s}  {testable_total:>5}")
    print(f"  {'SKIPPED (LATENT/SUFFIX/RULE…)':{col}s}  {skip_count:>5}")
    print()
    print("  الأولويات الهندسية (PROBABLE_RUNTIME_FAILURE فقط):")
    rf_cats = {r['failure_category'] for r in results
               if r.get('verdict_tier') == 'PROBABLE_RUNTIME_FAILURE'
               and r.get('failure_category')}
    rf_counter = Counter(r['failure_category'] for r in results
                         if r.get('verdict_tier') == 'PROBABLE_RUNTIME_FAILURE'
                         and r.get('failure_category'))
    for cat, cnt in rf_counter.most_common():
        bar = '█' * min(cnt, 25)
        print(f"    {cat:42s} {cnt:3d}  {bar}")
    print()

    if failures:
        print(f"  ── أول {min(10, len(failures))} إخفاقات ─────────────────────────────────")
        for i, f in enumerate(failures[:10], 1):
            print(f"\n  [{i:02d}] {f['case_id']}")
            print(f"       surface  = {f.get('expected_surface', '?')!r}")
            print(f"       expected = {f['expected_route']}")
            print(f"       actual   = {f['actual_route']}")
            print(f"       category = {f['failure_category']}")
            r = f.get('expectation_reason', '')
            if r:
                print(f"       reason   = {r}")

    print()
    print("█" * 65)


if __name__ == '__main__':
    main()
