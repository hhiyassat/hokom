# Architecture Inventory — HOKOM-HR2S-SEGMENTER-COMPARATIVE-AUDIT-01

**Date:** 2026-07-20
**Audit ID:** HOKOM-HR2S-SEGMENTER-COMPARATIVE-AUDIT-01
**Status:** READ-ONLY — no code was modified

---

## System Discovery Summary

### Mount Points Checked

| Path | Status |
|------|--------|
| `/sessions/lucid-gifted-planck/mnt/hokom/` | MOUNTED — Hokom repo |
| `/sessions/lucid-gifted-planck/mnt/fractal/` | NOT MOUNTED — path does not exist |
| `/sessions/lucid-gifted-planck/mnt/fractal/hr2s_morphology/` | NOT FOUND |
| `/sessions/lucid-gifted-planck/mnt/fractal/algebra/` | NOT FOUND |

---

## HOKOM Segmenter

**Location:** `/sessions/lucid-gifted-planck/mnt/hokom/pipeline/p0_segmentation/`

**Files:**
- `engine.py` — canonical entrypoint: `segment_token(request: SegmentationRequest) → SegmentBundle`
- `models.py` — SegmentationRequest, SegmentBundle, SegmentationVerdict, etc.
- `inventory.py` — PROCLITICS, ENCLITICS, PROTECTED_WHOLE_TOKENS, WHOLE_TOKEN_OPERATORS
- `rules.py` — `_extract_proclitics`, `_try_enclitic`, `_is_legal_host`
- `normalization.py` — `strip_diacritics`, `starts_with_definite_article`, etc.

**Entrypoint:**
```python
from pipeline.p0_segmentation.models import SegmentationRequest
from pipeline.p0_segmentation.engine import segment_token

req = SegmentationRequest(
    request_id='test:surface',
    original_surface='بِالْعَدْلِ',
    normalized_surface='بِالْعَدْلِ',
)
bundle = segment_token(req)
```

**Import success:** YES

**Python version:** 3.x (Linux workspace)

**Dependencies:** Zero external dependencies (no HR2S, no Taaqol at segmentation layer)

**Contract version:** 1

**Engine ID:** `HOKOM_CLITIC_SEGMENTER`

**Ownership marker:** `HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01`

---

## HR2S Morphology Engine

**Role:** ROOT ANALYSIS ENGINE — NOT a segmenter

**Critical finding:** HR2S is NOT a competing Arabic segmenter. It is the root analysis engine that runs AFTER Hokom segmentation. The architecture is sequential:

```
surface → [HOKOM SEGMENTER] → host → [HR2S ROOT ENGINE] → root radicals
```

**Adapter location:** `/sessions/lucid-gifted-planck/mnt/hokom/pipeline/integrations/hr2s_root_adapter.py`

**Package name:** `hr2s_morphology` (pip package, external)

**Installation status:** NOT INSTALLED — `ModuleNotFoundError: No module named 'hr2s'`

**Entrypoint (when available):**
```python
from hr2s import MorphologyEngine
engine = MorphologyEngine()
result = engine.analyze_surface(surface)  # returns root analysis, not segmentation
```

**Segmenter role:** NO — HR2S analyzes roots, not clitics

**Reference inventory:** `/sessions/lucid-gifted-planck/mnt/hokom/reports/segmentation/hr2s_reference_inventory.json` confirms: "HR2S segmenter not present in repo."

---

## Saleh / Qiyas

**Status:** NOT FOUND

**Search performed:**
- `find /sessions/lucid-gifted-planck/mnt/fractal/algebra -maxdepth 2 -type d -name 'Saleh*'` — path does not exist
- Searched for names: Saleh, saleh, Qiyas, qiyas, قياس in all mounted directories
- Result: No Saleh or Qiyas system found anywhere in the session

**Role:** NOT APPLICABLE (system absent)

**Adjudication method used instead:** Linguistic rules (classical Arabic morphology) applied via Qiyas framework (اصل/فرع/نسبة/شرط/سبب/مانع/أثر/بقايا) to each contested token.

---

## Token Corpus

**Source:** Ayat al-Dayn (Al-Baqarah 282) — canonical text, fully vocalized (with diacritics)

**Token count:** 129 tokens (whitespace-split)

**File:** `/sessions/lucid-gifted-planck/mnt/hokom/reports/segmenter_comparison/ayat_al_dayn_hokom.jsonl`

---

## Architectural Clarification

The audit prompt assumed HR2S has a competing Arabic clitic segmenter. This assumption is INCORRECT based on code examination:

1. The Hokom segmenter (`engine.py`) explicitly states: "No HR2S import. No Taaqol import. No root computation."
2. HR2S is invoked only via `HR2SRootAdapter.analyze()` AFTER segmentation is complete.
3. The boundary ceiling law: Hokom boundary decisions cannot be upgraded by HR2S.
4. The `hr2s_reference_inventory.md` explicitly confirms: "HR2S segmenter NOT found in the repository."

Therefore, this audit is a **self-audit of the Hokom segmenter** against linguistic ground truth, since no competing system exists.
