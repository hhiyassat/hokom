from __future__ import annotations
import os, sys
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from pipeline.execution_ledger.hokom_stage_registry import (
    validate_registry, HOKOM_STAGE_REGISTRY, EXPECTED_HOKOM_STAGE_COUNT,
    get_stage, get_all_stage_ids, token_scope_stages, higher_scope_stages,
    HOKOM_TOKEN_STAGES, HOKOM_SPAN_OR_HIGHER_STAGES,
)

def test_hokom_stage_count_exactly_19():
    """CONSTITUTIONAL: Hokom must have exactly 19 stages."""
    assert len(HOKOM_STAGE_REGISTRY) == 19, (
        f"HOKOM_STAGE_REGISTRY_COUNT_MISMATCH: expected 19, got {len(HOKOM_STAGE_REGISTRY)}"
    )

def test_validate_registry_no_errors():
    errors = validate_registry()
    assert errors == [], f"Registry validation errors: {errors}"

def test_terminal_stage_is_p12():
    terminals = [s for s in HOKOM_STAGE_REGISTRY if s.terminal]
    assert len(terminals) == 1
    assert terminals[0].stage_id == "P12_IFADAH_SPEECH_FORCE"

def test_no_duplicate_stage_ids():
    ids = get_all_stage_ids()
    assert len(ids) == len(set(ids)), "Duplicate stage IDs found"

def test_p0_is_first_stage():
    assert HOKOM_STAGE_REGISTRY[0].stage_id == "P0_UNICODE_CANDIDATE"

def test_token_stages_count():
    token_stages = token_scope_stages()
    assert len(token_stages) == 12, f"Expected 12 token-scope stages, got {len(token_stages)}"

def test_higher_scope_stages_count():
    higher_stages = higher_scope_stages()
    assert len(higher_stages) == 7, f"Expected 7 higher-scope stages, got {len(higher_stages)}"

def test_expected_constant_matches_registry():
    assert EXPECTED_HOKOM_STAGE_COUNT == len(HOKOM_STAGE_REGISTRY)

def test_all_stages_have_executor():
    for s in HOKOM_STAGE_REGISTRY:
        assert s.executor, f"Stage {s.stage_id} missing executor"

def test_stage_id_p0_through_p12():
    ids = set(get_all_stage_ids())
    required = {
        "P0_UNICODE_CANDIDATE", "P0_TYPED_CODEPOINT", "P0_GLYPH_CLASSIFICATION",
        "P1_LETTER_IDENTITY_CARRIER", "P1_HARAKA_MARK_IDENTITY_CARRIER",
        "P1_CONDITIONED_TYPED_SEQUENCE", "P1_POSITION_CARRIER", "P1_SLOT_CANDIDATE",
        "P2_REGISTRY_PROJECTION", "P3_ROOT_STEM_CLOSURE", "P4_JAMID_MUSHTAQ",
        "P5_MUFRAD_WORD_CONTRACTS", "P6_VERBAL_SIGNIFIED_ALONE", "P7_COMPOSITION_READINESS",
        "P8_AMIL_MAMUL", "P9_SENTENCE_GEOMETRY", "P10_RELATION_GEOMETRY",
        "P11_IRAB_GEOMETRY", "P12_IFADAH_SPEECH_FORCE",
    }
    missing = required - ids
    assert not missing, f"Missing required stages: {missing}"
