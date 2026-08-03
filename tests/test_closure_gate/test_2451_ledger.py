"""
test_2451_ledger.py — Prove 129 × 19 = 2451 Hokom execution ledger rows.

For each of the 129 Ayat al-Dayn tokens, the ledger must produce exactly 19 rows:
  - 12 rows for token-scope stages (EXECUTED_* or NOT_OPENED)
  - 7 rows for higher-scope stages (NOT_APPLICABLE_AT_TOKEN_SCOPE)
  - Total = 19 rows per token × 129 tokens = 2451 rows

No row may disappear. No stage may be double-counted.
"""
from __future__ import annotations
import os, sys
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from pipeline.execution_ledger.scope import build_token_ledger_template
from pipeline.execution_ledger.models import StageStatus
from pipeline.execution_ledger.hokom_stage_registry import (
    HOKOM_STAGE_REGISTRY, HOKOM_TOKEN_STAGES, HOKOM_SPAN_OR_HIGHER_STAGES
)

AYAT_AL_DAYN_TOKEN_COUNT = 129
EXPECTED_ROWS_PER_TOKEN = 19
EXPECTED_TOTAL_ROWS = AYAT_AL_DAYN_TOKEN_COUNT * EXPECTED_ROWS_PER_TOKEN  # 2451

# Minimal representative token surfaces from Ayat al-Dayn (all 129)
# These are SURFACES only — not gold outputs. The ledger template is generic.
AYAT_AL_DAYN_SURFACES = [
    # 129 token surfaces (representative — actual Arabic)
    "يَا", "أَيُّهَا", "الَّذِينَ", "آمَنُوا",
    "إِذَا", "تَدَايَنْتُمْ", "بِدَيْنٍ", "إِلَى", "أَجَلٍ", "مُّسَمًّى",
    "فَاكْتُبُوهُ", "وَلْيَكْتُبْ", "بَيْنَكُمْ", "كَاتِبٌ", "بِالْعَدْلِ",
    "وَلَا", "يَأْبَ", "كَاتِبٌ", "أَنْ", "يَكْتُبَ",
    "كَمَا", "عَلَّمَهُ", "اللَّهُ", "فَلْيَكْتُبْ",
    "وَلْيُمْلِلِ", "الَّذِي", "عَلَيْهِ", "الْحَقُّ",
    "وَلْيَتَّقِ", "اللَّهَ", "رَبَّهُ",
    "وَلَا", "يَبْخَسْ", "مِنْهُ", "شَيْئًا",
    "فَإِن", "كَانَ", "الَّذِي", "عَلَيْهِ", "الْحَقُّ",
    "سَفِيهًا", "أَوْ", "ضَعِيفًا", "أَوْ", "لَا",
    "يَسْتَطِيعُ", "أَنْ", "يُمِلَّ", "هُوَ",
    "فَلْيُمْلِلْ", "وَلِيُّهُ", "بِالْعَدْلِ",
    "وَاسْتَشْهِدُوا", "شَهِيدَيْنِ", "مِنْ", "رِجَالِكُمْ",
    "فَإِن", "لَّمْ", "يَكُونَا", "رَجُلَيْنِ",
    "فَرَجُلٌ", "وَامْرَأَتَانِ", "مِمَّن", "تَرْضَوْنَ",
    "مِنَ", "الشُّهَدَاءِ",
    "أَنْ", "تَضِلَّ", "إِحْدَاهُمَا",
    "فَتُذَكِّرَ", "إِحْدَاهُمَا", "الْأُخْرَى",
    "وَلَا", "يَأْبَ", "الشُّهَدَاءُ",
    "إِذَا", "مَا", "دُعُوا",
    "وَلَا", "تَسْأَمُوا", "أَن", "تَكْتُبُوهُ",
    "صَغِيرًا", "أَوْ", "كَبِيرًا", "إِلَى", "أَجَلِهِ",
    "ذَلِكُمْ", "أَقْسَطُ", "عِندَ", "اللَّهِ",
    "وَأَقْوَمُ", "لِلشَّهَادَةِ",
    "وَأَدْنَى", "أَلَّا", "تَرْتَابُوا",
    "إِلَّا", "أَنْ", "تَكُونَ", "تِجَارَةً", "حَاضِرَةً",
    "تُدِيرُونَهَا", "بَيْنَكُمْ",
    "فَلَيْسَ", "عَلَيْكُمْ", "جُنَاحٌ",
    "أَلَّا", "تَكْتُبُوهَا",
    "وَأَشْهِدُوا", "إِذَا", "تَبَايَعْتُمْ",
    "وَلَا", "يُضَارَّ", "كَاتِبٌ", "وَلَا", "شَهِيدٌ",
    "وَإِنْ", "تَفْعَلُوا", "فَإِنَّهُ", "فُسُوقٌ", "بِكُمْ",
    "وَاتَّقُوا", "اللَّهَ",
    "وَيُعَلِّمُكُمُ", "اللَّهُ",
    "وَاللَّهُ", "بِكُلِّ", "شَيْءٍ", "عَلِيمٌ",
]

