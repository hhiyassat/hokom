# 05 — P2 REGISTRY CONTRACT

**Document ID:** `R0-05-P2-REGISTRY`  
**Phase:** R0 — Requirements Package  
**Date:** 2026-08-01  
**Status:** REQUIREMENTS_READY

---

## 1. Blocker Root Cause

**File:** `src/hokom/canonical/stages/p2_p5.py`  
**Method:** `_check_blockers(self, input: StageInput, evidence: EvidenceSet)`

```python
registry_matches = input.hokom_evidence.get("registry_matches")
failure = registry_matches is None
return (ManiBlocker(
    blocker_id="registry_load_failure",
    layer_id="P2_REGISTRY_PROJECTION",
    is_active=failure,
    severity=ResidualSeverity.BLOCKER,
    detail="Registry matches not provided — registry may not be loaded",
),)
```

**Effect:** When `hokom_evidence["registry_matches"]` is `None`, P2 blocker is `is_active=True` → P3, P4, P5 remain `NOT_OPENED`.

**Fix requirement:** The adapter layer must populate `hokom_evidence["registry_matches"]` with a non-None value (a `RegistryLookupResult`) **before** the P2 adapter runs.

---

## 2. PR-16C Schema (from `registry_contract.py`, VENDOR_SHA=35381739...)

### RegistryDomain
```python
class RegistryDomain(StrEnum):
    DAL_ONLY = "DAL_ONLY"
    VERBAL_MADLUL = "VERBAL_MADLUL"
```

### Rank (enum, bounded)
```python
# rank must be ≤ REGISTRY_RANK_CEILING
# REGISTRY_RANK_CEILING defined in registry_contract.py
```

### FailureCode (enum)
```python
class FailureCode(StrEnum):
    # Specific failure codes — read from registry_contract.py
    pass
```

### RegistryEntry (frozen dataclass)
```python
@dataclass(frozen=True, slots=True)
class RegistryEntry:
    key: str
    domain: RegistryDomain          # DAL_ONLY | VERBAL_MADLUL
    non_meaning_proof: str          # Required — proves this is NOT a semantic meaning
    rank: Rank                      # Must be ≤ REGISTRY_RANK_CEILING
    residuals: tuple[Residual, ...]
    trace_ref: str
```

### RegistryLookupState
```python
class RegistryLookupState(StrEnum):
    FOUND = "FOUND"
    REFUSED = "REFUSED"
    DEFERRED = "DEFERRED"
```

### RegistryLookupResult (frozen dataclass)
```python
@dataclass(frozen=True, slots=True)
class RegistryLookupResult:
    state: RegistryLookupState
    entry: RegistryEntry | None     # None when state != FOUND
    failure_code: FailureCode | None
```

### lookup_registry_entry()
```python
def lookup_registry_entry(key: str, ...) -> RegistryLookupResult:
    # Pure function — no I/O, no side effects
    # Returns RegistryLookupResult with appropriate state
    pass
```

---

## 3. Constitutional Invariants

| Invariant | Proof Required |
|---|---|
| `RegistryEntry ≠ Meaning` | `non_meaning_proof` field must be non-empty string |
| `RegistryEntry` contains no semantic content | No field may contain interpretation, gloss, or translation |
| `lookup_registry_entry()` is pure | No I/O; deterministic; no external calls |
| `rank ≤ REGISTRY_RANK_CEILING` | Validated at construction time |
| `entry is None` when `state != FOUND` | Type-contract guaranteed by frozen dataclass |
| No lexical content in registry schema | RegistryEntry stores structural metadata only |

---

## 4. Adapter Requirements (E0)

The Hokom P2 adapter must:

1. Call `lookup_registry_entry(token_surface)` for each token before P2 runs  
2. Store result in `hokom_evidence["registry_matches"]` — must not be `None`  
3. For tokens with no registry entry: result = `RegistryLookupResult(state=DEFERRED, entry=None, failure_code=<appropriate>)`  
4. The `DEFERRED` result still satisfies `registry_matches is not None` — blocker deactivated  
5. Adapter must carry `trace_id` from live `PipelineTrace` — no synthetic IDs  
6. Adapter must embed `VENDOR_SHA` in every produced artifact

---

## 5. P2→P3 Type Contract

| From (Hokom) | To (Taaqol weight/) | Current gap |
|---|---|---|
| `HokomLinguisticClaimBundle` | `LicensingBoundaryVerdict` | TYPE_MISMATCH — root of weight-layer gap |
| `hokom_evidence["registry_matches"]` | `RegistryLookupResult` | `None` currently — blocker active |

**Fix for P2 blocker:** populate `registry_matches`.  
**Fix for full weight-layer integration:** produce `LicensingBoundaryVerdict` from `HokomLinguisticClaimBundle` — requires `licensing_boundary.py` adapter (E0 scope).

---

## 6. Lexicon Policy

- Lexical content (Arabic word → meaning/gloss) is **NOT** part of PR-16C  
- Lexicon construction must NOT begin until registry schema is frozen  
- Lexical content belongs to a separate contract (post-E0)  
- `RegistryEntry.key` = token surface form; `RegistryEntry.non_meaning_proof` = structural proof — never a semantic gloss
