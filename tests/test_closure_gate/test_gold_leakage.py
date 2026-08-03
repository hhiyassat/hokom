"""
test_gold_leakage.py — Prove production code does not read gold expected outputs.

CONSTITUTIONAL RULE: Production engines must not read expected clause boundaries,
relation labels, Ifadah, Hukm, or verdicts from any gold corpus file at runtime.
Gold data must only exist in tests/evaluation/ and tests/*.
"""
from __future__ import annotations
import importlib
import os, sys
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

PRODUCTION_MODULES = [
    "pipeline.clause_graph.segmenter",
    "pipeline.relation_graph.models",
    "pipeline.semantic_providers.dal_provider",
    "pipeline.semantic_providers.madlul_provider",
    "pipeline.vertical_chain.chain",
    "pipeline.vertical_chain.models",
    "pipeline.capability_providers.cap_word_class",
    "pipeline.capability_providers.cap_morphology",
    "pipeline.capability_providers.cap_syntax",
    "pipeline.execution_ledger.ledger",
    "pipeline.execution_ledger.scope",
]

FORBIDDEN_GOLD_IMPORTS = [
    "tests.evaluation",
    "tests.evaluation.ayat_al_dayn_gold_corpus",
    "GOLD_CLAUSES",
    "GOLD_RELATIONS",
    "gold_clauses",
    "gold_relations",
    "AYAT_AL_DAYN_GOLD_CLAUSES",
    "AYAT_AL_DAYN_GOLD_RELATIONS",
]


def test_production_segmenter_no_gold_import():
    """pipeline.clause_graph.segmenter must NOT import from gold corpus."""
    import pipeline.clause_graph.segmenter as seg
    import inspect
    src = inspect.getsource(seg)
    for forbidden in ["AYAT_AL_DAYN_GOLD_CLAUSES", "GOLD_CLAUSES", "tests.evaluation"]:
        assert forbidden not in src, (
            f"GOLD_LEAKAGE: production segmenter imports/references '{forbidden}'"
        )


def test_production_segmenter_is_generic():
    """Generic segmenter must not hardcode specific Ayat token indices."""
    import pipeline.clause_graph.segmenter as seg
    import inspect
    src = inspect.getsource(seg)
    # Should not contain hard-coded Ayat clause surfaces
    AYAT_SURFACES = ["فَاكْتُبُوهُ", "وَاسْتَشْهِدُوا", "AD-C0"]
    for surface in AYAT_SURFACES:
        assert surface not in src, (
            f"HARDCODED_CLAUSE_OUTPUT: segmenter contains Ayat-specific surface '{surface}'"
        )


def test_production_relation_graph_no_hardcoded_relations():
    """Production relation graph models must not hard-code specific relation assignments."""
    import pipeline.relation_graph.models as rm
    import inspect
    src = inspect.getsource(rm)
    for surface in ["كَاتِبٌ", "شَهِيدَيْنِ", "AD-R0"]:
        assert surface not in src, (
            f"HARDCODED_RELATION_OUTPUT: relation models contain Ayat-specific data '{surface}'"
        )


def test_vertical_chain_no_gold_expectations():
    """Vertical chain must not read expected Ifadah/Hukm from gold corpus."""
    import pipeline.vertical_chain.chain as ch
    import inspect
    src = inspect.getsource(ch)
    for forbidden in ["GOLD_", "gold_", "expected_ifadah", "expected_hukm", "AD-C0", "AD-R0"]:
        assert forbidden not in src, (
            f"GOLD_LEAKAGE in vertical_chain.chain: '{forbidden}'"
        )


def test_production_modules_importable_without_gold():
    """All production modules must import cleanly without touching gold corpus."""
    for mod_path in PRODUCTION_MODULES:
        try:
            mod = importlib.import_module(mod_path)
            assert mod is not None, f"Module {mod_path} returned None"
        except ImportError as e:
            assert False, f"Production module {mod_path} failed to import: {e}"


def test_gold_corpus_in_evaluation_dir():
    """Gold corpus must only exist in tests/evaluation/, not in pipeline/."""
    import importlib.util
    spec = importlib.util.find_spec("tests.evaluation.ayat_al_dayn_gold_corpus")
    assert spec is not None, "Gold corpus must exist at tests/evaluation/ayat_al_dayn_gold_corpus"
    # Must NOT exist in pipeline/
    no_pipeline_spec = importlib.util.find_spec("pipeline.clause_graph.ayat_al_dayn_gold_corpus")
    assert no_pipeline_spec is None, (
        "GOLD_LEAKAGE: gold corpus found in pipeline/ — must be in tests/evaluation/ only"
    )
