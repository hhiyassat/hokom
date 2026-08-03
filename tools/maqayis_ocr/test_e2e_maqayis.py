#!/usr/bin/env python3
"""
end-to-end smoke test: does maqayis_root_catalog_evidence appear in the
EvidenceContract when we pass a bundle with a known root?

Run from hokom root:
    python3 /tmp/test_e2e_maqayis.py
"""
import sys, os
sys.path.insert(0, os.path.expanduser("~/hokom"))

from pipeline.taaqol_integration.provider_models import HokomLinguisticClaimBundle
from pipeline.taaqol_integration.evidence_adapter import map_evidence

# ── minimal root_claim stub ────────────────────────────────────────────────────
class _FakeRadical:
    def __init__(self, letter): self._l = letter
    def __str__(self): return self._l

class _FakeRootClaim:
    def __init__(self, letters):
        self.canonical_root = tuple(_FakeRadical(c) for c in letters)

# ── build a minimal bundle for root حد ────────────────────────────────────────
bundle = HokomLinguisticClaimBundle(
    claim_id          = "test:حد:001",
    token_id          = "test:001",
    original_surface  = "حدّ",
    normalized_surface= "حد",
    refined_host      = "حد",
    lexical_class     = "VERB",
    part_of_speech    = "VERB",
    root_claim        = _FakeRootClaim("حد"),
    wazn_claim        = None,
    form_claim        = None,
    masdar_claim      = None,
    mushtaq_claims    = (),
    inflection_claim  = None,
    attachment_claims = (),
    domain_directive  = "ACCEPT",
    source_engine     = "HOKOM_ROOT_ENGINE",
    evidence_ids      = ("root:catalog:حد:maqaees",),
    trace_ids         = (),
    active_residuals  = (),
    resolved_residuals= (),
    catalog_versions  = (),
    engine_version    = "test",
)

# ── run evidence mapping ───────────────────────────────────────────────────────
result = map_evidence(bundle)

print(f"\nBundle root : حد")
print(f"Verdict     : {result.verdict}")
print(f"Total recs  : {result.total_count}")
print()

maqayis_recs = [r for r in result.records if r.evidence_type == "maqayis_root_catalog_evidence"]
other_recs   = [r for r in result.records if r.evidence_type != "maqayis_root_catalog_evidence"]

print(f"── Maqayis evidence ({len(maqayis_recs)}) ───────────────────────")
for r in maqayis_recs:
    print(f"  {r.evidence_id}")
    print(f"  content: {r.content}")

print(f"\n── Other evidence ({len(other_recs)}) ──────────────────────────")
for r in other_recs:
    print(f"  [{r.evidence_type}] {r.evidence_id}")

# ── check known root كتب ──────────────────────────────────────────────────────
print("\n\n─── Testing كتب ───────────────────────────────────────────")
bundle2 = HokomLinguisticClaimBundle(
    claim_id="test:كتب:001", token_id="test:002",
    original_surface="كتب", normalized_surface="كتب",
    refined_host="كتب", lexical_class="VERB", part_of_speech="VERB",
    root_claim=_FakeRootClaim("كتب"),
    wazn_claim=None, form_claim=None, masdar_claim=None,
    mushtaq_claims=(), inflection_claim=None, attachment_claims=(),
    domain_directive="ACCEPT", source_engine="HOKOM_ROOT_ENGINE",
    evidence_ids=(), trace_ids=(), active_residuals=(),
    resolved_residuals=(), catalog_versions=(), engine_version="test",
)
r2 = map_evidence(bundle2)
maqayis2 = [r for r in r2.records if r.evidence_type == "maqayis_root_catalog_evidence"]
print(f"Verdict: {r2.verdict}  |  Maqayis records: {len(maqayis2)}")
for r in maqayis2:
    print(f"  {r.evidence_id}")

# ── unknown root ──────────────────────────────────────────────────────────────
print("\n─── Testing unknown root خزق ────────────────────────────────")
bundle3 = HokomLinguisticClaimBundle(
    claim_id="test:خزق:001", token_id="test:003",
    original_surface="خزق", normalized_surface="خزق",
    refined_host="خزق", lexical_class="VERB", part_of_speech="VERB",
    root_claim=_FakeRootClaim("خزق"),
    wazn_claim=None, form_claim=None, masdar_claim=None,
    mushtaq_claims=(), inflection_claim=None, attachment_claims=(),
    domain_directive="ACCEPT", source_engine="HOKOM_ROOT_ENGINE",
    evidence_ids=(), trace_ids=(), active_residuals=(),
    resolved_residuals=(), catalog_versions=(), engine_version="test",
)
r3 = map_evidence(bundle3)
maqayis3 = [r for r in r3.records if r.evidence_type == "maqayis_root_catalog_evidence"]
print(f"Verdict: {r3.verdict}  |  Maqayis records: {len(maqayis3)}  (expected: 0)")

print("\n✓ end-to-end smoke test complete.")
