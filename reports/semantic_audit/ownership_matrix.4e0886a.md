# Post-Segmentation Layer Ownership Matrix
## HEAD: 4e0886a | Date: 2026-07-20

This matrix covers every post-segmentation processing layer, what it owns, what it consumes, what it produces, and known gaps revealed by this audit.

---

## Layer 1: P5 Routing (mabni_projection / operator_catalog)

| Field | Value |
|-------|-------|
| **Owns** | Identifying catalog-protected tokens (operators, haroof, mabni particles); routing token to OPERATOR_BOUNDARY vs. OPEN path |
| **Consumes** | Slot engineering result (verdict=ACCEPT/BLOCK/DEFER); normalized surface |
| **Produces** | `mabni.verdict` (OPERATOR_BOUNDARY / MABNI_BOUNDARY / OPEN / BLOCK); `word_class=HARF` when operator |
| **Correct in audit** | يَا, أَيُّهَا, إِذَا, إِلَى, أَنْ, أَوْ, لَا (standalone), مِنْ, لَمْ, مِنَ, إِلَّا (21 B-class tokens) |
| **Known gaps** | 1. الَّذِينَ/الَّذِي: catalog-protected in segmenter but mabni returns OPEN (catalog split). 2. لَا/إِنْ/إِنَّ/لَيْسَ/كَمَا not in mabni catalog when appearing as post-proclitic hosts. 3. لفظ الجلالة not in protected catalog — inconsistent results across case forms. 4. ذَلِكُمْ اسم إشارة not cataloged. 5. أَلَّا compound particle not recognized. |

---

## Layer 2: Root Admission (pre_root)

| Field | Value |
|-------|-------|
| **Owns** | Deciding whether to open the root path; stripping inflectional prefixes/suffixes before root counting; handling defective/weak radical patterns |
| **Consumes** | `segment_host` (after clitic stripping); morphological path classification |
| **Produces** | `root_candidate.directive` (ACCEPT / DEFER); `root_path_directive`; `residual_codes` |
| **Correct in audit** | أَجَلٍ, كَاتِبٌ, فَرَجُلٌ, شَيْئًا, حَاضِرَةً, أَقْسَطُ, رَبَّهُ (root correct), أجوف simple cases |
| **Known gaps** | 1. مضارع verb prefixes (ي/ت/ن/أ) not stripped → quadriliteral_beyond_scope for all imperfect verbs (13+ tokens). 2. Geminate radicals (shadda) counted as two consonants → quadriliteral for يُمِلَّ، تَضِلَّ، كُلّ (4 tokens). 3. Medial-waw (أجوف) verbs: root_path_not_opened for تَكُون/يَكُون (3 tokens). 4. جمع التكسير patterns not handled → root_path_not_opened for الشُّهَدَاء/الشَّهَادَة (3 tokens). 5. Plural suffix ون/ين/ات not stripped before counting (تَرْضَوْنَ, رِجَالِكُمْ). |

---

## Layer 3: Root Candidate (root_candidate module)

| Field | Value |
|-------|-------|
| **Owns** | Extracting the canonical trilateral/quadriliteral root from the stripped host; assigning `canonical_root`; producing `root_profile` |
| **Consumes** | `pre_root` output (stripped stem); `morphology_path` classification |
| **Produces** | `root_candidate.canonical_root`; `root_candidate.directive`; `final_root` |
| **Correct in audit** | ء-ج-ل (أَجَلٍ/أَجَلِهِ), ك-ت-ب (كَاتِبٌ ×3), ش-ي-ء (شَيْئًا/شَيْءٍ), ح-ض-ر (حَاضِرَةً), ق-س-ط (أَقْسَطُ), ع-ل-م (عَلَّمَهُ), ذ-ك-ر (فَتُذَكِّرَ), ر-ب-ب (رَبَّهُ), ح-ق-ق (الْحَقُّ) |
| **Known gaps** | 1. فَعِيل pattern ي counted as radical → 14+ false quadriliteral deferrals (صَغِير، كَبِير، شَهِيد، ضَعِيف، etc.). 2. Tanwin ن counted as radical → false deferral for بِدَيْنٍ. 3. Medial-waw roots (ق-و-م, د-و-ر, ك-و-ن) not extractable when waw is present. 4. Defective lam-waw roots (د-ن-و) not handled. 5. Plural pattern extensions (رِجَال, فُعَلَاء) not stripped. |

