"""
RC-A proofs: a REAL native cross-token government (عامل/معمول) vertical.

The jar→majrur family (حرف الجر → الاسم المجرور) is detected from the canonical
mabniyat catalog (a linguistic knowledge base — the closed class of حروف الجر —
NOT the ayat_al_dayn gold oracle). It produces genuine sentence-level government
evidence that drives the canonical P8→P12 chain to a POSITIVE certified vertical,
while a no-preposition control DEFERs honestly (no fabricated government).

Success (owner criterion): REAL_NATIVE_CROSS_TOKEN_GOVERNMENT_CERTIFICATE_COUNT > 0
AND complete accounting (unexplained == 0), NOT a guessed CERTIFIED.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PKG = os.path.dirname(_HERE)
_HOKOM = os.path.dirname(_PKG)
for p in (_HOKOM, os.path.join(_HOKOM, "src"), _PKG):
    if p not in sys.path:
        sys.path.insert(0, p)

from hokom_pipeline import hokom                                            # noqa: E402
from hokom.canonical.pipeline import CanonicalPipeline, SentenceInput, WordInput  # noqa: E402
from canonical_bridge.bridge import bridge_word_evidence, build_dispute_scope     # noqa: E402
from canonical_bridge.government_producer import produce_government, is_preposition  # noqa: E402
from canonical_bridge.certificates import build_certificate_chain            # noqa: E402

_P = CanonicalPipeline.build()


def _vertical(tokens):
    gov = produce_government(tokens)
    per = [hokom(t) for t in tokens]
    words = []
    for i, (t, hk) in enumerate(zip(tokens, per)):
        ev = bridge_word_evidence(hk)
        ev.update(gov["word_evidence"].get(i, {}))
        words.append(WordInput(surface=t, hokom_evidence_by_stage=ev, word_index=i))
    ds = build_dispute_scope(" ".join(tokens), per).to_dict()
    tr = _P.run_sentence(SentenceInput(words=tuple(words),
                                       sentence_hokom_evidence=gov["sentence_evidence"]))
    return build_certificate_chain(tr, ds, government_evidence=gov)


def test_preposition_detection_is_from_closed_class():
    # real حروف الجر
    for prep in ("إِلَىٰ", "عَلَى", "فِي", "مِنْ", "عَنْ", "بِ"):
        assert is_preposition(prep), prep
    # non-prepositions must not be detected
    for non in ("كَتَبَ", "الْكَاتِبُ", "أَجَلٍ", "الْأَرْضِ"):
        assert not is_preposition(non), non


def test_positive_cross_token_government_vertical_certifies():
    r = _vertical(["إِلَىٰ", "أَجَلٍ"])          # jar → majrur (ilā ajalin)
    assert r["real_native_cross_token_government_certificate_count"] >= 1
    assert r["government_relations"] == ["jar_majrur:jar_w0->majrur_w1"]
    p8 = next(c for c in r["certificates"] if c["layer_id"] == "P8_AMIL_MAMUL")
    assert p8["verdict"] == "CERTIFIED"
    # government evidence is the real relation, not an empty placeholder
    assert any("jar_majrur" in e for e in p8["evidence_ids"])
    acc = r["accounting"]
    assert acc["unexplained"] == 0
    assert acc["certified"] >= 3          # at least P8/P9/P10 certify
    assert r["ancestry_certificate"]["no_jump_failures"] == 0
    assert r["res_ancestry_01"] == "CLOSED"


def test_no_jump_holds_on_certified_chain():
    r = _vertical(["عَلَى", "الْأَرْضِ"])
    for c in r["certificates"]:
        assert c["no_jump_verified"] is True
    # every certified successor has a permitting (certified/NA) predecessor
    verds = {c["layer_id"]: c["verdict"] for c in r["certificates"]}
    assert verds["P8_AMIL_MAMUL"] == "CERTIFIED"
    assert verds["P9_SENTENCE_GEOMETRY"] == "CERTIFIED"


def test_negative_control_defers_without_fabrication():
    r = _vertical(["كَتَبَ", "الْكَاتِبُ"])       # no حرف جر → no government
    assert r["real_native_cross_token_government_certificate_count"] == 0
    assert r["government_relations"] == []
    verds = {c["layer_id"]: c["verdict"] for c in r["certificates"]}
    assert verds["P8_AMIL_MAMUL"] == "NOT_APPLICABLE"
    assert verds["P9_SENTENCE_GEOMETRY"] == "DEFER"
    assert r["accounting"]["unexplained"] == 0      # still fully accounted for
    assert r["res_ancestry_01"] == "CLOSED"


def test_producer_never_reads_gold_oracle():
    """No IMPORT of / CALL to the gold oracle (docstring may name it to forbid it)."""
    import canonical_bridge.government_producer as gp
    code_lines = [ln for ln in open(gp.__file__, encoding="utf-8").read().splitlines()
                  if (ln.lstrip().startswith(("import ", "from "))
                      or "build_gold_relations(" in ln)]
    for ln in code_lines:
        assert "ayat_al_dayn" not in ln, ln
        assert "build_gold_relations" not in ln, ln
