"""
tests/canonical/test_registry_snapshot_determinism.py
— Byte-level determinism and structural integrity for canonical registry snapshot.

Mandate: two consecutive generator runs must produce byte-identical output.
The wall-clock `generated_at` field was the sole source of nondeterminism and
has been removed from the canonical snapshot schema.

Prerequisites
-------------
    The generator must be runnable — Saleh/Qiyas importable on PYTHONPATH:

        PYTHONPATH=src:vendor/Taaqol-GPT/src:../fractal/algebra/Saleh-/src \\
            python -m pytest tests/canonical/test_registry_snapshot_determinism.py -vv

Tests
-----
    01 — No generated_at field in provenance (regression guard)
    02 — Two consecutive runs produce byte-identical JSON (2-second delay)
    03 — File SHA-256 is identical across both runs
    04 — Internal registry_digest is identical across both runs
    05 — layer_count == 19 in both runs
    06 — terminal_layer_id == P12_IFADAH_SPEECH_FORCE in both runs
    07 — P12 is_terminal == True and target_boundary_opens == [] in both runs
    08 — No P13 in canonical_order in both runs
    09 — Generated output matches the committed data/canonical_19_stage_registry.json
         modulo saleh_src_path (machine-specific, see PORTABILITY NOTE below)

PORTABILITY NOTE
----------------
    provenance.saleh_src_path is an absolute machine-specific path
    (/Users/husseinhiyassat/fractal/algebra/Saleh-/src on the primary workstation).
    It does NOT cause same-machine nondeterminism (it is stable within a run),
    but it will differ across machines and CI environments.
    This is a known portability concern; it is out of scope for this repair.
    Do not modify saleh_src_path handling in this file unless a portability
    mandate is issued separately.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import time
from pathlib import Path

import pytest

# ── locate the generator module ───────────────────────────────────────────────

_HOKOM_ROOT = Path(__file__).resolve().parents[2]   # tests/canonical → hokom
_GENERATOR_PATH = _HOKOM_ROOT / "scripts" / "generate_canonical_registry_snapshot.py"
_SNAPSHOT_PATH = _HOKOM_ROOT / "data" / "canonical_19_stage_registry.json"

_GENERATOR_AVAILABLE = False
_GENERATOR_IMPORT_ERROR: str = ""

try:
    spec = importlib.util.spec_from_file_location(
        "generate_canonical_registry_snapshot",
        _GENERATOR_PATH,
    )
    _gen_module = importlib.util.module_from_spec(spec)           # type: ignore[arg-type]
    spec.loader.exec_module(_gen_module)                          # type: ignore[union-attr]
    _GENERATOR_AVAILABLE = True
except Exception as _exc:
    _GENERATOR_IMPORT_ERROR = str(_exc)


_SALEH_AVAILABLE = _GENERATOR_AVAILABLE  # generator import = Saleh importable

pytestmark = pytest.mark.skipif(
    not _SALEH_AVAILABLE,
    reason=(
        f"Generator / Saleh not importable: {_GENERATOR_IMPORT_ERROR}. "
        "Run with correct PYTHONPATH."
    ),
)


# ── shared fixture: two runs separated by ≥2 seconds ─────────────────────────

@pytest.fixture(scope="module")
def two_runs():
    """
    Call generate() twice, sleeping ≥2 s between runs so any residual
    wall-clock dependency cannot accidentally produce identical output.

    Returns (run1_bytes, run2_bytes, run1_dict, run2_dict).
    """
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f1, \
         tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f2:
        path1 = Path(f1.name)
        path2 = Path(f2.name)

    _gen_module.generate(path1)          # type: ignore[union-attr]
    time.sleep(2)                        # ensure any wall-clock field would differ
    _gen_module.generate(path2)          # type: ignore[union-attr]

    bytes1 = path1.read_bytes()
    bytes2 = path2.read_bytes()
    dict1 = json.loads(bytes1)
    dict2 = json.loads(bytes2)

    path1.unlink(missing_ok=True)
    path2.unlink(missing_ok=True)

    return bytes1, bytes2, dict1, dict2


# ── test 01: no generated_at in provenance ───────────────────────────────────

def test_01_no_generated_at_in_provenance(two_runs):
    """
    Regression guard: generated_at must NOT appear in the provenance block.
    Its removal is the source of the fix.
    """
    _, _, d1, d2 = two_runs
    assert "generated_at" not in d1["provenance"], (
        "run1: generated_at is still present in provenance — nondeterminism not fixed"
    )
    assert "generated_at" not in d2["provenance"], (
        "run2: generated_at is still present in provenance — nondeterminism not fixed"
    )


# ── test 02: byte-identical output ───────────────────────────────────────────

def test_02_consecutive_runs_byte_identical(two_runs):
    """
    Two consecutive generator calls, separated by ≥2 seconds, must produce
    byte-for-byte identical JSON.
    """
    b1, b2, _, _ = two_runs
    assert b1 == b2, (
        "Generator output is NOT byte-identical across consecutive runs.\n"
        f"Run 1 length: {len(b1)}\n"
        f"Run 2 length: {len(b2)}\n"
        "Inspect provenance blocks for differences."
    )


# ── test 03: SHA-256 identical ───────────────────────────────────────────────

def test_03_sha256_identical(two_runs):
    """File SHA-256 must be identical across both runs."""
    b1, b2, _, _ = two_runs
    sha1 = hashlib.sha256(b1).hexdigest()
    sha2 = hashlib.sha256(b2).hexdigest()
    assert sha1 == sha2, (
        f"SHA-256 differs: run1={sha1}  run2={sha2}"
    )


# ── test 04: registry_digest identical ───────────────────────────────────────

def test_04_internal_registry_digest_identical(two_runs):
    """provenance.registry_digest must be identical in both runs."""
    _, _, d1, d2 = two_runs
    dig1 = d1["provenance"]["registry_digest"]
    dig2 = d2["provenance"]["registry_digest"]
    assert dig1, "run1: registry_digest is empty"
    assert dig2, "run2: registry_digest is empty"
    assert dig1 == dig2, (
        f"registry_digest differs:\n  run1: {dig1}\n  run2: {dig2}"
    )


# ── test 05: layer_count == 19 ────────────────────────────────────────────────

def test_05_layer_count_19(two_runs):
    """Both runs must produce exactly 19 layers."""
    _, _, d1, d2 = two_runs
    assert d1["layer_count"] == 19, f"run1 layer_count={d1['layer_count']}"
    assert d2["layer_count"] == 19, f"run2 layer_count={d2['layer_count']}"
    assert len(d1["layers"]) == 19, f"run1 actual layers={len(d1['layers'])}"
    assert len(d2["layers"]) == 19, f"run2 actual layers={len(d2['layers'])}"


# ── test 06: terminal_layer_id == P12 ────────────────────────────────────────

def test_06_terminal_layer_id_p12(two_runs):
    """terminal_layer_id must be P12_IFADAH_SPEECH_FORCE in both runs."""
    _EXPECTED = "P12_IFADAH_SPEECH_FORCE"
    _, _, d1, d2 = two_runs
    assert d1["terminal_layer_id"] == _EXPECTED, (
        f"run1 terminal_layer_id={d1['terminal_layer_id']}"
    )
    assert d2["terminal_layer_id"] == _EXPECTED, (
        f"run2 terminal_layer_id={d2['terminal_layer_id']}"
    )


# ── test 07: P12 is_terminal and target_boundary_opens ───────────────────────

def test_07_p12_is_terminal_and_boundary_empty(two_runs):
    """P12 must have is_terminal=True and target_boundary_opens=[] in both runs."""
    for label, snap in [("run1", two_runs[2]), ("run2", two_runs[3])]:
        p12 = next(
            (l for l in snap["layers"] if l["id"] == "P12_IFADAH_SPEECH_FORCE"),
            None,
        )
        assert p12 is not None, f"{label}: P12 not found in layers"
        assert p12["is_terminal"] is True, (
            f"{label}: P12 is_terminal={p12['is_terminal']}"
        )
        assert p12["target_boundary_opens"] == [], (
            f"{label}: P12 target_boundary_opens={p12['target_boundary_opens']}"
        )


# ── test 08: no P13 ───────────────────────────────────────────────────────────

def test_08_no_p13_in_canonical_order(two_runs):
    """No P13 layer ID may appear in canonical_order in either run."""
    for label, snap in [("run1", two_runs[2]), ("run2", two_runs[3])]:
        for lid in snap["canonical_order"]:
            assert not lid.startswith("P13"), (
                f"{label}: P13 found in canonical_order: {lid}"
            )
        for layer in snap["layers"]:
            assert not layer["id"].startswith("P13"), (
                f"{label}: P13 found in layers: {layer['id']}"
            )


# ── test 09: matches committed snapshot ──────────────────────────────────────

def test_09_matches_committed_snapshot(two_runs):
    """
    The regenerated output must match the committed data/canonical_19_stage_registry.json
    modulo saleh_src_path, which is a known machine-specific absolute path.

    Only the structural content is compared: layers, canonical_order,
    layer_count, registry_digest, terminal_layer_id, no_layer_after_p12.
    provenance.saleh_src_path is excluded (PORTABILITY NOTE in module docstring).
    """
    if not _SNAPSHOT_PATH.exists():
        pytest.skip(f"Committed snapshot not found at {_SNAPSHOT_PATH}")

    committed = json.loads(_SNAPSHOT_PATH.read_bytes())
    _, _, regen, _ = two_runs   # run1 is sufficient

    # Structural fields
    assert regen["layer_count"] == committed["layer_count"], (
        f"layer_count: regen={regen['layer_count']} committed={committed['layer_count']}"
    )
    assert regen["terminal_layer_id"] == committed["terminal_layer_id"]
    assert regen["no_layer_after_p12"] == committed["no_layer_after_p12"]
    assert regen["canonical_order"] == committed["canonical_order"]
    assert regen["schema_version"] == committed["schema_version"]

    # registry_digest is the integrity seal — must match
    assert regen["provenance"]["registry_digest"] == committed["provenance"]["registry_digest"], (
        "registry_digest mismatch: Saleh registry has changed or "
        "the committed snapshot is stale. Re-run the generator."
    )

    # Layer content must match exactly
    regen_layers_by_id = {l["id"]: l for l in regen["layers"]}
    committed_layers_by_id = {l["id"]: l for l in committed["layers"]}
    for lid, committed_layer in committed_layers_by_id.items():
        assert lid in regen_layers_by_id, f"Layer {lid} missing from regen"
        assert regen_layers_by_id[lid] == committed_layer, (
            f"Layer {lid} content differs between regen and committed snapshot"
        )