---

## Layer 4: Pattern / Wazn

| Field | Value |
|-------|-------|
| **Owns** | Assigning morphological pattern (وزن) to the host form; distinguishing فَاعِل / فَعِيل / مَفْعُول / مَصْدَر / etc. |
| **Consumes** | `root_candidate`; slot patterns; morphological path |
| **Produces** | `final_wazn`; `word_class_subclass` (ISM_FA3IL, MASDAR, etc.) |
| **Correct in audit** | ISM_FA3IL for أَجَلٍ/فَرَجُلٌ/أَجَلِهِ; LEXICAL_NOUN for كَاتِبٌ/شَيْئًا/حَاضِرَةً; MASDAR for أَقْسَطُ; VERBAL_PAST for كَانَ/يَأْبَ |
| **Known gaps** | 1. MASDAR assigned to verb forms عَلَّمَهُ/يَسْتَطِيعُ/فَتُذَكِّرَ — pattern engine confuses verbal وزن with nominal وزن. 2. VERBAL_PAST assigned to nominal forms الحق/بين/عِند/الأُخْرَى — nominal patterns matching verbal shapes not disambiguated. 3. LEXICAL_NOUN assigned to verb forms تُدِيرُونَهَا/وَلْيُمْلِلِ/وَلْيَتَّقِ. |

---

## Layer 5: Masdar

| Field | Value |
|-------|-------|
| **Owns** | Recognizing مَصْدَر (verbal noun) forms and mapping them to the correct verb root and form |
| **Consumes** | Pattern result; root_candidate |
| **Produces** | `final_masdar`; `final_masdar_pattern` |
| **Correct in audit** | Correctly deferred for most tokens (final_masdar=None is expected when root not extracted) |
| **Known gaps** | Over-triggers for verb forms: عَلَّمَهُ and يَسْتَطِيعُ receive ISM/MASDAR when they are verbs. The MASDAR route fires on verbal patterns, not just nominal مصدر forms. |

---

## Layer 6: Derivatives (mushtaqat)

| Field | Value |
|-------|-------|
| **Owns** | Identifying مُشْتَقَّات (derived forms: اسم فاعل، اسم مفعول، صفة مشبهة، اسم تفضيل، etc.) |
| **Consumes** | `root_candidate`; `final_wazn` |
| **Produces** | `accepted_mushtaqat`; derivative word class subclass |
| **Correct in audit** | ISM_FA3IL correctly assigned to أَجَلٍ/فَرَجُلٌ/أَجَلِهِ (pattern فَاعِل from أ-ج-ل, ر-ج-ل) |
| **Known gaps** | 1. ISM_MAFOOL (مفعول) not assigned to مُسَمًّى (passive participle pattern مُفَعَّل). 2. Elative/comparative (أفعل التفضيل) pattern not always correctly routed (أَدْنَى deferred). 3. اسم تفضيل like أَقْسَطُ gets MASDAR subclass instead of ELATIVE. |

---

## Layer 7: Inflection

| Field | Value |
|-------|-------|
| **Owns** | Assigning inflectional features: person, number, gender, case, mood, tense, voice |
| **Consumes** | `word_class`; `root_candidate`; `final_wazn` |
| **Produces** | `inflectional_form`; `person`; `number`; `gender`; `mood`; `tense_aspect`; `voice` |
| **Correct in audit** | Correctly skipped (inflection_skipped_reason set) for HARF tokens and BLOCKED tokens |
| **Known gaps** | 1. Inflection cannot run on any of the 53 FALSE_DEFER tokens — no downstream inflectional data available. 2. Dual forms (شَهِيدَيْنِ, رَجُلَيْنِ) not recognized by inflection layer. 3. Plural suffix ون (تَرْضَوْنَ) not extracted. 4. All 10 FALSE_BLOCK tokens have no inflectional data. |

---

## Cross-Cutting: Taaqol Bridge

| Field | Value |
|-------|-------|
| **Status** | UNAVAILABLE in this environment (Python 3.10 lacks StrEnum from Python 3.11+) |
| **Impact** | `taaqol_effective_verdict=DEFERRED` for all 129 tokens — not a per-token defect; a runtime constraint |
| **Action** | Run audit on Python 3.11+ to enable Taaqol. No per-token classification change required. |
