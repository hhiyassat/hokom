# هياكل السجلات الثلاثة عشر (الجولة 34 — هياكل فقط)

**status = SKELETON_ONLY_NOT_POPULATED لكلٍّ.** الهيكل ليس سجلًّا مأهولًا، ولا يُنشئ واقعة/مصدر/تصديقًا/حكمًا/تنزيلًا/جوابًا.

## `factual_claim_registry` — سجل الدعاوى الواقعية
- الغرض: يسجّل الوقائع المزعومة كدعاوى تحتاج تزويدًا وتصديقًا، لا كوقائع مثبتة.
- allowed_record_types: FACTUAL_CLAIM_CANDIDATE · min_fields: claim_id, claim_text, source_ref, owner_ratification
- owner_ratification_required = YES · gate_dependencies: owner_supplied_fact_registry، owner_ratification_registry
- creates_fact/source/hukm/tanzil/final_answer = NO · default_if_empty = DEFER · expansion_blocker_if_empty = YES
## `owner_supplied_fact_registry` — سجل الوقائع المزوَّدة من المالك
- الغرض: يستقبل وقائع يزوّدها المالك مع بينة؛ هو الوحيد الذي قد يُنشئ واقعة بعد التصديق.
- allowed_record_types: OWNER_SUPPLIED_FACT · min_fields: fact_id, fact_text, evidence_ref, owner_ratification
- owner_ratification_required = YES · gate_dependencies: owner_ratification_registry
- creates_fact/source/hukm/tanzil/final_answer = NO · default_if_empty = DEFER · expansion_blocker_if_empty = YES
## `source_requirement_registry` — سجل متطلبات المصادر
- الغرض: يسجّل نوع المصدر المطلوب لكل بُعد؛ لا يُنشئ مصدرًا.
- allowed_record_types: SOURCE_REQUIREMENT · min_fields: req_id, required_source_type, linked_requirement
- owner_ratification_required = YES · gate_dependencies: normative_source_registry
- creates_fact/source/hukm/tanzil/final_answer = NO · default_if_empty = DEFER · expansion_blocker_if_empty = YES
## `normative_source_registry` — سجل المصادر المعيارية
- الغرض: يسجّل المصادر المصدَّقة من المالك (مثل المولودة في الجولات 17/21)؛ لا يُصدّق من الوكيل.
- allowed_record_types: OWNER_RATIFIED_SOURCE · min_fields: source_id, authority, evidence, owner_ratification
- owner_ratification_required = YES · gate_dependencies: owner_ratification_registry
- creates_fact/source/hukm/tanzil/final_answer = NO · default_if_empty = DEFER · expansion_blocker_if_empty = YES
## `domain_candidate_registry` — سجل مرشحات المجال
- الغرض: يسجّل مرشحات المجال (الجولة 13) دون إغلاق نهائي.
- allowed_record_types: DOMAIN_CANDIDATE · min_fields: domain_candidate_id, is_final_closed_domain
- owner_ratification_required = NO · gate_dependencies: —
- creates_fact/source/hukm/tanzil/final_answer = NO · default_if_empty = DEFER · expansion_blocker_if_empty = YES
## `hukm_candidate_registry` — سجل مرشحات الحكم
- الغرض: يسجّل مرشحات الحكم (الجولة 23) كمرشحات فقط.
- allowed_record_types: HUKM_CANDIDATE · min_fields: hukm_candidate_id, verdict, final_hukm_allowed
- owner_ratification_required = NO · gate_dependencies: normative_source_registry
- creates_fact/source/hukm/tanzil/final_answer = NO · default_if_empty = DEFER · expansion_blocker_if_empty = YES
## `manat_candidate_registry` — سجل مرشحات المناط
- الغرض: يسجّل مرشحات المناط (الجولة 24) كمرشحات فقط.
- allowed_record_types: MANAT_CANDIDATE · min_fields: manat_candidate_id, verdict, final_manat_allowed
- owner_ratification_required = NO · gate_dependencies: hukm_candidate_registry
- creates_fact/source/hukm/tanzil/final_answer = NO · default_if_empty = DEFER · expansion_blocker_if_empty = YES
## `tanzil_requirement_registry` — سجل متطلبات التنزيل
- الغرض: يسجّل شروط التنزيل المطلوبة قبل أي تنزيل؛ لا يُنتج تنزيلًا.
- allowed_record_types: TANZIL_REQUIREMENT · min_fields: req_id, condition, owner_ratification
- owner_ratification_required = YES · gate_dependencies: manat_candidate_registry، owner_ratification_registry
- creates_fact/source/hukm/tanzil/final_answer = NO · default_if_empty = DEFER · expansion_blocker_if_empty = YES
## `proof_burden_registry` — سجل عبء الإثبات
- الغرض: يسجّل بوابات البينة/اليمين؛ لا يقرّر الحق الموضوعي.
- allowed_record_types: PROOF_BURDEN_GATE · min_fields: gate_id, claimant, evidence_ref
- owner_ratification_required = YES · gate_dependencies: factual_claim_registry
- creates_fact/source/hukm/tanzil/final_answer = NO · default_if_empty = DEFER · expansion_blocker_if_empty = YES
## `possession_yad_registry` — سجل الحيازة/اليد
- الغرض: يسجّل حالة اليد/الحيازة والقرائن؛ الحيازة ليست ملكية نهائية.
- allowed_record_types: POSSESSION_YAD_STATE · min_fields: state_id, hand_credible, qarina_ref
- owner_ratification_required = YES · gate_dependencies: factual_claim_registry
- creates_fact/source/hukm/tanzil/final_answer = NO · default_if_empty = DEFER · expansion_blocker_if_empty = YES
## `inheritance_condition_registry` — سجل شروط الإرث
- الغرض: يسجّل شروط الكلالة/حصر الورثة كشروط تحتاج إثباتًا.
- allowed_record_types: INHERITANCE_CONDITION · min_fields: condition_id, condition_text, evidence_ref
- owner_ratification_required = YES · gate_dependencies: owner_supplied_fact_registry
- creates_fact/source/hukm/tanzil/final_answer = NO · default_if_empty = DEFER · expansion_blocker_if_empty = YES
## `residual_registry` — سجل البقايا
- الغرض: يسجّل البقايا غير المحسومة عبر الجولات.
- allowed_record_types: RESIDUAL · min_fields: residual_id, residual_text, blocking
- owner_ratification_required = NO · gate_dependencies: —
- creates_fact/source/hukm/tanzil/final_answer = NO · default_if_empty = DEFER · expansion_blocker_if_empty = YES
## `owner_ratification_registry` — سجل تصديقات المالك
- الغرض: يسجّل تصديقات المالك الصريحة؛ لا يُنشئ تصديقًا من الوكيل.
- allowed_record_types: OWNER_RATIFICATION · min_fields: ratification_id, subject, decision, scope
- owner_ratification_required = YES · gate_dependencies: —
- creates_fact/source/hukm/tanzil/final_answer = NO · default_if_empty = DEFER · expansion_blocker_if_empty = YES

---
*لا يجوز اعتبار أي هيكل مأهولًا حتى تُضاف سجلات مصدَّقة من المالك.*
