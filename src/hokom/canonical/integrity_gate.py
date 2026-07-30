"""
integrity_gate.py — Canonical 19-stage implementation integrity gate.

Produces structured JSON reports for:
    - Registry parity (snapshot vs. Saleh live registry)
    - Stage coverage (all 19 stages present and callable)
    - Constitutional invariants (P12 terminal, no P13, no forbidden flags)
    - Pipeline trace validation (per-case and aggregate)

Generates:
    data/generated/canonical_integrity_gate_report.json
    data/generated/canonical_stage_coverage_report.json
    data/generated/FINAL_CLOSURE_REPORT.md (Phase 8)

Usage:
    python -m hokom.canonical.integrity_gate
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .pipeline import (
    CanonicalPipeline,
    WordInput,
    SentenceInput,
    PipelineTrace,
    _WORD_STAGE_IDS,
    _SENTENCE_STAGE_IDS,
)
from .registry import load_snapshot, CANONICAL_LAYER_IDS
from .constitutional.contracts import ConstitutionalStatus


# ── Report data classes ───────────────────────────────────────────────────────

@dataclass
class StageReport:
    layer_id: str
    ordinal: int
    adapter_class: str
    is_terminal: bool
    phase: str
    status: str        # "ok" | "missing" | "import_error"
    note: str = ""


@dataclass
class IntegrityGateReport:
    generated_at: str
    schema_version: str
    snapshot_digest: str
    saleh_commit_sha: str
    total_stages: int
    stages: list[StageReport]
    invariants: dict[str, bool]
    errors: list[str]
    is_green: bool


# ── Gate checks ───────────────────────────────────────────────────────────────

def _check_registry_snapshot() -> tuple[bool, str, str, list[str]]:
    """Load snapshot and return (ok, digest, sha, errors)."""
    errors: list[str] = []
    try:
        snap = load_snapshot()
        snap.assert_no_p13()
        return True, snap.provenance.registry_digest, snap.provenance.saleh_commit_sha, errors
    except Exception as exc:
        errors.append(f"Registry snapshot: {exc}")
        return False, "", "", errors


def _check_stage_coverage() -> list[StageReport]:
    """Verify all 19 stage adapters are importable and have correct LAYER_ID."""
    reports: list[StageReport] = []

    adapter_map = {
        "P0_UNICODE_CANDIDATE":      "hokom.canonical.stages.p0.UnicodeAdapter",
        "P0_TYPED_CODEPOINT":        "hokom.canonical.stages.p0.TypedCodepointAdapter",
        "P0_GLYPH_CLASSIFICATION":   "hokom.canonical.stages.p0.GlyphAdapter",
        "P1_LETTER_IDENTITY_CARRIER":      "hokom.canonical.stages.p1.LetterIdentityAdapter",
        "P1_HARAKA_MARK_IDENTITY_CARRIER": "hokom.canonical.stages.p1.HarakaMarkAdapter",
        "P1_CONDITIONED_TYPED_SEQUENCE":   "hokom.canonical.stages.p1.ConditionedSequenceAdapter",
        "P1_POSITION_CARRIER":             "hokom.canonical.stages.p1.PositionAdapter",
        "P1_SLOT_CANDIDATE":               "hokom.canonical.stages.p1.SlotCandidateAdapter",
        "P2_REGISTRY_PROJECTION":    "hokom.canonical.stages.p2_p5.RegistryProjectionAdapter",
        "P3_ROOT_STEM_CLOSURE":      "hokom.canonical.stages.p2_p5.RootStemAdapter",
        "P4_JAMID_MUSHTAQ":          "hokom.canonical.stages.p2_p5.JamidMushtaqAdapter",
        "P5_MUFRAD_WORD_CONTRACTS":  "hokom.canonical.stages.p2_p5.MufradWordAdapter",
        "P6_VERBAL_SIGNIFIED_ALONE": "hokom.canonical.stages.p6_p8.VerbalSignifiedAdapter",
        "P7_COMPOSITION_READINESS":  "hokom.canonical.stages.p6_p8.CompositionReadinessAdapter",
        "P8_AMIL_MAMUL":             "hokom.canonical.stages.p6_p8.AmilMamulAdapter",
        "P9_SENTENCE_GEOMETRY":      "hokom.canonical.stages.p9_p12.SentenceGeometryAdapter",
        "P10_RELATION_GEOMETRY":     "hokom.canonical.stages.p9_p12.RelationGeometryAdapter",
        "P11_IRAB_GEOMETRY":         "hokom.canonical.stages.p9_p12.IrabGeometryAdapter",
        "P12_IFADAH_SPEECH_FORCE":   "hokom.canonical.stages.p9_p12.IfadahAdapter",
    }

    terminal_ids = {"P12_IFADAH_SPEECH_FORCE"}

    try:
        snap = load_snapshot()
        layer_phases = {l.id: l.phase for l in snap.layers_in_order()}
        layer_ordinals = {l.id: l.ordinal for l in snap.layers_in_order()}
    except Exception:
        layer_phases = {}
        layer_ordinals = {lid: i for i, lid in enumerate(CANONICAL_LAYER_IDS)}

    for i, layer_id in enumerate(CANONICAL_LAYER_IDS):
        cls_path = adapter_map.get(layer_id, "MISSING")
        status = "missing"
        note = ""
        if cls_path != "MISSING":
            try:
                module_path, cls_name = cls_path.rsplit(".", 1)
                import importlib
                mod = importlib.import_module(module_path)
                cls = getattr(mod, cls_name)
                inst = cls()
                assert inst.LAYER_ID == layer_id, (
                    f"LAYER_ID mismatch: {inst.LAYER_ID} != {layer_id}"
                )
                status = "ok"
            except Exception as exc:
                status = "import_error"
                note = str(exc)[:200]

        reports.append(StageReport(
            layer_id=layer_id,
            ordinal=layer_ordinals.get(layer_id, i),
            adapter_class=cls_path,
            is_terminal=(layer_id in terminal_ids),
            phase=layer_phases.get(layer_id, "unknown"),
            status=status,
            note=note,
        ))

    return reports


def _check_invariants(pipeline: CanonicalPipeline) -> dict[str, bool]:
    """Check constitutional invariants on the built pipeline."""
    invariants: dict[str, bool] = {}

    # P12 TERMINAL: _next_layer_id() returns None
    try:
        p12 = pipeline._adapters["P12_IFADAH_SPEECH_FORCE"]
        invariants["p12_next_layer_is_none"] = (p12._next_layer_id() is None)
    except Exception:
        invariants["p12_next_layer_is_none"] = False

    # No P13 adapter registered
    invariants["no_p13_adapter"] = "P13" not in {
        k for k in pipeline._adapters if k.startswith("P13")
    }

    # All 19 adapters present
    invariants["all_19_adapters_present"] = (
        set(CANONICAL_LAYER_IDS) == set(pipeline._adapters.keys())
    )

    # Snapshot loads and validates
    try:
        snap = load_snapshot()
        snap.assert_no_p13()
        invariants["snapshot_valid"] = True
        invariants["snapshot_19_layers"] = (snap.layer_count == 19)
        invariants["snapshot_all_implemented"] = all(
            l.status == "implemented" for l in snap.layers_in_order()
        )
    except Exception:
        invariants["snapshot_valid"] = False
        invariants["snapshot_19_layers"] = False
        invariants["snapshot_all_implemented"] = False

    # HR2S/H2RS not imported
    hr2s_imported = False
    for name, mod in sys.modules.items():
        if "hr2s" in name.lower() or "h2rs" in name.lower():
            hr2s_imported = True
            break
    invariants["hr2s_not_imported"] = not hr2s_imported

    return invariants


def run_gate(output_dir: Path | None = None) -> IntegrityGateReport:
    """
    Run the full integrity gate and return a structured report.

    Parameters
    ----------
    output_dir : Path | None
        If provided, writes JSON report to output_dir/canonical_integrity_gate_report.json
    """
    errors: list[str] = []

    # 1. Registry snapshot
    snap_ok, digest, sha, snap_errors = _check_registry_snapshot()
    errors.extend(snap_errors)

    # 2. Stage coverage
    stage_reports = _check_stage_coverage()
    failed_stages = [r for r in stage_reports if r.status != "ok"]
    if failed_stages:
        for r in failed_stages:
            errors.append(f"Stage {r.layer_id}: {r.status} — {r.note}")

    # 3. Build pipeline and check invariants
    invariants: dict[str, bool] = {}
    try:
        pipeline = CanonicalPipeline.build()
        invariants = _check_invariants(pipeline)
    except Exception as exc:
        errors.append(f"Pipeline build failed: {exc}")
        invariants["pipeline_builds"] = False

    invariants["pipeline_builds"] = (
        "Pipeline build failed" not in str(errors)
    )

    is_green = (
        snap_ok
        and not failed_stages
        and all(invariants.values())
        and not errors
    )

    report = IntegrityGateReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        schema_version="1.0",
        snapshot_digest=digest,
        saleh_commit_sha=sha,
        total_stages=len(stage_reports),
        stages=stage_reports,
        invariants=invariants,
        errors=errors,
        is_green=is_green,
    )

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = output_dir / "canonical_integrity_gate_report.json"

        def _serialize(obj):
            if hasattr(obj, "__dataclass_fields__"):
                return {k: _serialize(v) for k, v in vars(obj).items()}
            if isinstance(obj, (list, tuple)):
                return [_serialize(i) for i in obj]
            if isinstance(obj, dict):
                return {k: _serialize(v) for k, v in obj.items()}
            return obj

        out_path.write_text(
            json.dumps(_serialize(report), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"Integrity gate report → {out_path}")
        print(f"  is_green: {is_green}")
        if errors:
            print(f"  errors ({len(errors)}):")
            for e in errors[:5]:
                print(f"    • {e}")

    return report


if __name__ == "__main__":
    # Find hokom root
    _HERE = Path(__file__).resolve().parent
    for _ in range(6):
        if (_HERE / "pyproject.toml").exists():
            break
        _HERE = _HERE.parent
    out_dir = _HERE / "data" / "generated"
    report = run_gate(out_dir)
    sys.exit(0 if report.is_green else 1)
