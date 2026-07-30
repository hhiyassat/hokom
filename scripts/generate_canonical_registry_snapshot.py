"""
generate_canonical_registry_snapshot.py
— generates data/canonical_19_stage_registry.json from Saleh/Qiyas

Run once (or after any Saleh registry change):

    cd /path/to/hokom
    PYTHONPATH=src:vendor/Taaqol-GPT/src:../fractal/algebra/Saleh-/src \
        python scripts/generate_canonical_registry_snapshot.py

The generated JSON is the immutable provenance snapshot consumed by
src/hokom/canonical/registry/saleh_snapshot.py at runtime.

Ownership: Saleh/Qiyas is the sole canonical owner of the 19-stage
registry. This script is a read-only consumer — it imports, reads, and
serializes; it NEVER writes back to Saleh.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import sys
from pathlib import Path

# ── path resolution ────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve().parent
_HOKOM_ROOT = _HERE.parent
_FRACTAL_ROOT = _HOKOM_ROOT.parent / "fractal"
_SALEH_SRC = _FRACTAL_ROOT / "algebra" / "Saleh-" / "src"

if str(_SALEH_SRC) not in sys.path:
    sys.path.insert(0, str(_SALEH_SRC))

# ── Saleh import ───────────────────────────────────────────────────────────────
try:
    from qiyas_core.slot_geometry_core.master_registry_seed import (
        build_p12_implemented_registry,
        LAYER_ID_P12_IFADAH_SPEECH_FORCE,
    )
    from qiyas_core.slot_geometry_core.layer_spec import LayerStatus
except ImportError as exc:
    print(
        f"ERROR: Cannot import Saleh/Qiyas from {_SALEH_SRC}.\n"
        f"Cause: {exc}\n"
        "Make sure PYTHONPATH includes the Saleh src directory.",
        file=sys.stderr,
    )
    sys.exit(1)

# ── canonical ordinal order (verbatim from master_registry_seed.py §4.2) ──────
_CANONICAL_ORDER: list[str] = [
    "P0_UNICODE_CANDIDATE",
    "P0_TYPED_CODEPOINT",
    "P0_GLYPH_CLASSIFICATION",
    "P1_LETTER_IDENTITY_CARRIER",
    "P1_HARAKA_MARK_IDENTITY_CARRIER",
    "P1_CONDITIONED_TYPED_SEQUENCE",
    "P1_POSITION_CARRIER",
    "P1_SLOT_CANDIDATE",
    "P2_REGISTRY_PROJECTION",
    "P3_ROOT_STEM_CLOSURE",
    "P4_JAMID_MUSHTAQ",
    "P5_MUFRAD_WORD_CONTRACTS",
    "P6_VERBAL_SIGNIFIED_ALONE",
    "P7_COMPOSITION_READINESS",
    "P8_AMIL_MAMUL",
    "P9_SENTENCE_GEOMETRY",
    "P10_RELATION_GEOMETRY",
    "P11_IRAB_GEOMETRY",
    "P12_IFADAH_SPEECH_FORCE",
]


def _layer_to_dict(spec, ordinal: int) -> dict:
    """Serialize one LayerSpec to a snapshot-compatible dict."""
    return {
        "id": spec.id,
        "name": spec.name,
        "phase": spec.phase,
        "status": spec.status.value,
        "ordinal": ordinal,
        "is_terminal": spec.target_boundary_opens == (),
        "origin_layer_id": spec.origin.layer_id,
        "origin_output_type": spec.origin.output_type,
        "branch_output_type": spec.branch.output_type,
        "branch_reason": spec.branch.branch_reason,
        "shared_cause": spec.shared_cause,
        "conditions": list(spec.conditions),
        "blockers": list(spec.blockers),
        "invalidating_differences": list(spec.invalidating_differences),
        "target_boundary_closes": list(spec.target_boundary_closes),
        "target_boundary_opens": list(spec.target_boundary_opens),
        "forbidden_outputs": list(spec.forbidden_outputs),
        "minimum_required_fields": list(spec.minimum_required_fields),
        "preserves_ids": list(spec.preserves_ids),
        "allowed_changes": list(spec.allowed_changes),
        "forbidden_changes": list(spec.forbidden_changes),
        "allowed_previous_layer_ids": list(spec.allowed_previous_layer_ids),
        "allowed_next_layer_ids": list(spec.allowed_next_layer_ids),
        "forbidden_direct_next_layer_ids": list(
            spec.forbidden_direct_next_layer_ids
        ),
    }


def generate(output_path: Path | None = None) -> dict:
    """
    Call Saleh's build_p12_implemented_registry(), serialize to snapshot dict,
    optionally write to output_path.

    Returns the snapshot dict.
    """
    registry = build_p12_implemented_registry()

    # Verify all 19 layers present and IMPLEMENTED
    for layer_id in _CANONICAL_ORDER:
        spec = registry.get(layer_id)
        assert spec.status is LayerStatus.IMPLEMENTED, (
            f"Expected {layer_id} IMPLEMENTED, got {spec.status}"
        )

    # Build layer list in canonical ordinal order
    layers: list[dict] = []
    for ordinal, layer_id in enumerate(_CANONICAL_ORDER):
        spec = registry.get(layer_id)
        layers.append(_layer_to_dict(spec, ordinal))

    # Compute registry digest over layer IDs + statuses (deterministic)
    digest_input = "|".join(
        f"{l['id']}:{l['status']}" for l in layers
    ).encode("utf-8")
    registry_digest = hashlib.sha256(digest_input).hexdigest()

    # Determine Saleh commit SHA from git (best-effort)
    saleh_commit_sha = "c2c7145"  # fallback — audited 2026-07-29
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(_SALEH_SRC.parent),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            saleh_commit_sha = result.stdout.strip()
    except Exception:
        pass

    snapshot = {
        "provenance": {
            "saleh_commit_sha": saleh_commit_sha,
            "saleh_src_path": str(_SALEH_SRC),
            "generation_function": "build_p12_implemented_registry",
            "registry_digest": registry_digest,
            "generator_script": "scripts/generate_canonical_registry_snapshot.py",
        },
        "schema_version": "1.0",
        "layer_count": len(layers),
        "terminal_layer_id": LAYER_ID_P12_IFADAH_SPEECH_FORCE,
        "no_layer_after_p12": True,
        "canonical_order": _CANONICAL_ORDER,
        "layers": layers,
    }

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False))
        print(f"Wrote {len(layers)}-layer snapshot → {output_path}")
        print(f"  digest: {registry_digest}")
        print(f"  saleh_commit_sha: {saleh_commit_sha}")

    return snapshot


if __name__ == "__main__":
    out = _HOKOM_ROOT / "data" / "canonical_19_stage_registry.json"
    if len(sys.argv) > 1:
        out = Path(sys.argv[1])
    generate(out)
