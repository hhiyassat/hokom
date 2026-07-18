# HR2S Root Engine — دليل التكامل

## لماذا لا يُنسخ المحرك؟

محرك الجذر في `hr2s_morphology` يُطبِّق قواعد صرفية دقيقة تشمل الأجوف والناقص واللفيف والمضعف والمهموز وغيرها. نسخ هذا المحرك إلى Hokom سيخلق **نسختين من الحقيقة**: أي تصحيح أو تطوير في HR2S يجب إعادته يدويًا في Hokom، وسيتباعد السلوك والاختبارات تدريجيًا. القرار المعتمد: Hokom يستهلك HR2S بوصفه مكتبة مستقلة.

---

## من يملك قرار الحدود؟

**Hokom يملك قرار فتح مسار الجذر.**

```
Hokom Boundary Layer
→ assess_boundary(surface)
→ RootEligibilityDecision(directive: OPEN | DEFER | BLOCK)
```

- **BLOCK**: الكلمة مُغلقة مبنيًا (مِنْ، هَلْ، فِي ...). HR2S لا يُستدعى.
- **DEFER**: التباس هيكلي أو كلمة وظيفية محتملة (عَلَى، تَقِي). HR2S لا يُستدعى.
- **OPEN**: السطح مرشح هيكليًا للجذر. HR2S يُستدعى.

---

## متى يُستدعى HR2S؟

**فقط عند** `boundary.directive == RootPathDirective.OPEN`.

```python
if boundary.directive is RootPathDirective.BLOCK:
    return _blocked_by_boundary(surface, boundary)   # HR2S not called

if boundary.directive is RootPathDirective.DEFER:
    return _deferred_by_boundary(surface, boundary)  # HR2S not called

# OPEN only:
hr2s_result = engine.analyze_surface(surface)        # called exactly once
```

---

## قاعدة عدم الترقية (Boundary Ceiling)

Hokom boundary هو **السقف الأعلى** — لا يُرفع أبدًا بنتيجة HR2S.

| Hokom boundary | نتيجة HR2S | القرار النهائي |
|----------------|-----------|----------------|
| BLOCK          | أي نتيجة   | **BLOCK**      |
| DEFER          | أي نتيجة   | **DEFER**      |
| OPEN           | ACCEPT    | ACCEPT         |
| OPEN           | DEFER     | DEFER          |
| OPEN           | BLOCK     | BLOCK          |

HR2S **يستطيع خفض** OPEN إلى DEFER أو BLOCK إذا اكتشف مانعًا داخليًا (مثل: صيغة مزيدة مجهولة، أو سطح غير مرخص في منظومته).

```python
def enforce_boundary_ceiling(
    boundary_directive: RootPathDirective,
    hr2s_directive: str,
) -> str:
    if boundary_directive is RootPathDirective.BLOCK: return 'BLOCK'
    if boundary_directive is RootPathDirective.DEFER: return 'DEFER'
    return hr2s_directive  # OPEN: HR2S يملك القرار
```

---

## كيف تتحول نتيجة HR2S إلى Hokom DTO؟

```
engine.analyze_surface(surface)  →  hr2s_result (نموذج HR2S الداخلي)
                                          ↓
                               _project_hr2s_result()
                                          ↓
                              ExternalRootAnalysis (Hokom DTO)
```

`hr2s_result` هو **`MorphologyResult` العام** لـ HR2S. الـ Adapter يستهلك **مرحلة الجذر
فقط**؛ بقايا bab/paradigm/masdar/derivation لا تُخفِّض جذرًا مقبولًا ولا تظهر في الـ DTO.

| المصدر في `MorphologyResult` (public schema) | الحقل في DTO |
|----------------------------------------------|-------------|
| `stage('root').decision.directive` (`Directive` enum → `.value`) | `directive` (بعد السقف) |
| `stage('root').candidates` حيث `kind == 'root'` → `.value.radicals[]` | `canonical_radicals[]` |
| `radical.identity` (أو `None` إذا `?`/غير محلول) | `canonical_radicals[].identity` |
| `radical.surface_form` | `canonical_radicals[].surface_form` |
| `radical.position` (`fa/ayn/lam` → `FA/AYN/LAM`) | `canonical_radicals[].position` |
| `radical.resolved` | `canonical_radicals[].resolved` |
| مرشح `restoration.root_candidates` حسب الموضع | `canonical_radicals[].candidates` |
| `radical.evidence_ids` | `evidence_ids` |
| `trace` مُصفّاة على `surface/boundary/root` | `trace_ids` |
| `residuals` حيث `stage == 'root'` فقط (+ رمز ceiling إذا خُفِّض) | `residual_codes` |
| `root_candidate.profile.to_dict()` | `root_profile` |

