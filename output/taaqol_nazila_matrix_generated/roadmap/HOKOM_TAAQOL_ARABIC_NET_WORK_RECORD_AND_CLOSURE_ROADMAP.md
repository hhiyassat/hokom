# HOKOM_TAAQOL_ARABIC_NET_WORK_RECORD_AND_CLOSURE_ROADMAP

**TASK_ID:** `HOKOM_TAAQOL_ARABIC_NET_RECORD_AND_CLOSURE_ROADMAP_01`
**AUTHORITY:** `DOCUMENTATION_AND_ROADMAP_ONLY` · **PROJECT_FINISHED = NO**

> This round is **documentation and plan only**. No new repair is executed. No gate is opened.
> `madlul_text_ar` is not filled. No score is changed. No commit / push / git-add.

---

## 1. Executive State

### ما أُنجز (done)
- **Arabic-Net semantic API** built and measured: `semantic_api.py` (8 functions), 65,544 Arabic
  lemmas, 17 relation types, 5,553 families — deterministic, offline, evidence-backed.
- **Source registration** (`data/governance/approved_semantic_source_registry.csv`):
  `ARABIC_NET = APPROVED_GENERAL_SEMANTIC_SOURCE`, `taaqol_arabic_analysis_allowed = NO`.
- **Hokom surface→lemma bridge** (`scripts/hokom_surface_lemma_bridge.py`): Hokom-owned morphology,
  Axis-2 not weakened (`exact_axis2_surface_match = NO`).
- **Live position reflection** into `wire_dal_madlul`: t003 now carries a source-derived
  `madlul_position` (synset) on the live row — **position only**, binding still DEFERRED.

### ما لم يُنجز (not done)
- No **licensed `madlul_text_ar`** anywhere (`TEXT_LICENSED_MADLUL_COUNT = 0`).
- No **gloss source** chosen (`wordnet_synsets.json` has no gloss field).
- t003 is **not bound** (`DAL_MADLUL_BOUND = NO`).
- `MANAT` / `TANZIL` / `ANSWER_AUDIT` remain closed.

### ما لا يجوز ادعاؤه (must not be claimed)
- That a **synset position is a meaning** (position ≠ meaning).
- That t003 is **bound / licensed**.
- That the **surface→lemma bridge** performs Axis-4 peeling.
- That the **kinship family** is an approved clean source layer.
- That any **tool paraphrase** is evidence.

---

## 2. Arabic-Net Work Record

### ما بُني (built)
| item | evidence |
|---|---|
| `semantic_api.py` | 8 functions; `lookup_lemma("أُخْت") → sibling.n.01`; families `family.n.02 / relative.n.01` |
| registration | `approved_semantic_source_registry.csv`, `ARABIC_NET = APPROVED_GENERAL_SEMANTIC_SOURCE` |
| surface→lemma bridge | `scripts/hokom_surface_lemma_bridge.py`, Hokom-owned, Axis-2 preserved |
| live position reflection | `wire_dal_madlul` → `madlul_position` / `position_source` / `position_status` columns |

### ما قيس (measured)
- **No gloss**: `wordnet_synsets.json` fields = `id, pos, words_ar, roots` → `NO_GLOSS_FIELD_IN_SYNSETS = TRUE`.
- **Kinship**: `ROLE_ALIGNED = 4/16` governing; `10/16` only with a role layer; not a clean family.
- **Index noise**: lemma→many synsets, some wrong (سيف→fish genus); API faithfully reflects the source.
- **Depth-only failure**: depth of coverage is not correctness.
- **Closed taxonomy** B / C / D / E: measurement taxonomy is bounded, not open-ended.

### ما امتُنع عنه (refused)
- No **authored madlul text**.
- No **global depth fix**.
- No **unmeasured alternative**.
- No **kinship source-layer approval**.

---

## 3. Current Taaqol/Hokom State

