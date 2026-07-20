# Taaqol Resume Requirements — Segmentation Bridge Handoff

**From: HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01**
**To: HOKOM-TAAQOL-LIVE-INTEGRATION-01 resume phase**
**Status: Taaqol bridge intentionally unchanged (per mandate)**

---

## What the Segmentation Phase Produces

Every `hokom()` call now populates:

```python
result['segment_bundle']     # SegmentBundle — full segmentation output
result['segment_host']       # str — lexical host (None-safe: falls back to normalized_surface)
result['segment_proclitics'] # tuple[str] — proclitic surfaces
result['segment_enclitics']  # tuple[str] — enclitic surfaces
result['segment_clitic_only'] # bool — True when host is None (proclitic+enclitic only)
```

---

## Required Changes in Resume Phase

### 1. bridge.py — Use segment_host for lexical scope

Current (DO NOT CHANGE YET):
```python
# bridge.py uses original_surface or normalized_surface as the CENTER scope
claim = ... bundle.original_surface ...
```

Resume change required:
```python
# Use segment_host (the post-segmentation lexical host) as the CENTER scope
# INVARIANT: ORIGINAL_SURFACE_AS_CENTER_SCOPE = FORBIDDEN
segment_bundle = hokom_result.get('segment_bundle')
lexical_scope = (
    segment_bundle.host
    if segment_bundle and segment_bundle.host
    else hokom_result['normalized_surface']
)
```

### 2. claim_adapter.py — Add proclitic/enclitic slots

Resume change required in `bundle_from_hokom_result`:
```python
segment_bundle = hokom_result.get('segment_bundle')
if segment_bundle:
    # Add proclitic slots
    for p in segment_bundle.proclitics:
        add_slot(SlotType.PROCLITIC, p)
    # Add definite article slot
    if segment_bundle.definite_article:
        add_slot(SlotType.DEFINITE_ARTICLE, segment_bundle.definite_article)
    # Add enclitic slots
    for e in segment_bundle.enclitics:
        add_slot(SlotType.ENCLITIC, e)
```

### 3. Files to modify in resume phase

| File | Change |
|------|--------|
| `pipeline/taaqol_integration/live/bridge.py` | Use `segment_host` as lexical scope |
| `pipeline/taaqol_integration/claim_adapter.py` | Add proclitic/enclitic slot wiring |

### 4. Files that MUST NOT be changed in resume phase

| File | Reason |
|------|--------|
| `pipeline/p0_segmentation/` (all) | Already closed by this mandate |
| `hokom_pipeline.py` segmentation block | Already wired |

---

## Invariant

```
ORIGINAL_SURFACE_AS_CENTER_SCOPE = FORBIDDEN

The bridge must NEVER use:
- bundle.original_surface as the lexical scope
- bundle.normalized_surface as the lexical scope  
- The full token (e.g., وَلْيَكْتُبْ) when segment_host is available

It MUST use:
- segment_bundle.host (the post-segmentation lexical host)
- Fallback: normalized_surface (only when segment_bundle is None)
```
