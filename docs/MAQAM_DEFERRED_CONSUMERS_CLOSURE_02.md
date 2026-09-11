# MAQAM_DEFERRED_CONSUMERS_CLOSURE_02

**Round:** `MAQAM_DEFERRED_CONSUMERS_AND_CANONICAL_BLOCKER_CLOSURE_02` · **PROJECT_FINISHED = NO**
**No normative ḥukm / manāṭ / tanzīl / final answer. maqām produces no normative output. No commit.**

## Sources
- SOURCE_1 (kept): أصول ودلالات السياق المقامي — صورية جغبوب (33p). Body extraction uncertain.
- SOURCE_2 (added, not replacing): **المقام والقرينة الحالية ودورهما في المعنى — صالحة حاج يعقوب (17p)**.
  Full file not uploaded; owner-quoted excerpt stored + sha256 recorded
  (`docs/MAQAM_THEORY_SOURCE_2_MANIFEST.json`). Excerpt evidence rank = `OWNER_QUOTED`.

## The four deferred consumers — now implemented as measured gates
Each gate emits cause / conditions / preventers / verdict + producer_file + evidence_file
(`ASSERTED_NOT_MEASURED_COUNT = 0`). Applied to the nazila:

### A) MaqamAwareCoreferenceGate  (SOURCE_2#A — ربط/حال/مطابقة)
Supports غائب/مخاطب/متكلم, بارز/مستتر, صاحب الحال, تعدد مرشحين, عدم تعيين, مطابقة شخص/عدد/نوع/تعيين, rank.
On the nazila the pronouns are **NOT** asserted — agreement is not decisive and no discourse/owner
evidence is supplied → `COREFERENCE_DECISION = DEFER`. Explicitly forbidden (not produced):
`ه(معه)=الملك · ه(وارثه)=الملك · ها(طردها)=الأخت · ألف(تحاكما)=الوارث+الأخت`.

### B) MaqamAwareEllipsisGate  (SOURCE_2#B — الحذف بدلالة المقام/الحال)
Separates `ELLIPSIS_CANDIDATE != ELLIPSIS_CERTIFICATE`; requires deletion-cause + context-support +
minimal + no-equal-competing + trace. No maqām/context evidence on the nazila → `DEFER`, no free
reconstruction (`reconstructed_material = NONE_NOT_AUTHORED`).

### C) MaqamAwareRankGate  (SOURCE_2#C — محفوظة/غير محفوظة/لازمة لأمن اللبس)
`RANK_TYPE ∈ {PRESERVED, NON_PRESERVED, CONTEXTUALLY_LOCKED}` + ambiguity flags. Fixtures:
«ضرب موسى عيسى» → CONTEXTUALLY_LOCKED (ambiguity present, order required); «أخي صديقي» →
CONTEXTUALLY_LOCKED; nazila «مَاتَ مَلِكٌ» verb-subject → PRESERVED. Constraints enforced: not every
fronting is rhetoric; not every rank breakable; rank alone does not prove a relation.

### D) MaqamAwareSpeechActGate  (SOURCE_2#D — أسلوب القول/النغمة)
Candidate space (12, extensible) — never a direct certificate. `PUNCTUATION_ONLY != SPEECH_ACT_CERTIFICATE`,
`TEXT_ALONE != ISTIFTA_CERTIFICATE`. On the nazila **text alone → DEFER, no istiftāʾ**
(`TEXT_ALONE_INFERS_ISTIFTA = NO`). With a clearly-marked example context, a
`HYPOTHETICAL_CASE_PRESENTATION` / `ISTIFTA_REQUEST` candidate appears **within the example scope only**
and never becomes an owner decision (`EXAMPLE_CONTEXT_OWNER_RATIFICATION = NO`).

## Canonical integration
`CANONICAL_INTEGRATION_STATUS = BLOCKED_WITH_CAUSE` — see
`docs/MAQAM_CANONICAL_INTEGRATION_BLOCKER_REPORT_02.md`.

## Artifacts / tests
```
output/taaqol_maqam_foundation_generated/MAQAM_{COREFERENCE,ELLIPSIS,RANK,SPEECH_ACT}_GATE_02.json
output/taaqol_maqam_foundation_generated/MAQAM_CANONICAL_BLOCKER_02.json
output/taaqol_maqam_foundation_generated/MAQAM_DEFERRED_CONSUMERS_CLOSURE_02_MATRIX.csv
output/taaqol_maqam_foundation_generated/MAQAM_DEFERRED_CONSUMERS_MANAGER_REPORT_AR_02.html
tests/test_taaqol_maqam_deferred_consumers_02.py
```