### t003 row
```text
token_id                     = t003
surface                      = أُخْتٍ
LIVE_POSITION_REFLECTION_ONLY = YES
madlul_position              = sibling.n.01;family.n.02;relative.n.01
position_source              = ARABIC_NET
position_status              = POSITION_DERIVED_TEXT_DEFERRED
binding_status               = DEFERRED
verdict                      = MADLUL_OWNER_PENDING
DAL_MADLUL_BOUND             = NO
madlul_text_ar               = NOT_LICENSED_NO_GLOSS
```

### Closure invariants (unchanged this round)
```text
document_percent                    = 80.0
dal_madlul_score_percent            = 90.0
dal_madlul_bound_count              = 9
owner_pending_madlul_entries_count  = 1
REGISTRY_SHA                        = d3c7b60939b5
MANAT                               = DEFERRED_WITH_CAUSE
TANZIL                              = NOT_OPENED
ANSWER_AUDIT                        = NOT_OPENED
IFADAH/HUKM source tokens           = [t000, t001]
PROJECT_FINISHED                    = NO
```

### dal_registry vs madlul_registry
- **dal_registry** — blockers open (R3-ب POSS/OBJ source undecided; B2 classes partially ruled;
  old queue B3/B5/B6/B7/B15/B17 + boundary_kind + اسم العزل + اسم القاعدة 12 + عنوان المادة السادسة).
- **madlul_registry** — owner-curated, `SHA = d3c7b60939b5`, **not mutated**; single blocker is the
  missing **licensed gloss source** for `madlul_text_ar`.

---

## 4. Roadmap To Closure (ordered by dependencies)

### A. Stabilize the current governed round
- Decide **commit vs report-only** for the position-wiring round.
- Ensure `LIVE_POSITION_REFLECTION_ONLY` naming is used everywhere.
- Ensure **t003 remains DEFERRED** (position only, never bound).

### B. Finish the Hokom-side bridge path
- **T2** audit closure (117 operators + 43 mabniyat view; explicit poison flip; سَوِيًّا P3_PENDING).
- **T1** bridge-only finalization (bridge report + guards), if not already final.
- **No Axis-4 peeling** — the bridge is not peeling.

### C. Resolve dal_registry blockers
- **R3-ب POSS/OBJ** — choose source or DEFER (no tool-authored clitic functions).
- **B2** — class-by-class BLOCK / DEFER / UNCONSTRAINED decision.
- **Old queue** — B3 · B5 · B6 · B7 · B15 · B17 · `boundary_kind` · اسم العزل ·
  اسم القاعدة 12 · عنوان المادة السادسة (kept separate from current bridge work).

### D. Resolve the madlul_registry blocker
- Choose a **licensed Arabic gloss source**, one of:
  - Arabic WordNet 4.0
  - owner-digitized Arabic dictionary
  - owner-authored text layer
- Keep **Arabic-Net as a position source only** unless a gloss source is added.

### E. Resolve C_PATH / sonaiso
- Keep **C_PATH = DEFER** until a real connection counterfactual is measured.
- Do **not** use `89.3%` except as `SUPERSEDED_PROJECTION`.
- Decide the **sonaiso** external dependency (notify / connect) without silently moving the vendor boundary.

### F. Only after **both** registries are resolved
- `DAL_MADLUL_BINDING` review → then possible **MANAT** → then **TANZIL** → then **ANSWER_AUDIT**.

---

## 5. Guardrails

```text
POSITION ≠ MEANING
BRIDGE ≠ AXIS4_PEELING
CANDIDATE ≠ PROVEN
DEPTH_IS_NOT_CORRECTNESS
BREADTH_IS_NOT_BENEFIT
NOT_MEASURABLE_HERE ≠ NOT_MEASURED_YET
NO_TOOL_PARAPHRASE_AS_EVIDENCE
```

---

## 6. Final status block

```text
PROJECT_FINISHED             = NO
DOCUMENT                     = 80.0
DAL_MADLUL                   = 90.0
TEXT_LICENSED_MADLUL_COUNT   = 0
T003                         = DEFERRED_POSITION_ONLY
LIVE_POSITION_REFLECTION_ONLY = YES
GATES_OPENED                 = NO
```
