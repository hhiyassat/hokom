# SGA Conformance Audit — Serialization Contract
## HOKOM-TAAQOL-SLOT-GEOMETRY-ALGEBRA-CONFORMANCE-01

### SERIALIZATION_CONTRACT_STATUS: PARTIAL

### HokomTaaqolDecision Serialization

**Present** (`models.py` lines 122–123):
```python
def to_dict(self) -> dict:
    return dataclasses.asdict(self)
```

**Absent** (Violation T-13):
- No `from_dict()` classmethod
- No `from_json()` method
- No round-trip test: `assert Decision.from_dict(d.to_dict()) == d`
- No JSON schema / Pydantic validator

### Residual Typing (Violation T-14)

`HokomTaaqolDecision.residuals` field (`models.py` line 104):
```python
residuals: tuple   # declared as bare 'tuple', not 'tuple[HokomTaaqolResidual, ...]'
```

`HokomTaaqolResidual` IS defined in models.py:
```python
@dataclass(frozen=True)
class HokomTaaqolResidual:
    code: str
    claim_id: str
    reason: str
```

But the bridge populates `residuals` with plain strings (not HokomTaaqolResidual instances). The type annotation and the actual populated type do not match.

### Serialization Surface Area

| Type | to_dict | from_dict | Round-trip Test |
|------|---------|-----------|-----------------|
| HokomTaaqolDecision | YES | NO | NO |
| HokomClaimProjection | NO (no method) | NO | NO |
| HokomTaaqolTraceEvent | via asdict() | NO | NO |
| HokomTaaqolResidual | via asdict() | NO | NO |
| TaaqolIntegrationOwnershipGate | YES | NO | NO |

### Remediation

1. Add `@classmethod from_dict(cls, d: dict) -> HokomTaaqolDecision` to HokomTaaqolDecision
2. Type `residuals` as `tuple[HokomTaaqolResidual, ...]` and populate with typed instances in bridge
3. Add round-trip test: `assert HokomTaaqolDecision.from_dict(decision.to_dict()) == decision`
