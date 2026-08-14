"""
CW2 structural ownership regression test.

Proves EXACTLY ONE production P3 root authority: pipeline/p3_candidate.
Fails if a second root authority (H2RS bridge / root_by_alignment / provider
certificate) is reintroduced into the production runtime path.

Structural (source-level) — does not run morphology. No production code changed.
"""
from __future__ import annotations

import os
import re

_HOKOM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# production runtime = hokom_pipeline.py + pipeline/ (EXCLUDING audit-only areas)
_EXCLUDE = ("__pycache__", "/tests/", "taaqol_integration/audit_layer")
# tokens that would indicate a competing root authority wired into production
_FOREIGN_ROOT_AUTHORITIES = (
    "qiyas_h2rs_bridge_demo",
    "root_by_alignment",
    "certify_morphology",
    "MorphologyOwnerCertificate",
)


def _production_py_files():
    files = [os.path.join(_HOKOM, "hokom_pipeline.py")]
    for root, _dirs, names in os.walk(os.path.join(_HOKOM, "pipeline")):
        if any(x in root for x in _EXCLUDE):
            continue
        for n in names:
            if n.endswith(".py"):
                p = os.path.join(root, n)
                if not any(x in p for x in _EXCLUDE):
                    files.append(p)
    return files


def _import_lines(src: str):
    return [ln for ln in src.splitlines()
            if re.match(r"\s*(import|from)\s", ln)]


def test_no_foreign_root_authority_imported_in_production():
    offenders = []
    for f in _production_py_files():
        src = open(f, encoding="utf-8").read()
        for ln in _import_lines(src):
            for tok in _FOREIGN_ROOT_AUTHORITIES:
                if tok in ln:
                    offenders.append((f, ln.strip()))
    assert not offenders, f"foreign root authority imported in production: {offenders}"


def test_single_production_root_entrypoint():
    src = open(os.path.join(_HOKOM, "hokom_pipeline.py"), encoding="utf-8").read()
    # the ONLY licensed production root producer call
    assert "resolve_root_pipeline(" in src
    assert "from pipeline.p3_candidate.root_resolution_orchestrator import resolve_root_pipeline" in src
    # no competing root-producing call in the live pipeline
    for tok in ("certify_morphology(", "root_by_alignment", "WaznAligner("):
        assert tok not in src, f"competing root producer call in hokom_pipeline: {tok}"


def test_p3_candidate_does_not_call_h2rs():
    """The authoritative owner must not secretly delegate to a foreign engine."""
    p3 = os.path.join(_HOKOM, "pipeline", "p3_candidate")
    for root, _d, names in os.walk(p3):
        if "__pycache__" in root:
            continue
        for n in names:
            if not n.endswith(".py"):
                continue
            src = open(os.path.join(root, n), encoding="utf-8").read()
            for ln in _import_lines(src):
                for tok in _FOREIGN_ROOT_AUTHORITIES:
                    assert tok not in ln, f"{n}: p3_candidate imports foreign {tok}"


def test_active_production_root_authorities_is_one():
    """Aggregate invariant: P3_ROOT_AUTHORITIES_ACTIVE == 1."""
    authorities = set()
    for f in _production_py_files():
        src = open(f, encoding="utf-8").read()
        if "resolve_root_pipeline(" in src and f.endswith("hokom_pipeline.py"):
            authorities.add("pipeline.p3_candidate")
        for ln in _import_lines(src):
            if "root_by_alignment" in ln:
                authorities.add("root_by_alignment")
            if "certify_morphology" in ln or "qiyas_h2rs_bridge_demo" in ln:
                authorities.add("h2rs_bridge")
    assert authorities == {"pipeline.p3_candidate"}, authorities