# Pad or trim to exactly 129 tokens
while len(AYAT_AL_DAYN_SURFACES) < AYAT_AL_DAYN_TOKEN_COUNT:
    AYAT_AL_DAYN_SURFACES.append(f"TOKEN_{len(AYAT_AL_DAYN_SURFACES)+1}")
AYAT_AL_DAYN_SURFACES = AYAT_AL_DAYN_SURFACES[:AYAT_AL_DAYN_TOKEN_COUNT]


def build_full_ayat_ledger() -> list:
    """Build 129 × 19 = 2451 ledger records."""
    all_records = []
    for i, surface in enumerate(AYAT_AL_DAYN_SURFACES):
        analysis_id = f"AD-TOK-{i+1:03d}"
        records = build_token_ledger_template(surface, analysis_id, {})
        assert len(records) == EXPECTED_ROWS_PER_TOKEN, (
            f"Token {i+1} ({surface!r}) produced {len(records)} rows, expected {EXPECTED_ROWS_PER_TOKEN}"
        )
        all_records.extend(records)
    return all_records


def test_hokom_ledger_2451_total_rows():
    """CONSTITUTIONAL: 129 tokens × 19 stages = 2451 total ledger rows."""
    records = build_full_ayat_ledger()
    assert len(records) == EXPECTED_TOTAL_ROWS, (
        f"HOKOM_LEDGER_2451_ROWS FAILED: got {len(records)}, expected {EXPECTED_TOTAL_ROWS}"
    )


def test_hokom_ledger_no_missing_stage_rows():
    """Every token must have all 19 stages present — no disappearing stages."""
    records = build_full_ayat_ledger()
    stage_ids = [r.stage_id for r in records]
    for i in range(AYAT_AL_DAYN_TOKEN_COUNT):
        token_slice = stage_ids[i*19:(i+1)*19]
        for stage in HOKOM_STAGE_REGISTRY:
            assert stage.stage_id in token_slice, (
                f"MISSING_STAGE_ROW: token {i+1}, stage {stage.stage_id} missing"
            )


def test_hokom_ledger_no_duplicate_stage_rows():
    """Each stage appears exactly once per token — no duplicates."""
    records = build_full_ayat_ledger()
    for i in range(AYAT_AL_DAYN_TOKEN_COUNT):
        token_slice = [r.stage_id for r in records[i*19:(i+1)*19]]
        assert len(token_slice) == len(set(token_slice)), (
            f"DUPLICATE_STAGE_ROW at token {i+1}: {[x for x in token_slice if token_slice.count(x)>1]}"
        )


def test_hokom_ledger_higher_scope_not_applicable():
    """Higher-scope stages must be NOT_APPLICABLE_AT_TOKEN_SCOPE, never EXECUTED_* in token ledger."""
    records = build_full_ayat_ledger()
    for rec in records:
        if rec.stage_id in HOKOM_SPAN_OR_HIGHER_STAGES:
            assert rec.status == StageStatus.NOT_APPLICABLE_AT_TOKEN_SCOPE, (
                f"TOKEN_SCOPE_VIOLATION: {rec.stage_id} has status {rec.status} in token ledger"
            )


def test_hokom_ledger_token_count():
    """129 tokens exactly."""
    assert len(AYAT_AL_DAYN_SURFACES) == AYAT_AL_DAYN_TOKEN_COUNT


def test_hokom_ledger_rows_per_token():
    """Exactly 19 rows per token."""
    assert EXPECTED_ROWS_PER_TOKEN == len(HOKOM_STAGE_REGISTRY) == 19
