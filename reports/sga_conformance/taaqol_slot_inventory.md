# Taaqol Slot Inventory by Module
HEAD: ce55f7b
Vendor: vendor/Taaqol-GPT/src/taaqqul_slot_geometry/

## core/slot_graph.py — SlotGraph Carrier

**SlotGraph shape**: G = ⟨Center, Slots, Boundary, Residuals, Rank, OutputBoundary, GenerationSource, EntryBoundary?⟩
**Sort enforcement**: Slot.name is a string; no enum sort field. Sorts are caller-declared names (not Taaqol's responsibility — architectural design choice).
**Insertion validation**: Every field validated in __post_init__. SlotGraphSchemaError on any violation. ConstructionResult.construct() returns named FailureCode for every expected presence-level refusal. ALIGNED.
**Boundary**: SlotBoundary(domain, scope, refusal_codes, licensed_operations). refusal_codes must be non-empty tuple of FailureCode — enforced. ALIGNED.
**Opening policy**: OpeningPolicy(allowed_potentials: frozenset[str]) — non-empty, non-empty strings enforced. ALIGNED.
**Slot**: name, value_state (SlotState enum), boundary, opening, required, value. FILLED requires value in allowed_potentials. ALIGNED.
**Residuals**: tuple[Residual, ...] — typed, visible/kind enforced by ResidualPolicy. ALIGNED.
**Trace**: TraceRef(anchor: str, kind: str) — anchor must be non-empty string. ALIGNED.
**Entry boundary**: Mandatory for DECLARED_ENTRY generation_source, must be absent otherwise. ALIGNED.

**SGA violations**: NONE. Taaqol SlotGraph is constitutionally correct.

## core/gamma.py — Gamma Closure Function

**Totality**: gamma() is total over SlotGraph domain; every refusal is a named GammaResult, never raises.
**Ordered law**: 10 steps strictly ordered; refusal at step k short-circuits k+1…10.
**Step 8**: All required slots must be FILLED before MINIMALLY_CLOSED — ALIGNED.
**Step 9**: rank ≤ ResidualCeiling — ALIGNED. gamma() never promotes rank.
**Trace**: Returns TraceEntryCandidate (stage='gamma') for caller to append. NEVER appends itself (purity). ALIGNED.
**Residual visibility**: Steps 6 and 7 check hidden/blocking residuals before closure. ALIGNED.

**SGA violations**: NONE. Gamma is constitutionally pure.

## core/transition_gate.py — TransitionGate

**All required gate fields present**:
- cause: EvidenceContract.sources (evidence presence check, step 4)
- condition: gamma() consultation (step 1) — Gamma runs before any Gate
- obstacle: Forbidden Straight-Line Registry check (step 2)
- defeater: gate_name (non-empty string, required at construction)
- evidence: EvidenceContract.evidence_rank enters lattice meet (step 5)
**Rank promotion**: only through meet() — cannot raise rank above inputs. ALIGNED.
**TransitionVerdict invariants**: APPROVED iff failure_code=None; refusal iff failure_code named; granted_rank=ZERO on refusal. ALIGNED.
**Trace split**: gate_transition_state separate from consulted_gamma_state (PR-6 binding). ALIGNED.
**Named gate**: gate_name required non-empty — unnamed gate refused at construction. ALIGNED.

**SGA violations**: NONE. TransitionGate is constitutionally correct.

## core/trace_ledger.py — TraceLedger

**Append-only**: TraceLedger.append(TraceEntryCandidate) — type-checked. ALIGNED.
**PR-6 trace split**: consulted_gamma_state (ClosureState) separate from gate_transition_state (TransitionState | None). ALIGNED.
**Purity**: gamma() and TransitionGate never import or call TraceLedger. ALIGNED.
**In-memory**: No persistence (PR-2 through PR-6 scope). ALIGNED.

**SGA violations**: NONE. TraceLedger is constitutionally correct.
**NOTE**: TraceLedger is NEVER USED by Hokom bridge — this is a Hokom violation, not Taaqol's.

## core/rank_lattice.py — RankLattice

**Lattice operations**: meet() = min, join() = max. Cannot synthesize ranks. ALIGNED.
**Domain guard**: empty or non-Rank inputs raise TypeError. ALIGNED.
**Non-promotion law**: meet() can only keep or lower — never raises. ALIGNED.

**SGA violations**: NONE.

## core/residual_policy.py — ResidualPolicy

**Typed Residual**: name (non-empty str), kind (ResidualKind enum), visible (bool), note (str). ALIGNED.
**Rank caps**: BLOCKING → ZERO, HIDDEN_FORBIDDEN → ZERO, DEFERRABLE → HYPOTHESIS, NON_BLOCKING → TOP, EXPLANATORY → TOP. ALIGNED.
**ResidualCeiling**: meet over all per-kind caps. Empty surface → TOP (vacuously no constraint). ALIGNED.
**evaluate()**: Returns ResidualEvaluation with failure_code, ceiling, all_visible, perforating. ALIGNED.
**Hidden refusal before blocking**: HIDDEN_RESIDUAL check precedes BLOCKING check (mirrors Gamma step ordering). ALIGNED.

**SGA violations**: NONE.

## core/evidence_contract.py — EvidenceContract

**EvidenceSource**: name, kind, rank (Rank enum), trace_ref (TraceRef) — all mandatory non-empty. ALIGNED.
**Single-source ceiling**: SINGLE_SOURCE_EVIDENCE_CEILING = Rank.STRONG — prevents Evidence→Certainty straight line from single source. ALIGNED.
**EvidenceContract.evidence_rank**: join over all source ranks — strongest wins, never invents above inputs. ALIGNED.
**Empty sources**: EvidenceContract(sources=()) → evidence_rank=ZERO; TransitionGate step 4 returns DEFERRED/GATE_REQUIRED. ALIGNED.

**SGA violations**: NONE.

## core/forbidden_lines.py — ForbiddenLineRegistry

**CANONICAL_REGISTRY**: Every row carries source_layer, target_layer, required_bridge, failure_code. No row is silent. ALIGNED.
**is_forbidden_direct()**: Checks source→target pair against registry. Fatal before evidence check (TransitionGate step 2). ALIGNED.
**Certificate target**: Any CERTIFICATE target through generic gate identified as Evidence→Certainty straight line. ALIGNED.

**SGA violations**: NONE.

## weight/ — Pre-Weight / Weight Carriers (PR-10)

**Carriers**: SyllableCandidate, WordCarrierCandidate, RootStemCandidate, WeightImage, Mizan, etc. All typed frozen dataclasses.
**No Arabic morphology content**: Weight carriers are pure mathematical shape carriers — no linguistic meaning assignment. ALIGNED.
**Boundary**: weight carriers land only in PATTERN_SPACE — no crossover to meaning/hukm/reality. ALIGNED.

**SGA violations**: NONE. Weight layer correctly isolated.

## Summary: Taaqol Vendor

All Taaqol vendor modules (core, weight, adapters, audit) are constitutionally correct. No Arabic morphology logic in Taaqol. No Taaqol constitutional logic misplaced in wrong module. No boundary reopens. No rank promotions outside gate. No silent failures. Serialization round-trip: no serialize/deserialize protocol defined (frozen dataclasses only) — this is a declared residual of current PRs, not a violation.

TAAQOL_SLOT_COUNT: 14 typed slot/carrier types (SlotGraph, Slot, Residual, EvidenceSource, TraceRef, TraceEntryCandidate, TransitionVerdict, GammaResult, ResidualEvaluation, ConstructionResult, EvidenceContract, SlotBoundary, OpeningPolicy, OutputBoundary)
TAAQOL SGA VIOLATIONS: 0
