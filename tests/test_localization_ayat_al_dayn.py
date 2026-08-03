"""
tests/test_localization_ayat_al_dayn.py

Unit tests for the Ayat al-Dayn localization service and its wiring into
the demo script's CSV / HTML renderers.

Scope:
  - YAML loads correctly.
  - load_locale() returns well-formed dicts.
  - Unknown locales raise ValueError (fail-closed).
  - translate_header() covers both CSV sections, both locales.
  - translate_value() covers key enum categories in Arabic.
  - Missing translations emit UserWarning and fall back (never silently wrong).
  - format_csv(lang='ar') produces Arabic headers.
  - format_csv(lang='ar') content is BOM-free (BOM added by write_outputs on disk).
  - format_csv(lang='en') is byte-identical to the no-lang baseline.
  - generate_taaqol_layer_csv(lang='ar') translates layer_name headers.
  - format_html(lang='ar') sets dir="rtl" and lang="ar".
  - format_html(lang='en') sets dir="ltr" and lang="en".
  - Canonical identifiers are never translated (claim_key, evaluation_id).
  - translate_value with lang='en' is a no-op.
  - All 18 layer_name values have Arabic translations.

These tests are presentation-only: no pipeline logic is exercised.
All tests use synthetic stub results — the live pipeline is NOT called.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pytest

# ── path setup ────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / 'src'))

from hokom.demo.localization import (
    load_locale,
    translate_header,
    translate_value,
    get_html_label,
    _load_yaml,
)

# ── minimal stub result (no pipeline calls) ───────────────────────────────────
_STUB_RESULT: dict = {
    'token_index': 1,
    'original_surface': 'يَا',
    'normalization': {'normalized_surface': 'يا'},
    'segmentation': {'proclitics': [], 'host_surface': 'يا', 'enclitics': []},
    'word_class': {
        'class': 'HARF',
        'subclass': 'CLOSED_FUNCTION_WORD',
        'verdict': 'WORD_CLASS_ACCEPTED',
        'inflection_skipped_reason': 'WORD_CLASS_ACCEPTED',
    },
    'root_analysis': {
        'root_state': 'KNOWN',
        'canonical_root': '',
        'root_candidates': [],
        'cra_form_family': '',
        'cra_suffix_stripped': '',
        'cra_reason_codes': [],
        'phase4a_residuals': [],
        'wazn': '',
        'masdar': '',
        'derivative_type': '',
    },
    'morphosyntax': {
        'number': '', 'gender': '', 'person': '',
        'tense_aspect': '', 'mood': '', 'voice': '',
        'ambiguity_candidates': [],
    },
    'composite_verdict': {
        'overall_verdict': 'COMPOSITE',
        'has_unresolved_claims': False,
        'licensed_claims': [],
        'deferred_claims': [],
        'not_opened_layers': [],
        'active_residuals': [],
        'by_layer': [],
    },
    'taaqol': {
        'available': False,
        'taaqol_verdict': 'DEFERRED',
        'upstream_verdict': 'DEFER',
        'effective_verdict': 'DEFERRED',
        'gamma_result': 'UNAVAILABLE',
        'transition_gate_result': 'UNAVAILABLE',
        'slot_graph_digest': '',
        'center_scope': '',
        'bridge_id': '',
        'trace_events': [],
        'reason_codes': [],
        'taaqol_commit': '',
        'hokom_commit': '',
        'runtime': {
            'kernel_loaded': False,
            'slot_graph_created': False,
            'gamma_executed': False,
            'gate_executed': False,
            'failure_code': '',
            'failure_detail': '',
            'trace_event_count': 0,
            'vendor_sha': '',
            'slot_graph_slots': [],
        },
    },
    'h11_h15': {'reached': False, 'filled_slots': []},
    'typed_slots': [],
    'claim_key': 'ck-stub-001',
    'evaluation_id': 'ev-stub-001',
    'pipeline_verdict': 'ACCEPT',
    'error': None,
}

_STUB_STATS: dict = {
    'token_count': 1,
    'typed_bundles': 0,
    'taaqol_live': 0,
    'h11_h15_reached': 0,
    'early_stops': 1,
    'root_states': {'KNOWN': 1, 'DEFERRED': 0, 'UNKNOWN': 0, 'AMBIGUOUS': 0},
    'overall_verdicts': {'COMPOSITE': 1},
    'taaqol_verdicts': {'DEFERRED': 1},
    'taaqol_constitutional_exemptions': 0,
    'taaqol_unexplained_coverage_gap': 0,
}

_STUB_CHECKS: dict = {
    'TAAQOL_RUNTIME_ACTIVE': 0,
    'TAAQOL_RUNTIME_INACTIVE': 1,
    'TAAQOL_CONSTITUTIONAL_EXEMPTIONS': 0,
    'TAAQOL_UNEXPLAINED_COVERAGE_GAP': 0,
    'SLOTS_MISSING_STATE': 0,
    'LICENSED_WITHOUT_SCOPE': 0,
    'MISSING_EVALUATION_ID': 0,
    'EVALUATION_ID_COLLISIONS': 0,
    'MISSING_TAAQOL_TRACE_ACTIVE': 0,
    'CLAIM_KEY_NONDETERMINISM': 0,
    'UNTYPED_PAYLOADS': 0,
    'SILENT_FALLBACKS': 0,
    'UNEXPECTED_RUNTIME_ERRORS': 0,
}

_STUB_META: dict = {
    'head': 'abc1234', 'vendor_sha': 'def5678',
    'python': '3.12.4', 'platform': 'Darwin',
    'timestamp': '2026-01-01T00:00:00+00:00',
    'ayat_source': 'tests/stub',
}


# ─────────────────────────────────────────────────────────────────────────────
# 1. YAML loads without error
# ─────────────────────────────────────────────────────────────────────────────
def test_yaml_loads_without_error():
    data = _load_yaml()
    assert isinstance(data, dict), "YAML root must be a dict"
    assert 'en' in data, "YAML must have 'en' top-level key"
    assert 'ar' in data, "YAML must have 'ar' top-level key"


# ─────────────────────────────────────────────────────────────────────────────
# 2. load_locale('en') returns well-formed dict
# ─────────────────────────────────────────────────────────────────────────────
def test_load_locale_en_structure():
    locale = load_locale('en')
    assert 'csv_headers' in locale
    assert 'results' in locale['csv_headers']
    assert 'layers' in locale['csv_headers']
    assert 'enums' in locale
    assert 'html_labels' in locale


# ─────────────────────────────────────────────────────────────────────────────
# 3. load_locale('ar') returns well-formed dict
# ─────────────────────────────────────────────────────────────────────────────
def test_load_locale_ar_structure():
    locale = load_locale('ar')
    assert 'csv_headers' in locale
    assert 'enums' in locale
    assert 'html_labels' in locale


# ─────────────────────────────────────────────────────────────────────────────
# 4. Unknown locale raises ValueError
# ─────────────────────────────────────────────────────────────────────────────
def test_load_locale_unknown_raises():
    with pytest.raises(ValueError, match="Unknown locale"):
        load_locale('xx')


# ─────────────────────────────────────────────────────────────────────────────
# 5. translate_header English results section returns same key
# ─────────────────────────────────────────────────────────────────────────────
def test_translate_header_en_results_passthrough():
    assert translate_header('word_class', 'en', 'results') == 'word_class'
    assert translate_header('token_index', 'en', 'results') == 'token_index'
    assert translate_header('overall_verdict', 'en', 'results') == 'overall_verdict'


# ─────────────────────────────────────────────────────────────────────────────
# 6. translate_header Arabic results section returns Arabic strings
# ─────────────────────────────────────────────────────────────────────────────
def test_translate_header_ar_results():
    result = translate_header('word_class', 'ar', 'results')
    assert result == 'فئة الكلمة', f"Expected Arabic header, got {result!r}"

    result = translate_header('token_index', 'ar', 'results')
    assert result == 'رقم الكلمة', f"Expected Arabic header, got {result!r}"

    result = translate_header('overall_verdict', 'ar', 'results')
    assert result == 'الحكم الإجمالي', f"Expected Arabic header, got {result!r}"


# ─────────────────────────────────────────────────────────────────────────────
# 7. translate_header Arabic layers section returns Arabic strings
# ─────────────────────────────────────────────────────────────────────────────
def test_translate_header_ar_layers():
    result = translate_header('layer_name', 'ar', 'layers')
    assert result == 'اسم الطبقة', f"Expected Arabic header, got {result!r}"

    result = translate_header('layer_state', 'ar', 'layers')
    assert result == 'حالة الطبقة', f"Expected Arabic header, got {result!r}"


# ─────────────────────────────────────────────────────────────────────────────
# 8. translate_value word_class Arabic
# ─────────────────────────────────────────────────────────────────────────────
def test_translate_value_word_class_ar():
    assert translate_value('word_class', 'FI3L', 'ar') == 'فعل'
    assert translate_value('word_class', 'HARF', 'ar') == 'حرف'
    assert translate_value('word_class', 'ISM', 'ar') == 'اسم'


# ─────────────────────────────────────────────────────────────────────────────
# 9. translate_value layer_state Arabic
# ─────────────────────────────────────────────────────────────────────────────
def test_translate_value_layer_state_ar():
    assert translate_value('layer_state', 'EXECUTED', 'ar') == 'منفَّذ'
    assert translate_value('layer_state', 'BLOCKED', 'ar') == 'محظور'
    assert translate_value('layer_state', 'NOT_REACHED', 'ar') == 'لم يُبلَغ'
    assert translate_value('layer_state', 'SKIPPED_BY_CONTRACT', 'ar') == 'مُتخطَّى بالعقد'


# ─────────────────────────────────────────────────────────────────────────────
# 10. Missing enum emits UserWarning and falls back to original value
# ─────────────────────────────────────────────────────────────────────────────
def test_translate_value_missing_emits_warning():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        result = translate_value('layer_state', 'NONEXISTENT_STATE', 'ar')
    assert result == 'NONEXISTENT_STATE', "Must fall back to original value"
    assert any('NONEXISTENT_STATE' in str(w.message) for w in caught), \
        "Must emit UserWarning mentioning the missing value"


# ─────────────────────────────────────────────────────────────────────────────
# 11. format_csv(lang='ar') produces Arabic column headers
# ─────────────────────────────────────────────────────────────────────────────
def test_format_csv_ar_headers():
    # Import the module-level format_csv via the demo script
    import importlib.util, sys as _sys
    _script = REPO_ROOT / 'scripts' / 'demo_ayat_al_dayn.py'
    spec = importlib.util.spec_from_file_location('_demo', _script)
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)  # type: ignore[union-attr]

    csv_text = demo.format_csv([_STUB_RESULT], lang='ar')
    first_line = csv_text.splitlines()[0]
    assert 'فئة الكلمة' in first_line, \
        f"Arabic header 'فئة الكلمة' missing from first CSV line: {first_line!r}"
    assert 'رقم الكلمة' in first_line, \
        f"Arabic header 'رقم الكلمة' missing from first CSV line: {first_line!r}"


# ─────────────────────────────────────────────────────────────────────────────
# 12. format_csv(lang='ar') content has no BOM (BOM added at write time)
# ─────────────────────────────────────────────────────────────────────────────
def test_format_csv_ar_no_inline_bom():
    import importlib.util
    _script = REPO_ROOT / 'scripts' / 'demo_ayat_al_dayn.py'
    spec = importlib.util.spec_from_file_location('_demo2', _script)
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)  # type: ignore[union-attr]

    csv_text = demo.format_csv([_STUB_RESULT], lang='ar')
    # BOM is the Unicode code point U+FEFF; it must NOT be in the str itself
    assert not csv_text.startswith('﻿'), \
        "format_csv() must not embed BOM — utf-8-sig encoding is applied at write time"


# ─────────────────────────────────────────────────────────────────────────────
# 13. format_csv(lang='en') is identical to the no-lang baseline (backward compat)
# ─────────────────────────────────────────────────────────────────────────────
def test_format_csv_en_identical_to_baseline():
    import importlib.util
    _script = REPO_ROOT / 'scripts' / 'demo_ayat_al_dayn.py'
    spec = importlib.util.spec_from_file_location('_demo3', _script)
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)  # type: ignore[union-attr]

    baseline = demo.format_csv([_STUB_RESULT])          # default lang='en'
    explicit_en = demo.format_csv([_STUB_RESULT], lang='en')
    assert baseline == explicit_en, \
        "format_csv() with no lang and with lang='en' must produce identical output"


# ─────────────────────────────────────────────────────────────────────────────
# 14. generate_taaqol_layer_csv(lang='ar') translates layer_name header
# ─────────────────────────────────────────────────────────────────────────────
def test_generate_taaqol_layer_csv_ar_headers():
    import importlib.util
    _script = REPO_ROOT / 'scripts' / 'demo_ayat_al_dayn.py'
    spec = importlib.util.spec_from_file_location('_demo4', _script)
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)  # type: ignore[union-attr]

    csv_text = demo.generate_taaqol_layer_csv([_STUB_RESULT], lang='ar')
    first_line = csv_text.splitlines()[0]
    assert 'اسم الطبقة' in first_line, \
        f"Arabic header 'اسم الطبقة' missing from layers CSV header: {first_line!r}"
    assert 'حالة الطبقة' in first_line, \
        f"Arabic header 'حالة الطبقة' missing from layers CSV header: {first_line!r}"


# ─────────────────────────────────────────────────────────────────────────────
# 15. format_html(lang='ar') sets lang="ar" and dir="rtl"
# ─────────────────────────────────────────────────────────────────────────────
def test_format_html_ar_attributes():
    import importlib.util
    _script = REPO_ROOT / 'scripts' / 'demo_ayat_al_dayn.py'
    spec = importlib.util.spec_from_file_location('_demo5', _script)
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)  # type: ignore[union-attr]

    html = demo.format_html([_STUB_RESULT], _STUB_STATS, _STUB_CHECKS, _STUB_META, lang='ar')
    assert 'lang="ar"' in html, "Arabic HTML must have lang=\"ar\" on <html> tag"
    assert 'dir="rtl"' in html, "Arabic HTML must have dir=\"rtl\" on <html> tag"


# ─────────────────────────────────────────────────────────────────────────────
# 16. format_html(lang='en') sets lang="en" and dir="ltr"
# ─────────────────────────────────────────────────────────────────────────────
def test_format_html_en_attributes():
    import importlib.util
    _script = REPO_ROOT / 'scripts' / 'demo_ayat_al_dayn.py'
    spec = importlib.util.spec_from_file_location('_demo6', _script)
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)  # type: ignore[union-attr]

    html = demo.format_html([_STUB_RESULT], _STUB_STATS, _STUB_CHECKS, _STUB_META, lang='en')
    assert 'lang="en"' in html, "English HTML must have lang=\"en\" on <html> tag"
    assert 'dir="ltr"' in html, "English HTML must have dir=\"ltr\" on <html> tag"


# ─────────────────────────────────────────────────────────────────────────────
# 17. Canonical identifiers are NOT translated (claim_key, evaluation_id)
# ─────────────────────────────────────────────────────────────────────────────
def test_canonical_identifiers_not_translated():
    # In the YAML, claim_key and evaluation_id map to themselves in 'ar'
    assert translate_header('claim_key', 'ar', 'results') == 'claim_key'
    assert translate_header('evaluation_id', 'ar', 'results') == 'evaluation_id'
    assert translate_header('claim_key', 'ar', 'layers') == 'claim_key'
    assert translate_header('evaluation_id', 'ar', 'layers') == 'evaluation_id'
    # Also canonical SHA / commit / digest headers
    assert translate_header('slot_graph_digest', 'ar', 'layers') == 'slot_graph_digest'
    assert translate_header('runtime_vendor_sha', 'ar', 'layers') == 'runtime_vendor_sha'


# ─────────────────────────────────────────────────────────────────────────────
# 18. translate_value with lang='en' is a no-op (English is canonical)
# ─────────────────────────────────────────────────────────────────────────────
def test_translate_value_en_noop():
    assert translate_value('word_class', 'FI3L', 'en') == 'FI3L'
    assert translate_value('layer_state', 'EXECUTED', 'en') == 'EXECUTED'
    assert translate_value('root_state', 'DEFERRED', 'en') == 'DEFERRED'


# ─────────────────────────────────────────────────────────────────────────────
# 19. All 18 layer_name values have Arabic translations in the YAML
# ─────────────────────────────────────────────────────────────────────────────
_EXPECTED_LAYER_NAMES = {
    'ARTICLE', 'BAB', 'BOUNDARY', 'DERIVATIVE', 'EVIDENCE',
    'INFLECTIONAL', 'LEXICAL_FUNCTIONAL', 'MASDAR', 'MORPHOSYNTAX',
    'NORMALIZATION', 'PARADIGM', 'PATTERN', 'PHONOLOGICAL', 'RADICAL',
    'RESIDUAL', 'SEGMENTATION', 'SURFACE_IDENTITY', 'WORD_CLASS',
}

def test_all_layer_names_have_arabic_translations():
    locale_ar = load_locale('ar')
    layer_names = locale_ar.get('enums', {}).get('layer_name', {})
    missing = _EXPECTED_LAYER_NAMES - set(layer_names.keys())
    assert not missing, \
        f"Missing Arabic translations for layer_name keys: {sorted(missing)}"
    # All values must be non-empty Arabic strings (contain Arabic script)
    import unicodedata
    for name, translation in layer_names.items():
        assert translation, f"Empty translation for layer_name={name!r}"
        has_arabic = any(
            unicodedata.name(c, '').startswith('ARABIC')
            for c in translation
        )
        assert has_arabic, \
            f"layer_name={name!r} translation {translation!r} contains no Arabic characters"


# ─────────────────────────────────────────────────────────────────────────────
# 20. get_html_label returns Arabic for known keys, warns for unknown keys
# ─────────────────────────────────────────────────────────────────────────────
def test_get_html_label_ar():
    assert get_html_label('h2_stats', 'ar') == 'إحصاءات'
    assert get_html_label('h2_integrity', 'ar') == 'صحة النظام'
    assert get_html_label('h2_tokens', 'ar') == 'الكلمات — انقر لتفاصيل كل طبقة'

def test_get_html_label_en():
    assert get_html_label('h2_stats', 'en') == 'Statistics'
    assert get_html_label('h2_integrity', 'en') == 'System Integrity'

def test_get_html_label_missing_emits_warning():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        result = get_html_label('NONEXISTENT_LABEL', 'ar')
    assert result == 'NONEXISTENT_LABEL', "Must fall back to key"
    assert any('NONEXISTENT_LABEL' in str(w.message) for w in caught), \
        "Must emit UserWarning for missing label"


# ═════════════════════════════════════════════════════════════════════════════
# Phase 2 — Composite-value, boolean, slot-ID, reason-code, terminal-label
#            localization tests (12 new tests, tests 21–32)
# ═════════════════════════════════════════════════════════════════════════════

from hokom.demo.localization import translate_composite_value, get_terminal_label  # noqa: E402

# ─────────────────────────────────────────────────────────────────────────────
# 21. Boolean strings translate to نعم/لا in Arabic CSV output
# ─────────────────────────────────────────────────────────────────────────────
def test_boolean_values_translated_in_arabic_csv():
    """True/False in h11_h15_reached and has_unresolved_claims must become نعم/لا."""
    import importlib.util
    _script = REPO_ROOT / 'scripts' / 'demo_ayat_al_dayn.py'
    spec = importlib.util.spec_from_file_location('_demo_bool', _script)
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)

    stub = dict(_STUB_RESULT)
    stub['h11_h15'] = {'reached': True, 'filled_slots': ['NUMBER_SLOT']}
    stub['composite_verdict'] = dict(_STUB_RESULT['composite_verdict'])
    stub['composite_verdict']['has_unresolved_claims'] = True

    csv_text = demo.format_csv([stub], lang='ar')
    assert 'True' not in csv_text, \
        "Arabic CSV must not contain literal 'True'; expected 'نعم'"
    assert 'False' not in csv_text, \
        "Arabic CSV must not contain literal 'False'; expected 'لا'"
    assert 'نعم' in csv_text, "Arabic CSV must contain 'نعم' for boolean True"


# ─────────────────────────────────────────────────────────────────────────────
# 22. not_opened_layers translates every member with ؛ separator
# ─────────────────────────────────────────────────────────────────────────────
def test_not_opened_layers_translated_in_arabic_csv():
    """Every layer name in not_opened_layers must appear in Arabic in the CSV."""
    import importlib.util
    _script = REPO_ROOT / 'scripts' / 'demo_ayat_al_dayn.py'
    spec = importlib.util.spec_from_file_location('_demo_layers', _script)
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)

    stub = dict(_STUB_RESULT)
    stub['composite_verdict'] = dict(_STUB_RESULT['composite_verdict'])
    stub['composite_verdict']['not_opened_layers'] = [
        'RADICAL', 'PATTERN', 'BAB', 'MASDAR',
    ]

    csv_text = demo.format_csv([stub], lang='ar')

    # All four layer names must be translated
    assert 'الجذري' in csv_text, "RADICAL must translate to الجذري"
    assert 'الصيغة' in csv_text, "PATTERN must translate to الصيغة"
    assert 'الباب' in csv_text, "BAB must translate to الباب"
    assert 'المصدر' in csv_text, "MASDAR must translate to المصدر"

    # Raw English layer names must not appear in the not_opened_layers cell
    # (they may appear elsewhere in the CSV as enum values, so we check cell-level)
    assert 'RADICAL; PATTERN' not in csv_text, \
        "Untranslated English list 'RADICAL; PATTERN' must not appear in Arabic CSV"


# ─────────────────────────────────────────────────────────────────────────────
# 23. licensed_claims translates every slot ID
# ─────────────────────────────────────────────────────────────────────────────
def test_licensed_claims_slot_ids_translated():
    """Slot IDs in licensed_claims must be translated to Arabic in the CSV."""
    import importlib.util
    _script = REPO_ROOT / 'scripts' / 'demo_ayat_al_dayn.py'
    spec = importlib.util.spec_from_file_location('_demo_lc', _script)
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)

    stub = dict(_STUB_RESULT)
    stub['composite_verdict'] = dict(_STUB_RESULT['composite_verdict'])
    stub['composite_verdict']['licensed_claims'] = ['WORD_CLASS_SLOT', 'NUMBER_SLOT', 'GENDER_SLOT']

    csv_text = demo.format_csv([stub], lang='ar')
    assert 'خانة فئة الكلمة' in csv_text, "WORD_CLASS_SLOT must translate to خانة فئة الكلمة"
    assert 'خانة العدد' in csv_text, "NUMBER_SLOT must translate to خانة العدد"
    assert 'خانة الجنس' in csv_text, "GENDER_SLOT must translate to خانة الجنس"


# ─────────────────────────────────────────────────────────────────────────────
# 24. deferred_claims translates every slot ID
# ─────────────────────────────────────────────────────────────────────────────
def test_deferred_claims_slot_ids_translated():
    """Slot IDs in deferred_claims must be translated to Arabic in the CSV."""
    import importlib.util
    _script = REPO_ROOT / 'scripts' / 'demo_ayat_al_dayn.py'
    spec = importlib.util.spec_from_file_location('_demo_dc', _script)
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)

    stub = dict(_STUB_RESULT)
    stub['composite_verdict'] = dict(_STUB_RESULT['composite_verdict'])
    stub['composite_verdict']['deferred_claims'] = [
        'RADICAL_R1', 'PATTERN_CANDIDATE_SET', 'MASDAR_CANDIDATE_SET',
    ]

    csv_text = demo.format_csv([stub], lang='ar')
    assert 'الجذر ر١' in csv_text, "RADICAL_R1 must translate to الجذر ر١"
    assert 'مجموعة مرشحات الصيغة' in csv_text, \
        "PATTERN_CANDIDATE_SET must translate to مجموعة مرشحات الصيغة"
    assert 'مجموعة مرشحات المصدر' in csv_text, \
        "MASDAR_CANDIDATE_SET must translate to مجموعة مرشحات المصدر"


# ─────────────────────────────────────────────────────────────────────────────
# 25. Reason-code lists translate every member in Arabic CSV
# ─────────────────────────────────────────────────────────────────────────────
def test_reason_code_lists_translated():
    """taaqol_reason_codes and cra_reason_codes must be translated in Arabic CSV."""
    import importlib.util
    _script = REPO_ROOT / 'scripts' / 'demo_ayat_al_dayn.py'
    spec = importlib.util.spec_from_file_location('_demo_rc', _script)
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)

    stub = dict(_STUB_RESULT)
    stub['taaqol'] = dict(_STUB_RESULT['taaqol'])
    stub['taaqol']['reason_codes'] = ['GATE_REQUIRED', 'REQUIRED_SLOT_EMPTY']
    stub['root_analysis'] = dict(_STUB_RESULT['root_analysis'])
    stub['root_analysis']['cra_reason_codes'] = ['TRILATERAL_ROOT_ACCEPTED']

    csv_text = demo.format_csv([stub], lang='ar')

    # Taaqol reason codes translated
    assert 'يلزم اجتياز بوابة الانتقال' in csv_text, \
        "GATE_REQUIRED must translate to يلزم اجتياز بوابة الانتقال"
    assert 'خانة مطلوبة فارغة' in csv_text, \
        "REQUIRED_SLOT_EMPTY must translate to خانة مطلوبة فارغة"

    # CRA reason code translated
    assert 'قبول جذر ثلاثي' in csv_text, \
        "TRILATERAL_ROOT_ACCEPTED must translate to قبول جذر ثلاثي"


# ─────────────────────────────────────────────────────────────────────────────
# 26. GATE_REQUIRED literal not visible in Arabic client-facing CSV columns
# ─────────────────────────────────────────────────────────────────────────────
def test_gate_required_not_visible_in_arabic_csv():
    """The raw code 'GATE_REQUIRED' must not appear in taaqol_reason_codes cell."""
    import importlib.util, csv as _csv, io
    _script = REPO_ROOT / 'scripts' / 'demo_ayat_al_dayn.py'
    spec = importlib.util.spec_from_file_location('_demo_gr', _script)
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)

    stub = dict(_STUB_RESULT)
    stub['taaqol'] = dict(_STUB_RESULT['taaqol'])
    stub['taaqol']['reason_codes'] = ['GATE_REQUIRED']

    csv_text = demo.format_csv([stub], lang='ar')

    # Read the CSV and inspect the reason_codes cell by column position
    reader = _csv.DictReader(io.StringIO(csv_text))
    rows = list(reader)
    assert rows, "CSV must have at least one data row"

    # Find the Arabic column name for taaqol_reason_codes
    ar_col = None
    for col in rows[0].keys():
        if 'تعقل' in col and 'أسباب' in col:
            ar_col = col
            break
    assert ar_col is not None, \
        f"Could not find Arabic taaqol_reason_codes column; headers: {list(rows[0].keys())}"

    cell_value = rows[0][ar_col]
    assert 'GATE_REQUIRED' not in cell_value, \
        f"Raw code 'GATE_REQUIRED' must not appear in Arabic CSV cell, got: {cell_value!r}"
    assert 'يلزم اجتياز بوابة الانتقال' in cell_value, \
        f"Arabic translation must be present in cell, got: {cell_value!r}"


# ─────────────────────────────────────────────────────────────────────────────
# 27. English composite values remain byte-compatible (lang='en' is a no-op)
# ─────────────────────────────────────────────────────────────────────────────
def test_english_composite_values_byte_compatible():
    """With lang='en', translate_composite_value must return the value unchanged."""
    cases = [
        ('layer_name',   'RADICAL; PATTERN; BAB'),
        ('slot_id',      'WORD_CLASS_SLOT NUMBER_SLOT GENDER_SLOT'),
        ('reason_code',  'GATE_REQUIRED; REQUIRED_SLOT_EMPTY'),
        ('booleans',     'True'),
        ('booleans',     'False'),
    ]
    for category, value in cases:
        result = translate_composite_value(category, value, 'en')
        assert result == value, \
            f"English composite value must be unchanged: {result!r} != {value!r}"


# ─────────────────────────────────────────────────────────────────────────────
# 28. claim_key and evaluation_id are identical across English and Arabic CSV
# ─────────────────────────────────────────────────────────────────────────────
def test_canonical_ids_identical_across_languages():
    """claim_key and evaluation_id must be the same string in both CSV outputs."""
    import importlib.util, csv as _csv, io
    _script = REPO_ROOT / 'scripts' / 'demo_ayat_al_dayn.py'
    spec = importlib.util.spec_from_file_location('_demo_ids', _script)
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)

    csv_en = demo.format_csv([_STUB_RESULT], lang='en')
    csv_ar = demo.format_csv([_STUB_RESULT], lang='ar')

    rows_en = list(_csv.DictReader(io.StringIO(csv_en)))
    rows_ar = list(_csv.DictReader(io.StringIO(csv_ar)))
    assert rows_en and rows_ar, "Both CSVs must have data rows"

    # English CSV uses canonical field names directly
    assert rows_en[0]['claim_key'] == _STUB_RESULT['claim_key']
    assert rows_en[0]['evaluation_id'] == _STUB_RESULT['evaluation_id']

    # Arabic CSV maps claim_key → 'claim_key' (unchanged per YAML canonical rule)
    assert rows_ar[0]['claim_key'] == _STUB_RESULT['claim_key'], \
        "claim_key must be identical in Arabic CSV"
    assert rows_ar[0]['evaluation_id'] == _STUB_RESULT['evaluation_id'], \
        "evaluation_id must be identical in Arabic CSV"


# ─────────────────────────────────────────────────────────────────────────────
# 29. Arabic console runtime labels contain no untranslated English descriptors
# ─────────────────────────────────────────────────────────────────────────────
def test_arabic_runtime_labels_no_english_descriptors():
    """
    render_runtime_identity(lang='ar') must not contain English descriptive row labels.
    Technical names (Python, Hokom, Taaqol) are allowed; descriptive phrases are not.
    """
    import sys, importlib.util
    sys.path.insert(0, str(REPO_ROOT / 'src'))
    from hokom.demo.demo_renderer import render_runtime_identity

    output = render_runtime_identity(
        hokom_head='abc1234',
        taaqol_head='def56789abcdef12',
        taaqol_pin='def56789abcdef12',
        taaqol_pin_verified=True,
        taaqol_worktree_clean=True,
        results=[],
        use_color=False,
        lang='ar',
    )

    # These English descriptive labels must NOT appear when lang='ar'
    forbidden = [
        'Live evaluations',
        'Silent fallbacks',
        'Pin verified',
        'Taaqol worktree',
        'Taaqol mode',
        'Runtime Identity',
    ]
    for label in forbidden:
        assert label not in output, \
            f"English label {label!r} must not appear in Arabic runtime output"


# ─────────────────────────────────────────────────────────────────────────────
# 30. Unknown composite members emit UserWarning (never silently discarded)
# ─────────────────────────────────────────────────────────────────────────────
def test_unknown_composite_member_emits_warning():
    """translate_composite_value must warn for each unknown token, not silently drop it."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        result = translate_composite_value(
            'layer_name', 'RADICAL; UNKNOWN_LAYER_XYZZY; PATTERN', 'ar',
            separators=('; ', ';'),
        )

    # The unknown member must still appear in the output (never silently discarded)
    assert 'UNKNOWN_LAYER_XYZZY' in result, \
        f"Unknown member must be preserved in output, got: {result!r}"

    # At least one warning about the unknown member
    assert any('UNKNOWN_LAYER_XYZZY' in str(w.message) for w in caught), \
        "UserWarning must be emitted for unknown composite member"

    # Known members must still be translated
    assert 'الجذري' in result, "Known member RADICAL must still be translated"
    assert 'الصيغة' in result, "Known member PATTERN must still be translated"


