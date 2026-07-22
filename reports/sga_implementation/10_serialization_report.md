# SGA Serialization Report
**Stage**: HOKOM-TAAQOL-SGA-CONSTITUTIONAL-CONVERGENCE-01
**Commit**: ee418b6
**Tasks**: T-02, T-03, T-09, T-10

## PhonologicalSlot (T-02)

`wrap_syllabify_output()` in `pipeline/p1_atomic_structure/phonological_slot.py` converts
the raw `list[dict]` from `syllabify()` into `tuple[PhonologicalSlot, ...]`.

Each `PhonologicalSlot` is a frozen dataclass with fields:
- `character: str` — extracted from `surface`/`letter`/`char`/`character` (priority order)
- `kind: str` — from explicit `kind`/`type` key, or inferred via `_infer_kind_from_syllabify_dict()`
- `assimilation_gemination_type: Optional[str]` — from `saturation_reason`
- `original_surface: Optional[str]` — provenance of source cell

Serialization: `dataclasses.asdict()` — fully JSON-serializable.

## HokomClaimBundle (T-03, T-09)

`build_claim_bundle()` in `pipeline/sga/adapters.py` produces a `HokomClaimBundle`
(frozen dataclass) with:
- `claim_key: str` — SHA-256 digest of `json.dumps(sorted(...))` — deterministic
- `typed_slots: tuple[TypedSlot, ...]` — 23 slots (H0-H15) sorted by `SlotSort`
- `candidate_sets: dict[str, CandidateSet]` — keyed by `SlotId.value`
- `residuals: tuple[HokomResidualRecord, ...]`
- `surface: SurfaceProvenance`

All component types are frozen dataclasses. `HokomClaimBundle.to_dict()` produces a
fully JSON-serializable representation.

## HokomTaaqolDecision (T-03)

`evaluate_sga_bundle()` returns `HokomTaaqolDecision` (frozen dataclass) with:
- `taaqol_verdict: str` — LICENSED | DEFERRED | BLOCKED | RESIDUAL
- `effective_verdict: str` — composed final verdict
- `typed_slots: Optional[tuple]` — serialized TypedSlots from SlotGraph
- All fields JSON-serializable via `to_dict()` / `dataclasses.asdict()`

## T-10 Ambiguity Serialization

When `root_candidate` is a list, the `CandidateSet` in `candidate_sets[ROOT_CANDIDATE_SET]`
carries all candidates as `tuple[CandidateEntry, ...]` with `selected=None`.
The `HokomResidualRecord(code=AMBIGUOUS_CANDIDATE_SET)` in `residuals` carries the full
`candidate_set` for downstream disambiguation. No silent collapse ever occurs.
