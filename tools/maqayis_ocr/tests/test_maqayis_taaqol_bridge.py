"""
tests/test_maqayis_taaqol_bridge.py — Maqayis OCR v2

Unit tests for the Taaqol integration bridge:
    pipeline/taaqol_integration/maqayis_root_registry.py
    pipeline/taaqol_integration/maqayis_evidence_adapter.py

Run from the hokom root:
    python3 -m pytest tools/maqayis_ocr/tests/test_maqayis_taaqol_bridge.py -v

Live-corpus tests (TestLiveCorpusSmoke) are skipped when
data/maqaees/full/root_entries.jsonl does not exist.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

import pytest

# When run via pytest from the hokom root, pyproject.toml sets
# pythonpath = ["."] so `pipeline` is importable as a package.
# The sys.path insert here covers direct invocation / conftest.py paths.
_HOKOM_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
if _HOKOM_ROOT not in sys.path:
    sys.path.insert(0, _HOKOM_ROOT)

from pipeline.taaqol_integration.maqayis_root_registry import (
    MaqayisRootEntry,
    MaqayisRootRegistry,
    lookup,
)
from pipeline.taaqol_integration.maqayis_evidence_adapter import (
    get_maqayis_evidence_ids,
    extract_root_letters_from_bundle,
    augment_evidence_from_bundle,
)
import pipeline.taaqol_integration.maqayis_root_registry as _reg_mod


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_jsonl(entries: list[dict]) -> str:
    """Write entries to a temp JSONL file; return the path."""
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
    )
    for e in entries:
        tmp.write(json.dumps(e, ensure_ascii=False) + "\n")
    tmp.close()
    return tmp.name


def _sample_entries() -> list[dict]:
    return [
        {
            "entry_id":             "02.pdf:p3:r001",
            "source_pdf":           "02.pdf",
            "pdf_page":             3,
            "root_heading_text":    "(حد) الحاء والدال أصلان:",
            "root_letters":         "حد",
            "bab_letter":           "الحاء",
            "semantic_origin_text": "أصلان",
            "semantic_origin_type": "DUAL",
            "origin_count":         2,
            "review_status":        "AUTO_AGREED",
        },
        {
            "entry_id":             "01.pdf:p5:r001",
            "source_pdf":           "01.pdf",
            "pdf_page":             5,
            "root_heading_text":    "(كتب) الكاف والتاء والباء أصل واحد",
            "root_letters":         "كتب",
            "bab_letter":           "الكاف",
            "semantic_origin_text": "أصل واحد",
            "semantic_origin_type": "SINGULAR",
            "origin_count":         1,
            "review_status":        "AUTO_AGREED",
        },
        {
            "entry_id":             "02.pdf:p10:r001",
            "source_pdf":           "02.pdf",
            "pdf_page":             10,
            "root_heading_text":    "(حد) الحاء والدال …",
            "root_letters":         "حد",
            "bab_letter":           "الحاء",
            "semantic_origin_text": "أصلان",
            "semantic_origin_type": "DUAL",
            "origin_count":         2,
            "review_status":        "AUTO_AGREED",
        },
        {
            "entry_id":             "03.pdf:p22:r002",
            "source_pdf":           "03.pdf",
            "pdf_page":             22,
            "root_heading_text":    "(دين) الدال والياء والنون",
            "root_letters":         "دين",
            "bab_letter":           "الدال",
            "semantic_origin_text": None,
            "semantic_origin_type": "NONE",
            "origin_count":         None,
            "review_status":        "REVIEW_REQUIRED",
        },
    ]


# ══════════════════════════════════════════════════════════════════════════════
# MaqayisRootRegistry
# ══════════════════════════════════════════════════════════════════════════════

class TestMaqayisRootRegistry:

    @pytest.fixture()
    def registry(self):
        path = _make_jsonl(_sample_entries())
        yield MaqayisRootRegistry(jsonl_path=path)
        os.unlink(path)

    def test_loads_unique_roots(self, registry):
        assert registry.total_roots == 3   # حد, كتب, دين

    def test_lookup_dual_root(self, registry):
        e = registry.lookup("حد")
        assert e is not None
        assert e.root_letters == "حد"
        assert e.semantic_origin_type == "DUAL"
        assert e.origin_count == 2
        assert e.bab_letter == "الحاء"

    def test_lookup_singular_root(self, registry):
        e = registry.lookup("كتب")
        assert e is not None
        assert e.semantic_origin_type == "SINGULAR"
        assert e.origin_count == 1

    def test_lookup_unknown_root_returns_none(self, registry):
        assert registry.lookup("خرج") is None

    def test_multi_page_root_deduplicates(self, registry):
        e = registry.lookup("حد")
        assert e.entry_count == 2

    def test_multi_page_root_source_pdfs(self, registry):
        e = registry.lookup("حد")
        assert "02.pdf" in e.source_pdfs

    def test_none_origin_type(self, registry):
        e = registry.lookup("دين")
        assert e is not None
        assert e.semantic_origin_type == "NONE"
        assert e.origin_count is None

    def test_empty_jsonl(self):
        path = _make_jsonl([])
        reg = MaqayisRootRegistry(jsonl_path=path)
        assert reg.total_roots == 0
        assert reg.lookup("حد") is None
        os.unlink(path)

    def test_missing_jsonl_does_not_raise(self):
        reg = MaqayisRootRegistry(jsonl_path="/nonexistent/path.jsonl")
        assert reg.total_roots == 0

    def test_repr_contains_root_count(self, registry):
        assert "3" in repr(registry)

    def test_len(self, registry):
        assert len(registry) == 3


# ══════════════════════════════════════════════════════════════════════════════
# get_maqayis_evidence_ids
# ══════════════════════════════════════════════════════════════════════════════

class TestGetMaqayisEvidenceIds:

    @pytest.fixture(autouse=True)
    def patch_registry(self, monkeypatch):
        path = _make_jsonl(_sample_entries())
        reg = MaqayisRootRegistry(jsonl_path=path)
        monkeypatch.setattr(_reg_mod, "_singleton", reg)
        yield
        os.unlink(path)

    def test_known_dual_root_returns_ids(self):
        ids = get_maqayis_evidence_ids("حد")
        assert len(ids) >= 1
        assert any("DUAL" in i for i in ids)
        assert any("count:2" in i for i in ids)

    def test_known_singular_root(self):
        ids = get_maqayis_evidence_ids("كتب")
        assert any("SINGULAR" in i for i in ids)
        assert any("count:1" in i for i in ids)

    def test_unknown_root_returns_empty(self):
        assert get_maqayis_evidence_ids("خرج") == ()

    def test_empty_string_returns_empty(self):
        assert get_maqayis_evidence_ids("") == ()

    def test_evidence_id_format_primary(self):
        ids = get_maqayis_evidence_ids("حد")
        primary = [i for i in ids if ":origin:" in i]
        assert len(primary) == 1
        assert primary[0].startswith("maqayis:root:حد:origin:DUAL:count:2")

    def test_evidence_id_format_bab(self):
        ids = get_maqayis_evidence_ids("حد")
        bab_ids = [i for i in ids if ":bab:" in i]
        assert len(bab_ids) == 1
        assert "الحاء" in bab_ids[0]

    def test_none_origin_produces_origin_id(self):
        ids = get_maqayis_evidence_ids("دين")
        assert any("NONE" in i for i in ids)

    def test_ids_are_strings(self):
        for i in get_maqayis_evidence_ids("كتب"):
            assert isinstance(i, str)


# ══════════════════════════════════════════════════════════════════════════════
# extract_root_letters_from_bundle (mock bundles)
# ══════════════════════════════════════════════════════════════════════════════

class _FakeRootClaim:
    def __init__(self, letters):
        self.canonical_root = tuple(letters)   # tuple of single chars


class _FakeBundle:
    def __init__(self, root_letters=None):
        self.root_claim = _FakeRootClaim(root_letters) if root_letters is not None else None


class TestExtractRootLettersFromBundle:

    def test_two_letter_root(self):
        assert extract_root_letters_from_bundle(_FakeBundle("حد")) == "حد"

    def test_three_letter_root(self):
        assert extract_root_letters_from_bundle(_FakeBundle("كتب")) == "كتب"

    def test_no_root_claim_returns_none(self):
        assert extract_root_letters_from_bundle(_FakeBundle(None)) is None

    def test_empty_canonical_root_returns_none(self):
        assert extract_root_letters_from_bundle(_FakeBundle("")) is None

    def test_none_canonical_root_attribute(self):
        class BadClaim:
            canonical_root = None
        b = _FakeBundle("حد")
        b.root_claim = BadClaim()
        assert extract_root_letters_from_bundle(b) is None

    def test_bundle_without_root_claim_attr(self):
        class Bare:
            pass
        assert extract_root_letters_from_bundle(Bare()) is None


# ══════════════════════════════════════════════════════════════════════════════
# augment_evidence_from_bundle
# ══════════════════════════════════════════════════════════════════════════════

class TestAugmentEvidenceFromBundle:

    @pytest.fixture(autouse=True)
    def patch_registry(self, monkeypatch):
        path = _make_jsonl(_sample_entries())
        reg = MaqayisRootRegistry(jsonl_path=path)
        monkeypatch.setattr(_reg_mod, "_singleton", reg)
        yield
        os.unlink(path)

    def test_known_root_returns_ids(self):
        assert len(augment_evidence_from_bundle(_FakeBundle("حد"))) >= 1

    def test_unknown_root_returns_empty(self):
        assert augment_evidence_from_bundle(_FakeBundle("خرج")) == ()

    def test_no_root_claim_returns_empty(self):
        assert augment_evidence_from_bundle(_FakeBundle(None)) == ()


# ══════════════════════════════════════════════════════════════════════════════
# Live corpus smoke test (auto-skipped if JSONL absent)
# ══════════════════════════════════════════════════════════════════════════════

_LIVE_JSONL = os.path.join(_HOKOM_ROOT, "data", "maqaees", "full", "root_entries.jsonl")


@pytest.mark.skipif(
    not os.path.exists(_LIVE_JSONL),
    reason="Full corpus not generated yet (run run_full.sh first)",
)
class TestLiveCorpusSmoke:

    @pytest.fixture(scope="class")
    def live_registry(self):
        return MaqayisRootRegistry(jsonl_path=_LIVE_JSONL)

    def test_corpus_loads_at_least_1000_roots(self, live_registry):
        assert live_registry.total_roots >= 1000

    def test_gold_anchor_root(self, live_registry):
        e = live_registry.lookup("حد")
        assert e is not None
        assert e.semantic_origin_type == "DUAL"
        assert e.origin_count == 2

    def test_evidence_ids_for_gold_root(self, live_registry, monkeypatch):
        monkeypatch.setattr(_reg_mod, "_singleton", live_registry)
        ids = get_maqayis_evidence_ids("حد")
        assert any("DUAL" in i for i in ids)

    def test_no_load_error(self, live_registry):
        assert live_registry.load_error is None
