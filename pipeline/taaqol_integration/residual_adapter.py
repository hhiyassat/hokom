"""
Residual mapping: Hokom residual codes -> Taaqol residual classification.
"""
from __future__ import annotations
from dataclasses import dataclass


RESIDUAL_CLASSES = {
    'BLOCKING': 'blocking_residual',
    'DEFERRABLE': 'deferrable_residual',
    'NON_BLOCKING': 'non_blocking_residual',
    'EXPLANATORY': 'explanatory_residual',
    'HIDDEN_FORBIDDEN': 'hidden_residual',
}


@dataclass(frozen=True)
class ClassifiedResidual:
    code: str
    classification: str     # BLOCKING | DEFERRABLE | NON_BLOCKING | EXPLANATORY | HIDDEN_FORBIDDEN
    is_active: bool
    is_resolved: bool


@dataclass(frozen=True)
class ResidualMappingResult:
    classified: tuple
    blocking_count: int
    deferrable_count: int
    hidden_count: int
    verdict: str    # CLEAR | DEFERRABLE | BLOCKING | HIDDEN


def map_residuals(active: tuple, resolved: tuple) -> ResidualMappingResult:
    """
    Map and classify residuals.
    - Active residual cannot appear in resolved simultaneously.
    - Hidden residuals trigger contract refusal.
    """
    classified = []

    # Validate no overlap
    active_set = set(active)
    resolved_set = set(resolved)
    hidden = active_set & resolved_set  # appearing in both = HIDDEN_FORBIDDEN

    for code in active:
        cls = _classify_residual(code)
        if code in hidden:
            cls = 'HIDDEN_FORBIDDEN'
        classified.append(ClassifiedResidual(
            code=code,
            classification=cls,
            is_active=True,
            is_resolved=False,
        ))

    for code in resolved:
        if code not in hidden:
            classified.append(ClassifiedResidual(
                code=code,
                classification=_classify_residual(code),
                is_active=False,
                is_resolved=True,
            ))

    blocking = sum(1 for c in classified if c.classification == 'BLOCKING' and c.is_active)
    deferrable = sum(1 for c in classified if c.classification == 'DEFERRABLE' and c.is_active)
    hidden_count = sum(1 for c in classified if c.classification == 'HIDDEN_FORBIDDEN')

    if hidden_count > 0:
        verdict = 'HIDDEN'
    elif blocking > 0:
        verdict = 'BLOCKING'
    elif deferrable > 0:
        verdict = 'DEFERRABLE'
    else:
        verdict = 'CLEAR'

    return ResidualMappingResult(
        classified=tuple(classified),
        blocking_count=blocking,
        deferrable_count=deferrable,
        hidden_count=hidden_count,
        verdict=verdict,
    )


def _classify_residual(code: str) -> str:
    code_lower = code.lower()
    if 'block' in code_lower or 'forbidden' in code_lower or 'illegal' in code_lower:
        return 'BLOCKING'
    if 'defer' in code_lower or 'pending' in code_lower or 'incomplete' in code_lower:
        return 'DEFERRABLE'
    if 'explain' in code_lower or 'note' in code_lower or 'info' in code_lower:
        return 'EXPLANATORY'
    return 'NON_BLOCKING'
