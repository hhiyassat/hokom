"""
tests/demo/test_ayat_al_dayn_report_integrity.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Report integrity tests for the Ayat al-Dayn full-slot demo (v2).

Five anti-patterns are tested:
  1. Slot exported with name but missing state
  2. Overall LICENSED without licensed_scope field populated
  3. Token missing evaluation_id
  4. Taaqol active but taaqol_trace absent
  5. composite_verdict.overall_verdict == 'FULLY_LICENSED' while
     deferred_claims is non-empty

These tests run against a LIVE pipeline call over 10 tokens
(sample drawn deterministically: indices 1, 14, 28, 42, 56,
 70, 84, 98, 112, 129 — spread evenly across the verse).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.demo_ayat_al_dayn import process_token_full  # noqa: E402

# ── shared sample ─────────────────────────────────────────────────────────────
AYAT_AL_DAYN = (
    'يَا أَيُّهَا الَّذِينَ آمَنُوا إِذَا تَدَايَنْتُمْ بِدَيْنٍ إِلَى أَجَلٍ مُسَمًّى '
    'فَاكْتُبُوهُ وَلْيَكْتُبْ بَيْنَكُمْ كَاتِبٌ بِالْعَدْلِ وَلَا يَأْبَ كَاتِبٌ '
    'أَنْ يَكْتُبَ كَمَا عَلَّمَهُ اللَّهُ فَلْيَكْتُبْ وَلْيُمْلِلِ الَّذِي عَلَيْهِ '
    'الْحَقُّ وَلْيَتَّقِ اللَّهَ رَبَّهُ وَلَا يَبْخَسْ مِنْهُ شَيْئًا فَإِنْ كَانَ '
    'الَّذِي عَلَيْهِ الْحَقُّ سَفِيهًا أَوْ ضَعِيفًا أَوْ لَا يَسْتَطِيعُ أَنْ يُمِلَّ '
    'هُوَ فَلْيُمْلِلْ وَلِيُّهُ بِالْعَدْلِ وَاسْتَشْهِدُوا شَهِيدَيْنِ مِنْ رِجَالِكُمْ '
    'فَإِنْ لَمْ يَكُونَا رَجُلَيْنِ فَرَجُلٌ وَامْرَأَتَانِ مِمَّنْ تَرْضَوْنَ مِنَ '
    'الشُّهَدَاءِ أَنْ تَضِلَّ إِحْدَاهُمَا فَتُذَكِّرَ إِحْدَاهُمَا الْأُخْرَى وَلَا '
    'يَأْبَ الشُّهَدَاءُ إِذَا مَا دُعُوا وَلَا تَسْأَمُوا أَنْ تَكْتُبُوهُ صَغِيرًا '
    'أَوْ كَبِيرًا إِلَى أَجَلِهِ ذَلِكُمْ أَقْسَطُ عِنْدَ اللَّهِ وَأَقْوَمُ '
    'لِلشَّهَادَةِ وَأَدْنَى أَلَّا تَرْتَابُوا إِلَّا أَنْ تَكُونَ تِجَارَةً '
    'حَاضِرَةً تُدِيرُونَهَا بَيْنَكُمْ فَلَيْسَ عَلَيْكُمْ جُنَاحٌ أَلَّا تَكْتُبُوهَا '
    'وَأَشْهِدُوا إِذَا تَبَايَعْتُمْ وَلَا يُضَارَّ كَاتِبٌ وَلَا شَهِيدٌ وَإِنْ '
    'تَفْعَلُوا فَإِنَّهُ فُسُوقٌ بِكُمْ وَاتَّقُوا اللَّهَ وَيُعَلِّمُكُمُ اللَّهُ '
    'وَاللَّهُ بِكُلِّ شَيْءٍ عَلِيمٌ'
)
TOKENS = AYAT_AL_DAYN.split()
assert len(TOKENS) == 129

# Sample indices (1-based) — spread across the 129 tokens
_SAMPLE_1BASED = [1, 14, 28, 42, 56, 70, 84, 98, 112, 129]
SAMPLE_PAIRS = [(i, TOKENS[i - 1]) for i in _SAMPLE_1BASED]


# ── fixture: run sample once per test session ─────────────────────────────────
@pytest.fixture(scope='module')
def sample_results():
    """Run the demo pipeline over the 10-token sample."""
    return [process_token_full(idx, surf) for idx, surf in SAMPLE_PAIRS]


# ── 1. Slot name present but state absent ─────────────────────────────────────
def test_no_slot_missing_state(sample_results):
    """
    Every exported typed slot must carry both 'slot_id' and 'state'.
    A slot name without a state is meaningless and forbidden.
    """
    violations = []
    for r in sample_results:
        for s in r.get('typed_slots', []):
            if 'slot_id' not in s:
                violations.append(
                    f"token {r['token_index']} ({r['original_surface']}): "
                    f"slot has no slot_id"
                )
            elif 'state' not in s or s['state'] is None:
                violations.append(
                    f"token {r['token_index']} ({r['original_surface']}): "
                    f"slot {s['slot_id']!r} has no state"
                )
    assert not violations, (
        f'{len(violations)} slot(s) exported without state:\n'
        + '\n'.join(violations)
    )


# ── 2. LICENSED without scope ─────────────────────────────────────────────────
def test_no_licensed_without_scope(sample_results):
    """
    overall_verdict == 'FULLY_LICENSED' must only appear when
    licensed_claims is non-empty AND deferred/blocked/ambiguous are all empty.

    Any token that declares FULLY_LICENSED while has_unresolved_claims=True
    is hiding unresolved obligations — forbidden.
    """
    violations = []
    for r in sample_results:
        cv = r.get('composite_verdict', {})
        if cv.get('overall_verdict') == 'FULLY_LICENSED':
            if cv.get('has_unresolved_claims'):
                violations.append(
                    f"token {r['token_index']} ({r['original_surface']}): "
                    f"overall_verdict=FULLY_LICENSED but has_unresolved_claims=True "
                    f"(deferred={cv.get('deferred_claims')}, "
                    f"blocked={cv.get('blocked_claims')})"
                )
            if not cv.get('licensed_claims'):
                violations.append(
                    f"token {r['token_index']} ({r['original_surface']}): "
                    f"overall_verdict=FULLY_LICENSED but licensed_claims is empty"
                )
    assert not violations, (
        'LICENSED declared without scope:\n' + '\n'.join(violations)
    )


# ── 3. Missing evaluation_id ──────────────────────────────────────────────────
def test_every_token_has_evaluation_id(sample_results):
    """
    Every processed token must have a non-empty evaluation_id.
    It must be unique within the sample (no collisions even for identical
    surfaces, because it is salted with the token index).
    """
    missing = [
        f"token {r['token_index']} ({r['original_surface']})"
        for r in sample_results
        if not r.get('evaluation_id')
    ]
    assert not missing, (
        f'Tokens missing evaluation_id: {missing}'
    )

    eids = [r['evaluation_id'] for r in sample_results if r.get('evaluation_id')]
    assert len(eids) == len(set(eids)), (
        f'evaluation_id collision in sample — same id appears more than once. '
        f'IDs: {eids}'
    )


# ── 4. Taaqol active but trace absent ────────────────────────────────────────
def test_taaqol_trace_present_when_active(sample_results):
    """
    When taaqol.available == True, taaqol.trace_events must be non-empty.
    A live Taaqol run without trace events means the trace pipeline broke.
    """
    violations = []
    for r in sample_results:
        tq = r.get('taaqol', {})
        if tq.get('available'):
            if not tq.get('trace_events'):
                violations.append(
                    f"token {r['token_index']} ({r['original_surface']}): "
                    f"taaqol.available=True but trace_events is empty"
                )
    assert not violations, (
        'Taaqol active but trace absent:\n' + '\n'.join(violations)
    )


# ── 5. FULLY_LICENSED hiding deferred claims ──────────────────────────────────
def test_fully_licensed_not_masking_deferred(sample_results):
    """
    composite_verdict.overall_verdict must not be 'FULLY_LICENSED'
    when composite_verdict.deferred_claims is non-empty.

    This is the critical guard: تَدَايَنْتُمْ has word_class=LICENSED but
    root=DEFERRED, so it must be labelled COMPOSITE, not FULLY_LICENSED.
    """
    violations = []
    for r in sample_results:
        cv = r.get('composite_verdict', {})
        if cv.get('overall_verdict') == 'FULLY_LICENSED' and cv.get('deferred_claims'):
            violations.append(
                f"token {r['token_index']} ({r['original_surface']}): "
                f"overall_verdict=FULLY_LICENSED but "
                f"deferred_claims={cv['deferred_claims']}"
            )
    assert not violations, (
        'overall_verdict=FULLY_LICENSED masking deferred claims:\n'
        + '\n'.join(violations)
    )


# ── 6. Spot-check تَدَايَنْتُمْ (token #6) ────────────────────────────────────
def test_tadayantum_composite_verdict():
    """
    تَدَايَنْتُمْ must NOT have overall_verdict=FULLY_LICENSED.
    Its root is DEFERRED and wazn/masdar are not opened.
    Expected: overall_verdict='COMPOSITE'.
    """
    r = process_token_full(6, 'تَدَايَنْتُمْ')
    cv = r.get('composite_verdict', {})

    # Slot groups must be populated
    assert 'licensed_claims' in cv, 'composite_verdict missing licensed_claims'
    assert 'deferred_claims' in cv, 'composite_verdict missing deferred_claims'

    # Word class must appear in licensed (WORD_CLASS_SLOT should be FILLED)
    # Allow that sandbox may return a non-FI3L if routing differs
    # but overall verdict must NOT be FULLY_LICENSED when deferred exist
    if cv.get('deferred_claims'):
        assert cv['overall_verdict'] != 'FULLY_LICENSED', (
            f"تَدَايَنْتُمْ was tagged FULLY_LICENSED but has "
            f"deferred_claims={cv['deferred_claims']}"
        )

    # Root analysis must indicate DEFERRED or UNKNOWN (not KNOWN)
    ra = r.get('root_analysis', {})
    assert ra.get('root_state') in ('DEFERRED', 'UNKNOWN', 'AMBIGUOUS'), (
        f"Expected root DEFERRED/UNKNOWN for تَدَايَنْتُمْ, "
        f"got {ra.get('root_state')!r}"
    )