# ─────────────────────────────────────────────────────────────────────────────
# 31. No emitted slot ID is missing from the YAML ar.enums.slot_id
# ─────────────────────────────────────────────────────────────────────────────
_EMITTED_SLOT_IDS = {
    # H11–H15 layer slots (from _H11_H15 set in demo script)
    'BAB_CANDIDATE_SET', 'MASDAR_CANDIDATE_SET', 'DERIVATIVE_CANDIDATE_SET',
    'NUMBER_SLOT', 'GENDER_SLOT', 'DEFINITENESS_SLOT', 'LEMMA_SLOT',
    'PARADIGM_SLOT', 'INFLECTIONAL_FAMILY_SLOT', 'DERIVATIONAL_FAMILY_SLOT',
    # Composite verdict slots
    'WORD_CLASS_SLOT',
    # SGA bundle slots
    'ORIGINAL_SURFACE', 'NORMALIZED_SURFACE', 'SEGMENT_HOST',
    'RADICAL_R1', 'RADICAL_R2', 'RADICAL_R3',
    'PATTERN_CANDIDATE_SET',
}

def test_no_emitted_slot_id_missing_from_yaml():
    """Every slot ID the pipeline can emit must have an Arabic translation in the YAML."""
    locale_ar = load_locale('ar')
    yaml_slot_ids = set(locale_ar.get('enums', {}).get('slot_id', {}).keys())
    missing = _EMITTED_SLOT_IDS - yaml_slot_ids
    assert not missing, \
        f"Slot IDs emitted by pipeline but missing from ar.enums.slot_id in YAML: {sorted(missing)}"


