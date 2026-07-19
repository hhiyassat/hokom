#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/scripts/test_analyze_text_demo.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
اختبارات runner الأساسية — HOKOM-TEXT-ROOT-DEMO-RUNNER

R1  text input
R2  file input
R3  punctuation preservation
R4  JSONL validity
R5  stop-at-root (لا وزن ولا باب في المخرج)
R6  deterministic output
R7  no external engine invocation (source_engine assertion for HOKOM records)
"""

import importlib.util
import io
import json
import pathlib
import pytest

# استيراد مباشر من المسار المطلق — يتجنب مشاكل package detection في pytest
_DEMO_PATH = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / 'scripts' / 'analyze_text_demo.py'
)
_spec = importlib.util.spec_from_file_location('analyze_text_demo', str(_DEMO_PATH))
_mod  = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

run_demo           = _mod.run_demo
tokenize_with_lines = _mod.tokenize_with_lines


# ══════════════════════════════════════════════════════════════════════════════
# R1 — text input
# ══════════════════════════════════════════════════════════════════════════════

class TestTextInput:

    def test_simple_verb_produces_records(self):
        buf = io.StringIO()
        stats = run_demo('كَتَبَ', fmt='jsonl', out=buf)
        assert stats['TOTAL_TOKENS'] >= 1

    def test_summary_keys_present(self):
        buf = io.StringIO()
        stats = run_demo('ضَرَبَ قَالَ', fmt='jsonl', out=buf)
        for key in ('TOTAL_TOKENS', 'ROOT_OPENED', 'ROOT_ACCEPTED',
                    'ROOT_DEFERRED', 'UNHANDLED_ERRORS'):
            assert key in stats, f"missing stats key: {key}"

    def test_unhandled_errors_zero(self):
        buf = io.StringIO()
        stats = run_demo(
            'هَلْ كَتَبَ الطَّالِبُ الدَّرْسَ؟',
            fmt='jsonl', out=buf,
        )
        assert stats['UNHANDLED_ERRORS'] == 0


# ══════════════════════════════════════════════════════════════════════════════
# R2 — file input (via tokenize_with_lines)
# ══════════════════════════════════════════════════════════════════════════════

class TestFileInput:

    def test_multiline_file(self):
        text = 'كَتَبَ الطَّالِبُ\nقَرَأَ الدَّرْسَ'
        tokens = tokenize_with_lines(text)
        word_tokens = [t for t in tokens if t['kind'] in ('word', 'clitic')]
        # line numbers must be set
        lines_seen = {t['line_number'] for t in word_tokens}
        assert 1 in lines_seen
        assert 2 in lines_seen

    def test_file_via_tempfile(self, tmp_path):
        p = tmp_path / 'input.txt'
        p.write_text('كَتَبَ\nقَرَأَ', encoding='utf-8')
        text = p.read_text(encoding='utf-8')
        buf  = io.StringIO()
        stats = run_demo(text, fmt='jsonl', out=buf)
        assert stats['TOTAL_TOKENS'] >= 2
        assert stats['UNHANDLED_ERRORS'] == 0

    def test_token_numbers_sequential(self):
        tokens = tokenize_with_lines('ضَرَبَ كَتَبَ قَرَأَ')
        nums = [t['token_number'] for t in tokens]
        assert nums == list(range(1, len(nums) + 1))


# ══════════════════════════════════════════════════════════════════════════════
# R3 — punctuation preservation
# ══════════════════════════════════════════════════════════════════════════════

class TestPunctuationPreservation:

    def test_punct_not_in_word_tokens(self):
        text = 'كَتَبَ، قَرَأَ؟ وَعَدَ.'
        all_tok  = tokenize_with_lines(text)
        word_tok = [t for t in all_tok if t['kind'] in ('word', 'clitic')]
        punct_tok = [t for t in all_tok if t['kind'] == 'punct']
        # punct tokens should exist (،؟.)
        assert len(punct_tok) > 0, "no punct tokens found"
        # word tokens must not contain pure punctuation surfaces
        for t in word_tok:
            assert t['surface'] not in ('،', '؟', '.', '!', ':'), (
                f"punct surface {t['surface']!r} in word tokens"
            )

    def test_diacritics_preserved(self):
        text = 'كَتَبَ'
        tokens = tokenize_with_lines(text)
        word_t  = [t for t in tokens if t['kind'] in ('word', 'clitic')]
        surfaces = [t['surface'] for t in word_t]
        # تشكيل يُحفظ
        combined = ''.join(surfaces)
        assert 'كَ' in combined or 'كَتَبَ' in combined or 'تَبَ' in combined, (
            f"diacritics lost: {surfaces}"
        )

    def test_punct_counted_in_stats(self):
        buf = io.StringIO()
        stats = run_demo('كَتَبَ، قَرَأَ.', fmt='jsonl', out=buf)
        assert stats['PUNCT_SKIPPED'] >= 2


# ══════════════════════════════════════════════════════════════════════════════
# R4 — JSONL validity
# ══════════════════════════════════════════════════════════════════════════════

class TestJSONLValidity:

    def _parse_jsonl(self, text: str, **kwargs) -> list[dict]:
        buf = io.StringIO()
        run_demo(text, fmt='jsonl', out=buf, **kwargs)
        buf.seek(0)
        records = []
        for line in buf:
            line = line.strip()
            if line:
                records.append(json.loads(line))
        return records

    def test_every_line_valid_json(self):
        records = self._parse_jsonl('كَتَبَ قَالَ مِنْ')
        assert len(records) >= 1

    def test_last_record_is_summary(self):
        records = self._parse_jsonl('كَتَبَ قَالَ')
        assert records[-1].get('record_type') == 'SUMMARY'

    def test_token_records_have_required_fields(self):
        required = [
            'line_number', 'token_number', 'input_surface',
            'normalized_surface', 'analysis_surface',    # Fix #4: both fields required
            'P4_structural_verdict',
            'P5_lexical_verdict', 'P5_root_gate',
        ]
        records = self._parse_jsonl('كَتَبَ الطَّالِبُ')
        token_recs = [r for r in records if r.get('record_type') != 'SUMMARY']
        for rec in token_recs:
            for field in required:
                assert field in rec, (
                    f"token {rec.get('input_surface')!r}: missing field {field!r}"
                )

    def test_summary_has_all_stat_keys(self):
        records = self._parse_jsonl('كَتَبَ قَرَأَ')
        summary = records[-1]
        for key in ('TOTAL_TOKENS', 'ROOT_ACCEPTED', 'ROOT_DEFERRED',
                    'ROOT_BLOCKED', 'UNHANDLED_ERRORS'):
            assert key in summary


# ══════════════════════════════════════════════════════════════════════════════
# R5 — stop-at-root (لا وزن ولا باب ولا مصدر في السجلات)
# ══════════════════════════════════════════════════════════════════════════════

class TestStopAtRoot:

    def _token_records(self, text: str) -> list[dict]:
        buf = io.StringIO()
        run_demo(text, fmt='jsonl', out=buf)
        buf.seek(0)
        return [json.loads(l) for l in buf if l.strip()
                and json.loads(l).get('record_type') != 'SUMMARY']

    def test_no_wazn_field(self):
        for rec in self._token_records('كَتَبَ مَدَّ'):
            assert 'wazn' not in rec, f"wazn leaked into record: {rec.get('input_surface')}"
            assert 'final_wazn' not in rec

    def test_no_bab_field(self):
        for rec in self._token_records('كَتَبَ'):
            assert 'bab' not in rec
            assert 'phase4b' not in rec

    def test_no_masdar_field(self):
        for rec in self._token_records('كَتَبَ'):
            assert 'masdar' not in rec
            assert 'phase4c' not in rec

    def test_no_mushtaqat_field(self):
        for rec in self._token_records('كَتَبَ'):
            assert 'mushtaqat' not in rec
            assert 'phase4d' not in rec

    def test_no_inflection_field(self):
        for rec in self._token_records('كَتَبَ'):
            assert 'inflectional_form' not in rec
            assert 'phase5' not in rec


# ══════════════════════════════════════════════════════════════════════════════
# R6 — deterministic output
# ══════════════════════════════════════════════════════════════════════════════

class TestDeterministicOutput:

    def _jsonl_output(self, text: str) -> str:
        buf = io.StringIO()
        run_demo(text, fmt='jsonl', out=buf)
        return buf.getvalue()

    @pytest.mark.parametrize("text", [
        'كَتَبَ الطَّالِبُ',
        'قَالَ رَمَى وَقَى',
        'هَلْ مِنْ ضَرَبَ',
    ])
    def test_same_output_twice(self, text):
        out1 = self._jsonl_output(text)
        out2 = self._jsonl_output(text)
        assert out1 == out2, f"non-deterministic output for {text!r}"

    def test_max_tokens_limits_output(self):
        buf = io.StringIO()
        stats = run_demo('كَتَبَ قَرَأَ ضَرَبَ نَصَرَ', fmt='jsonl',
                         max_tokens=2, out=buf)
        assert stats['TOTAL_TOKENS'] == 2


# ══════════════════════════════════════════════════════════════════════════════
# R7 — source_engine is canonical for HOKOM_ROOT_ENGINE records
# ══════════════════════════════════════════════════════════════════════════════

class TestNoExternalEngine:

    # HOKOM_AUGMENTED_ENGINE is also canonical Hokom; demo maps it to HOKOM_ROOT_ENGINE in output
    CANONICAL = frozenset({'HOKOM_ROOT_ENGINE', 'HOKOM_AUGMENTED_ENGINE', 'HOKOM_BOUNDARY'})

    def _token_records(self, text: str) -> list[dict]:
        buf = io.StringIO()
        run_demo(text, fmt='jsonl', out=buf)
        buf.seek(0)
        return [json.loads(l) for l in buf if l.strip()
                and json.loads(l).get('record_type') != 'SUMMARY']

    def _se(self, rec: dict) -> str | None:
        """source_engine is stored as root_source_engine in JSONL records."""
        return rec.get('root_source_engine') or rec.get('source_engine')

    def test_closed_gate_uses_hokom_boundary(self):
        """المبنيات المغلقة يجب أن تُنتج HOKOM_BOUNDARY أو لا source_engine."""
        records = self._token_records('هَلْ مِنْ لَمْ')
        for rec in records:
            gate = rec.get('P5_root_gate')
            se   = self._se(rec)
            if gate == 'CLOSED':
                assert se in (None, 'HOKOM_BOUNDARY'), (
                    f"{rec.get('input_surface')!r}: CLOSED gate but source_engine={se!r}"
                )

    def test_accepted_roots_use_hokom_engine(self):
        """الجذور المقبولة يجب أن تأتي من HOKOM_ROOT_ENGINE."""
        records = self._token_records('كَتَبَ ضَرَبَ نَصَرَ قَرَأَ مَدَّ')
        accepted = [r for r in records if r.get('root_directive') == 'ACCEPT']
        assert len(accepted) >= 1, "no ACCEPT records found in test corpus"
        for rec in accepted:
            se = self._se(rec)
            assert se in ('HOKOM_ROOT_ENGINE', None), (
                f"{rec.get('input_surface')!r}: ACCEPT but source_engine={se!r}"
            )
            # If present, must be canonical
            if se is not None:
                assert se == 'HOKOM_ROOT_ENGINE', (
                    f"{rec.get('input_surface')!r}: ACCEPT but source_engine={se!r}"
                )
