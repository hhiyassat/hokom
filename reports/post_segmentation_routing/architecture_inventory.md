# Post-Segmentation Morphology Routing — Architecture Inventory
## HOKOM-POST-SEGMENTATION-MORPHOLOGY-ROUTING-OWNERSHIP-01

### Field Provenance Map

| Field | Producer | Consumer |
|-------|----------|----------|
| `input_surface` | hokom() top-level | All layers (read-only) |
| `segment_host` | `pipeline/p0_segmentation` via `segment_token()` | morphology gate, `_p5_host` computation, pre_root |
| `segment_proclitics` | p0_segmentation | Taaqol adapter |
| `segment_enclitics` | p0_segmentation | Taaqol adapter |
| `segment_clitic_only` | p0_segmentation | morphology gate |
| `segment_definite_article` | p0_segmentation (SegmentBundle.definite_article) | article provenance check |
| `morphology_surface` | `normalize(segment_host)` in hokom_pipeline.py | phonological pipeline (phones, licensing, slots) |
| `morphology_blocked` | True when segment_host is None | pre_root gate, word_class gate |
| `mabni` | `mabni_layer.process_mabni()` | pre_root gate, root path |
| `attachment` | `mabniyat_attachment.recognize_token()` (P5.2) | `_p5_host` routing, pre_root gate |
| `attachment.host_route` | mabniyat_attachment | routing decision in hokom_pipeline |
| `pre_root` | `pipeline.pre_root.pre_root_decision.assess_pre_root()` | root candidate |
| `root_candidate` | `pipeline.p3_candidate` via `resolve_root_pipeline()` | phase4a, word_class |
| `root_candidate.host_surface` | p3_candidate from `_resolved_host` | root admission |
| `root_candidate.canonical_root` | p3_candidate | phase4a (wazn, bab, masdar) |

### Routing Decision Logic (post-fix)

```
mabni = process_mabni()                          # P5 lookup
attachment = recognize_token() if MabniOpen      # P5.2 mabniyat detection

# Pre-Root gate (hokom_pipeline.py ~line 173)
pre_root = None
if NOT morphology_blocked AND isinstance(mabni, MabniOpen):
    _seg_v   = attachment.segmentation_verdict
    _route_v = attachment.host_route
    
    if NOT_SEGMENTED and MABNI_BOUNDARY → pre_root = None
    elif _route_v == OPERATOR_BOUNDARY  → pre_root = None  # [FIX 1]
    else                                → pre_root = assess_pre_root(_p5_host)

# Root opens only when pre_root.root_path_directive == 'OPEN'
```

### Violations Found (Pre-Fix)

| Token | Type | Root Directive | Cause |
|-------|------|---------------|-------|
| فَلَيْسَ | ROOT_ACCEPT_AFTER_OP_BOUNDARY_COMPOSITE | ACCEPT (ل-ي-س) | attachment.host_route=OPERATOR_BOUNDARY not guarded before pre_root |
| بِكُمْ | ROOT_AFTER_MORPHOLOGY_BLOCKED | DEFER | morphology_blocked not checked before pre_root block |

### Fixes Applied (hokom_pipeline.py)

**Fix 1** — OPERATOR_BOUNDARY monotonic guard:
- Added `elif _route_v == 'OPERATOR_BOUNDARY': pre_root = None`
- Effect: tokens like فَلَيْسَ (فَ+لَيْسَ where لَيْسَ is an operator) no longer open root analysis

**Fix 2** — Morphology blocked gate:
- Changed `if isinstance(mabni, MabniOpen):` → `if not morphology_blocked and isinstance(mabni, MabniOpen):`
- Effect: clitic-only tokens (بِكُمْ, بِالْعَدْلِ) with morphology_blocked=True no longer call assess_pre_root

### Confirmed Working (No Violation)

- OPERATOR_BOUNDARY standalone (أَيُّهَا, إِذَا, أَوْ, لَا, إِلَّا, مَا): mabni=MabniBoundary, root_candidate=None ✓
- MABNI_BOUNDARY standalone (هُوَ, الَّذِي, الَّذِينَ): attach_route=MABNI_BOUNDARY, pre_root=None, root_candidate=None ✓
- Article stripping (الْحَقُّ → حَقُّ): segment_host='حَقُّ', root_candidate.host_surface derived from morphology_surface ✓
- Surface provenance (عَلَّمَهُ, رَبَّهُ): root_candidate.host_surface = morphology_surface (not input_surface) ✓

### Actual Field Names in hokom() Result

These are the REAL fields (the task spec used assumed names like `p5_route`, `root_host`, `root_stage` which do NOT exist):

```python
r['mabni']                     # MabniBoundary | MabniOpen | MabniBlocked
r['attachment']                # TokenAnalysis object (P5.2 mabniyat)
r['attachment'].host_route     # 'OPERATOR_BOUNDARY' | 'MABNI_BOUNDARY' | 'OPEN_TO_HR2S' | 'EMPTY'
r['attachment'].segmentation_verdict  # 'SEGMENTED' | 'NOT_SEGMENTED' | 'AMBIGUOUS'
r['pre_root']                  # PreRootDecision | None
r['pre_root'].root_path_directive  # 'OPEN' | 'DEFER' | 'BLOCK'
r['root_candidate']            # RootCandidate | None
r['root_candidate'].directive  # 'ACCEPT' | 'DEFER' | 'BLOCK'
r['root_candidate'].canonical_root  # tuple[str,...] | None
r['root_candidate'].host_surface    # str
r['segment_host']              # str | None
r['morphology_surface']        # str | None (= normalize(segment_host))
r['morphology_blocked']        # bool
```

### Post-Fix Verification

Ayat al-Dayn (129 tokens):
- POST_SEGMENTATION_ROUTING_VIOLATIONS: 0
- ROOT_AFTER_CLOSED_BOUNDARY: 0
- SURFACE_PROVENANCE_VIOLATIONS: 0
- ARTICLE_REATTACHMENT_VIOLATIONS: 0