# ─────────────────────────────────────────────────────────────────────────────
# 32. No emitted reason code is missing from YAML (reason_code + cra_reason_code)
# ─────────────────────────────────────────────────────────────────────────────
_EMITTED_REASON_CODES = {
    'GATE_REQUIRED', 'REQUIRED_SLOT_EMPTY', 'SEGMENTATION_NO_LEXICAL_HOST',
    'ROOT_PATH_BLOCKED', 'OPEN_MORPHOLOGY', 'gamma:REQUIRED_SLOT_EMPTY',
}

_EMITTED_CRA_REASON_CODES = {
    'AUGMENTED_ROOT_ACCEPTED', 'FORM_IV_HOLLOW_IMPERFECT_ACCEPTED',
    'TRILATERAL_ROOT_ACCEPTED', 'WEAK_RADICAL_IN_AUGMENTED_ROOT:DEFER',
    'defer:root:defective_lam_unresolved', 'defer:root:non_standard_consonant_count',
    'defer:root:quadriliteral_beyond_scope', 'defer:root:two_consonant_form_unresolved',
}

def test_no_emitted_reason_code_missing_from_yaml():
    """Every reason code the pipeline can emit must have an Arabic translation in the YAML."""
    locale_ar = load_locale('ar')
    enums_ar = locale_ar.get('enums', {})

    yaml_reason = set(enums_ar.get('reason_code', {}).keys())
    missing_reason = _EMITTED_REASON_CODES - yaml_reason
    assert not missing_reason, \
        f"Reason codes missing from ar.enums.reason_code: {sorted(missing_reason)}"

    yaml_cra = set(enums_ar.get('cra_reason_code', {}).keys())
    missing_cra = _EMITTED_CRA_REASON_CODES - yaml_cra
    assert not missing_cra, \
        f"CRA reason codes missing from ar.enums.cra_reason_code: {sorted(missing_cra)}"
