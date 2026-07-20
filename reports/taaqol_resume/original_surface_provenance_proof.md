# Original Surface Provenance Proof — HOKOM-TAAQOL-LIVE-INTEGRATION-01-RESUME

## Claim

`original_surface` is preserved as provenance and never silently lost,
even though it is forbidden as Center.scope.

## Evidence

### 1. Bundle claim_id encodes original_surface
```python
# claim_adapter.py
claim_id=f'hokom:{token_id or uuid.uuid4().hex[:12]}:{surface}'
#                                                    ^ surface = original_surface
```

### 2. Bridge TraceRef anchor uses claim_id (which contains original_surface)
```python
anchor = claim_id or f'hokom:{original_surface}'
trace_ref = TraceRef(anchor=anchor, kind='hokom_claim')
```

### 3. SlotGraph trace event records both original and center
```python
trace.append(HokomTaaqolTraceEvent(
    step='slot_graph_construction',
    output=f'SlotGraph(center={_morphological_center!r},'
           f'rank={slot_graph.rank},'
           f'original={_original_surface!r})',  # ← preserved
))
```

### 4. hokom() return dict exposes both
```python
'original':           word,         # original_surface
'segment_host':       segment_host, # morphological center
'taaqol_center_scope': ...,         # confirmed Center.scope
```

## Verification: Ayat al-Dayn run
- 129 tokens processed, 0 errors
- original_surface traceable for all tokens via claim_id
- Center.scope = segment_host for all split tokens
- Center.scope = None for بِكُمْ (clitic-only)
- No original_surface silently dropped
