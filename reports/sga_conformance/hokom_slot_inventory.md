# Hokom Slot Inventory by Stage
HEAD: ce55f7b

## P0: Unicode / Segmentation

**Module**: `pipeline/p0_unicode/glyph_classification.py`, `pipeline/p0_segmentation/`
**Input**: raw token string
**Output**: SegmentBundle (host, proclitics, enclitics, definite_article, clitic_only)
**Slot type**: typed dataclass (SegmentBundle) — partially SGA-aligned
**SGA status**: ALIGNED for type; UNTYPED_SLOT for sub-fields (host, proclitics are plain strings, not Slot objects)
**Trace**: none
**Residuals**: morphology_block_reason (plain string)

## P1: Atomic Structure / Slot Engineering

**Module**: `pipeline/p1_atomic_structure/cell_builder.py`, `pipeline/p1_atomic_structure/slot_engineering.py`
**Input**: phones (list of Phone objects)
**Output**: slots (list of plain dicts: `{surface, pattern, gate, status, violations}`)
**Slot type**: UNTYPED — plain dicts
**SGA sorts**: None declared. Patterns (CV, CVV, CVC, CVVC, CVCC, CVVCC) are string labels, not SGA sort enums.
**Transition logic**: `SLOT_TRANS` dict lookup — no gate, no cause, no condition, no obstacle, no evidence, no defeater
**Verdict**: `word_gate()` returns ACCEPT/DEFER/BLOCK — no EvidenceContract attached to verdict

**SGA Violations**:
- UNTYPED_SLOT: all phonological slots
- UNLICENSED_TRANSITION: all SLOT_TRANS transitions
- EVIDENCELESS_ACCEPT: word_gate ACCEPT on pattern membership alone

**Special slots**:
- HAMZAT_AL_WASL: `{'surface': 'ا', 'pattern': 'HAMZAT_AL_WASL', 'gate': ''}` — gate='' means invisible to word_gate; RESIDUAL_LOSS
- ALEF_FARQA: `{'surface': 'ا', 'pattern': 'ALEF_FARQA', 'gate': ''}` — same issue

## P2: Augmented / Projection

**Module**: `pipeline/p2_augmented/augmented_host_refinement.py`, `pipeline/p2_projection/root_projection.py`
**Input**: refined_host, morphology_path, evidence_ids, trace_ids
**Output**: AugmentedRootAnalysis or RootProjection (typed dataclasses)
**Slot type**: typed dataclasses — partially SGA-aligned
**SGA status**: UNTYPED_SLOT for evidence_ids/trace_ids (plain tuples of strings)

## P3: Root Candidate

**Module**: `pipeline/p3_candidate/root_candidate.py`, `pipeline/p3_pre_root/canonical_radical_accounting.py`
**Input**: RootProjection or CRA result
**Output**: RootCandidate (typed, has canonical_root, directive, evidence_ids, trace_ids)
**Slot type**: typed dataclass
**Radical slots**: RADICAL_SLOT_R1/R2/R3 implicit in canonical_root tuple — NOT declared as SGA Slot objects
**SGA status**: UNTYPED_SLOT for radical slots; evidence_ids are plain strings (UNTYPED evidence)
**Residuals**: residual_codes (plain tuple of strings) — UNTYPED

**SGA Violations**:
- UNTYPED_SLOT: canonical_root is a tuple of Arabic character strings, not typed Slot objects
- RESIDUAL_LOSS: residual_codes are plain strings not Residual objects

## P4: Pattern / Bab / Masdar / Mushtaqat

**Module**: `pipeline/p4_wazn/`, `pipeline/p4_bab/`, `pipeline/p4_masdar/`, `pipeline/p4_mushtaqat/`
**Input**: RootCandidate, morphology_path
**Output**: phase4a/b/c/d results (typed orchestrator result objects)
**Slot type**: typed dataclasses
**SGA status**:
- PATTERN_SLOT (final_wazn): implicit in phase4a_result.final_wazn — NOT a Slot object
- BAB_SLOT (final_form): implicit in phase4b_result.final_bab — NOT a Slot object
- MASDAR_SLOT (final_masdar): implicit in phase4c_result.final_masdar — NOT a Slot object
**Residuals**: residual_codes in phase4a/b objects (plain string tuples) — UNTYPED

**SGA Violations**:
- UNTYPED_SLOT: PATTERN_SLOT, BAB_SLOT, MASDAR_SLOT all implicit in dataclass fields
- RESIDUAL_LOSS: residual_codes are plain strings

## P5: Lexical / Inflection / Word Class

**Module**: `pipeline/p5_lexical/`, `pipeline/p5_inflection/`, `pipeline/word_class/`
**Input**: surface, root, bab_id, form_family, wazn_id, morphology_path
**Output**: phase5_result, word_class_result (typed dataclasses)
**Slot type**: typed dataclasses
**SGA status**:
- PARADIGM_SLOT: implicit in phase5_result.paradigm_candidate.paradigm_id — NOT a Slot object
- INFLECTION_PREFIX_SLOT: implicit in phase5_result.inflectional_form fields — NOT Slot objects
- WORD_CLASS_SLOT: implicit in word_class_result.word_class — NOT a Slot object
**WRONG_SORT**: يَسْتَطِيعُ classified as ISM (incorrect — should be FI3L for Form X verb)

**SGA Violations**:
- UNTYPED_SLOT: all P5 output fields
- WRONG_SORT: word_class=ISM for يَسْتَطِيعُ (verb)
- EVIDENCELESS_ACCEPT: word_class ACCEPTED without EvidenceContract in SlotGraph

## Taaqol Integration Layer

**Module**: `pipeline/taaqol_integration/live/bridge.py`
**Input**: HokomLinguisticClaimBundle
**Output**: HokomTaaqolDecision
**Slot type in Taaqol**: 1-2 properly typed Taaqol Slot objects (domain_claim, optional word_class_claim)
**Critical bug**: _REPO_ROOT miscalculation (line 22) — vendor path wrong, all evaluations DEFERRED

**SGA status of bridge output**:
- OPAQUE_BRIDGE_PAYLOAD: HokomTaaqolDecision.trace is plain string events
- TRACE_LOSS: gate TraceEntryCandidate never appended to TraceLedger
- MISSING_REQUIRED_SLOT: only 1-2 of the required linguistic slots expressed
- SILENT_CANDIDATE_SELECTION: domain_claim value selected directly from verdict string
- OWNER_DUPLICATION: Arabic morphological term matching in _build_evidence_contract
- RANK_DRIFT: graph rank heuristically assigned (HYPOTHESIS for ACCEPT)