قواعد صريحة:
- قراءة القرار عبر `_enum_value(...)` (قيمة الـ Enum)، لا `str(enum)`.
- قيمة قرار غير معروفة، أو غياب مرحلة الجذر، أو `ACCEPT` بجذر غير مكتمل →
  `HR2SProjectionContractError` (لا تحويل صامت إلى `BLOCK`).

**إذا تغيرت بنية HR2S العامة، عدّل `_project_hr2s_result()` فقط. بقية Hokom لا تتأثر.**

---

## ما الذي يحدث عند ACCEPT / DEFER / BLOCK؟

### ACCEPT (المسار OPEN، والجذر أُغلق)
```
canonical_radicals  ← ثلاثة أحرف محلولة (لا UnknownRadical، لا ا/ى)
root_profile        ← مملوء (وزن، بنية، ...)
directive           ← 'ACCEPT'
stage_state         ← 'COMPLETED'
residual_codes      ← ()  (بقايا الجذر فارغة؛ bab/paradigm/... لا تظهر)
```

### DEFER (المسار OPEN، والجذر مؤجَّل)
```
canonical_radicals  ← محفوظة مع UnknownRadical (identity=None, resolved=False)
directive           ← 'DEFER'
stage_state         ← 'DEFERRED'
residual_codes      ← بقايا مرحلة الجذر فقط (سبب التأجيل)
```

### BLOCK (الجذر مُنع كمرشح بعد التشغيل)
```
canonical_radicals  ← ()
directive           ← 'BLOCK'
stage_state         ← 'BLOCKED'
```

### إغلاق الحدود قبل HR2S (لم يُستدعَ المحرك)
```
boundary BLOCK → directive 'BLOCK', stage_state 'NOT_OPENED'
boundary DEFER → directive 'DEFER', stage_state 'NOT_OPENED'
```

**لا يجوز أبدًا**: `canonical_radicals` ممتلئة عند BLOCK، أو `ACCEPT` يحمل `UnknownRadical`.
DEFER **يحفظ** المرشحين وحرف العلة غير المحلول (لا يُفرَّغ).

---

## هوية الهمزة

الهمزة تُحفظ دائمًا كـ `ء` (U+0621) — لا `أ` (U+0623) ولا `إ` (U+0625) ولا غيرها. هذا مبدأ Hokom المطبَّق في التطبيع قبل إرسال السطح إلى HR2S، وتحتفظ به بنية `ExternalRadical.identity`.

---

## كيف تُثبَّت نسخة HR2S؟

### في بيئة التطوير
```bash
pip install -e /path/to/hr2s_morphology
```

### التحقق
```bash
python3 -c "from hr2s import MorphologyEngine; print(MorphologyEngine)"
```

### الاستخدام المعتمد داخل Hokom
```python
from hr2s import MorphologyEngine   # فقط هذا
```

**ممنوع**:
```python
from hr2s.root import ...          # محظور
from hr2s.boundary import ...      # محظور
from hr2s.surface import ...       # محظور
```

### في الإنتاج
- `wheel` أو `git dependency` مُثبَّت على commit/tag محدد.
- `source_version` يُسجَّل في كل نتيجة `ExternalRootAnalysis`.

---

## غياب HR2S

إذا لم تكن `hr2s_morphology` مثبتة:
- BLOCK/DEFER: تعمل بلا استثناء (HR2S لا يُستدعى).
- OPEN: يُرفع `HR2SUnavailableError` مع رسالة واضحة.

**لا fallback** إلى محرك جذر محلي قديم — هذا سيخلق مصدرَين للحقيقة.

---

## حدود المسؤولية

| المسؤولية | Hokom | HR2S |
|-----------|-------|------|
| فتح/إغلاق مسار الجذر | ✓ | — |
| استخراج الجذر | — | ✓ |
| قواعد الأجوف/الناقص/اللفيف | — | ✓ |
| باب / وزن / مصدر | — | ✓ (المستقبل) |
| P4 law | ✓ | — |
| JamidMushtaq | ✓ (R-11) | — |
| تحديد نوع الكلمة المبنية | ✓ | — |
| تسلسل النتائج إلى JSON | ✓ (DTO) | — |

---

## ربط بـ P2/P3 (R-10 لاحقًا)

هذا التكامل يُجهِّز العقد فقط. الربط الفعلي بـ `RootProjection P2` و`RootCandidate P3` يأتي في **R-10** بعد إغلاق R-6 إلى R-9.

```
ExternalRootAnalysis (pipeline/integrations/)
        ↓  [R-10]
RootProjection P2 (pipeline/p2_projection/)
        ↓  [R-10]
RootCandidate P3 (pipeline/p3_candidate/)
```

P3 يستهلك نتيجة HR2S المسقطة ويطبق عقود Hokom فقط (identity/evidence/ceiling). لا يُعيد تحليل السطح.
