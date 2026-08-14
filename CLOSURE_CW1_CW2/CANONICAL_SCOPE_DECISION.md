# CANONICAL 19-STAGE CLOSURE SCOPE — constitutional decision (owner)

```
CANONICAL_19_STAGE_CLOSURE_SCOPE = LINGUISTIC_STRUCTURAL_JUDGMENT
```
L7 and beyond = linguistic/structural judgment, NOT a fatwa/fiqh engine.
Allowed: `تحرير محل النزاع` (DisputeScope) first · the linguistic claim (الدعوى) ·
licensed linguistic evidence from prior stages · surface conflict (التعارض) ·
جمع/ترجيح ONLY where a pre-licensed *linguistic* rule permits · `TAWAQQUF/DEFER`
when evidence is insufficient · typed sabab/evidence/residuals/lineage.
Forbidden: inventing fiqh/usul theory · issuing shar'i hukm · turning
سبب/شرط/مانع/علة/صحة/فساد/بطلان into a fiqh authority · tafsir/fiqh in the engine.
`GRES_HUKM = AUTHORIZED_OUT_OF_SCOPE`, `GRES_TAFSIR = AUTHORIZED_OUT_OF_SCOPE` — not
a defect blocking linguistic 19-stage closure. Root owner stays
`pipeline/p3_candidate/root_resolution.resolve_root_pipeline` (AUTHORITIES=1). P0–P5
is a closed baseline to build ON, not re-audit.

## Executable findings that reframe RC3/RC4 (with evidence)

**The audit's "P6–P12 FIXTURE_ONLY / judgment theory absent" is CORRECTED.**
A real Hokom-owned 19-stage runtime exists: `src/hokom/canonical/pipeline.py`
`CanonicalPipeline.build().run_sentence(SentenceInput) -> PipelineTrace`.

Verified live (this session):
- `build()` wires all 19 adapters (P0–P8 word-level + P9–P12 sentence-level).
- `run_sentence(["كَتَبَ","الكاتبُ","الرسالةَ"])` reaches **P12_IFADAH_SPEECH_FORCE**
  and returns a typed `ConstitutionalJudgment`.
- That judgment implements the constitutional sequence AS LINGUISTIC/STRUCTURAL:
  `wad, sabab(evidence+confidence), shurut(ShartRequirement), mawani(ManiBlocker),
  illah(IllahRationale+granted_rank), qawadih, athar, baqaya` — matching the scope
  decision (structural, not fiqh).
- **Honest, no silent success:** with empty/garbage evidence → `status = DEFERRED`
  (speech_force='unknown', irab_geometry_present.is_satisfied=False); empty surface
  → ValueError. It DEFERS rather than fabricating a verdict.
- Imports and runs **without maqayis_v2 / word_tree** → the canonical path does NOT
  depend on the RC4 external deps.

Implication: RC3 (judgment runtime) largely EXISTS; RC4 (Wave11/maqayis/word_tree)
is likely OBSOLETE for the canonical path (the AMN L5/L6/L7 kernels are a parallel
implementation; the canonical pipeline is Hokom-owned and self-contained).

## Remaining single closure program (bounded; NOT new theory, NOT from-scratch)
1. **Real end-to-end evidence wiring**: feed production `hokom()` per-word evidence
   into `WordInput.hokom_evidence_by_stage` so the 19-stage judgment runs on REAL
   evidence (today it runs on empty evidence → DEFER). Owner of the bridge: an
   explicit adapter (no new theory).
2. **`تحرير محل النزاع` explicit gate**: the judgment has `wad` first but no explicit
   DisputeScope node — add it as the typed first gate per the scope decision.
3. **Ownership reconciliation**: declare the canonical pipeline the P11/P12
   ifadah/irab/judgment owner; AMN `ifadah_kernel/irab_judgment_kernel/hokom_kernel`
   = COMPARISON/LEGACY. This closes RC4 (deps obsolete) with one contract.
4. **Determinism + clean-clone + regression** for the canonical runtime; connect the
   evidence bridge; then the real P0→P12 chain is live.

This is one integration program with executable evidence of state — not ten gates,
and not the "invent fiqh theory" blocker previously reported (that was dissolved by
both the scope decision AND the discovery that the sequence is already implemented
as linguistic/structural).
