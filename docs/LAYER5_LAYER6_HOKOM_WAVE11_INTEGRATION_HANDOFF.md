# Handoff: LAYER 5 + LAYER 6 — Integration into Hokom Wave11
**تسليم: دمج الطبقة الخامسة والسادسة في خط معالجة Hokom Wave11**

---

## 1. ما الذي اكتمل

| الطبقة | الاسم | الحالة | الاختبارات |
|--------|-------|--------|------------|
| LAYER 5 | IfadahKernel | ✅ FROZEN | 18/18 pass |
| LAYER 6 | IrabJudgmentKernel | ✅ FROZEN | 13/13 pass |

التوكن الختمي لـ LAYER 5:
```
IFADAH_KERNEL_LAYER5_FROZEN_READY_FOR_LAYER6_HANDOFF
```
التوكن الختمي لـ LAYER 6:
```
IRAB_JUDGMENT_KERNEL_LAYER6_BUILT_READY_FOR_HOKOM_HANDOFF
```

---

## 2. الملفات المنشورة

**المستودع:** `arabic-mother-language-net`
**الفرع:** `main`
**المسار المحلي:** `/Users/husseinhiyassat/Downloads/arabic-mother-language-net/`

```
arabic-mother-language-net/
├── ifadah_types.py           ← LAYER 5 — أنواع البيانات (SentenceType, IsnadType,
│                                          FilledSlot, IfadahResult, Layer6Handoff)
├── ifadah_kernel.py          ← LAYER 5 — دالة ifadah_build() [نقطة الدخول]
├── irab_types.py             ← LAYER 6 — أنواع البيانات (IrabEntry, IrabJudgmentResult,
│                                          IrabRole, IrabCase, IrabSign)
├── irab_judgment_kernel.py   ← LAYER 6 — دالة irab_judge() [نقطة الدخول]
└── tests/
    └── test_irab_judgment_kernel.py   ← 13 اختبار تغطي الحراس + الأمثلة
```

---

## 3. سلسلة البيانات الكاملة

```
wave11_build(words, synset_id, db_path)
        ↓
  Wave11Ancestry                         ← LAYERS 0–4 (موجود الآن في hokom)
        ↓
  ifadah_build(anc, synset_id, context)  ← LAYER 5 (الجديد)
        ↓
  IfadahResult
    .jumlah_fi3liyya  — الجملة الفعلية
    .jumlah_ismiyya   — الجملة الاسمية
    .jumlah_wasfiyya  — العبارة الوصفية
    .musnad           — المسند (الفعل أو الخبر)
    .musnad_ilayh     — المسند إليه (الفاعل أو المبتدأ)
    .qayd             — القيود (مفعول، جار مجرور، حال...)
    .is_frozen        — True إذا جاهز للـ handoff
        ↓
  result.to_layer6_handoff()             ← بناء حزمة Layer6Handoff
        ↓
  irab_judge(handoff)                    ← LAYER 6 (الجديد)
        ↓
  IrabJudgmentResult
    .entries[]        — قائمة IrabEntry لكل كلمة في الجملة
    .verdict          — "IRAB_COMPLETE" | "BLOCKED"
    .is_complete      — True إذا تم الإعراب كاملاً
    .layer6_frozen    — توكن الختم
```

---

## 4. واجهة برمجية: حالة إعراب كل كلمة

```python
# كل IrabEntry في result.entries يحتوي:
entry.word          # الكلمة في الجملة
entry.position      # موضعها (0-based)
entry.irab_role     # "فعل" | "فاعل" | "مفعول به" | "مبتدأ" | "خبر" | "قيد-جار" | ...
entry.irab_case     # "مرفوع" | "منصوب" | "مجرور" | "مبني"
entry.irab_sign     # "ضمة" | "فتحة" | "كسرة" | "سكون"
entry.irab_reason   # السبب: "فاعل مرفوع بالضمة", "مفعول به منصوب بالفتحة"...
entry.muttasil      # للجار المجرور: الاسم المجرور
```

---

## 5. نقطة الدمج في Hokom

### 5.1 أين تقع نقطة الدمج

في `hokom/wave11_ancestry.py` — الدالة `wave11_build()` تُنتج `Wave11Ancestry`.
الطبقتان الجديدتان تأتيان **مباشرة بعدها** في خط المعالجة، قبل الوصول إلى `hokm`.

```
wave11_build()   → Wave11Ancestry.hokm = "OPEN"  ← نقطة الدمج هنا
                        ↓
                   ifadah_build()  [LAYER 5]
                        ↓
                   irab_judge()   [LAYER 6]
                        ↓
                   IrabJudgmentResult.verdict = "IRAB_COMPLETE"
```

### 5.2 الإعداد: sys.path

`hokom/wave11_ancestry.py` يُضيف `/Users/husseinhiyassat/` إلى `sys.path` ثم يستورد
كـ `from word_tree.*`. لذلك إضافة LAYER 5+6 في hokom تتطلب نمطاً واحداً من اثنين:

**النمط أ — إضافة مسار مباشر (أبسط، مباشر):**
```python
import sys, os
_AMN_REPO = "/Users/husseinhiyassat/Downloads/arabic-mother-language-net"
if _AMN_REPO not in sys.path:
    sys.path.insert(0, _AMN_REPO)

from ifadah_types import SentenceType, IsnadType, FilledSlot, IfadahResult, Layer6Handoff
from ifadah_kernel import ifadah_build
from irab_types import IrabJudgmentResult
from irab_judgment_kernel import irab_judge
```

**النمط ب — symlink (إذا أردت الاستمرار مع بنية `word_tree.*`):**
```bash
# في /Users/husseinhiyassat/ — نفذ مرة واحدة
ln -s Downloads/arabic-mother-language-net word_tree
```
ثم hokom يستورد طبيعياً:
```python
from word_tree.ifadah_types import ...
from word_tree.ifadah_kernel import ifadah_build
from word_tree.irab_types import ...
from word_tree.irab_judgment_kernel import irab_judge
```

---

## 6. كود الدمج الكامل

```python
# hokom/scripts/integrate_layer5_layer6.py  (مثال)

import sys, os

# ── مسار مستودع arabic-mother-language-net ──────────────────────────────
_AMN_REPO = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "..", "Downloads", "arabic-mother-language-net"
)
_AMN_REPO = os.path.normpath(_AMN_REPO)
if _AMN_REPO not in sys.path:
    sys.path.insert(0, _AMN_REPO)

from ifadah_kernel       import ifadah_build
from irab_judgment_kernel import irab_judge


def run_full_pipeline(anc, synset_id: str, context: dict = None):
    """
    تشغيل LAYER 5 + LAYER 6 على Wave11Ancestry جاهزة.

    Parameters
    ----------
    anc        : Wave11Ancestry  — مخرج wave11_build()
    synset_id  : str             — معرِّف المجموعة
    context    : dict | None     — {اسم_الفتحة: قيمة} لتخصيص الفتحات

    Returns
    -------
    dict مع مفاتيح:
        ifadah   — IfadahResult
        irab     — IrabJudgmentResult | None
        verdict  — "IRAB_COMPLETE" | "BLOCKED" | "IFADAH_BLOCKED"
    """
    # ── LAYER 5 ─────────────────────────────────────────────────────────
    ifadah = ifadah_build(anc, synset_id, context)

    if not ifadah.is_frozen:
        return {
            "ifadah":  ifadah,
            "irab":    None,
            "verdict": "IFADAH_BLOCKED",
            "reasons": ifadah.block_reasons,
        }

    # ── LAYER 6 ─────────────────────────────────────────────────────────
    handoff = ifadah.to_layer6_handoff()
    irab    = irab_judge(handoff)

    return {
        "ifadah":  ifadah,
        "irab":    irab,
        "verdict": irab.verdict,
        "entries": [e.to_dict() for e in irab.entries] if irab.is_complete else [],
        "reasons": irab.block_reasons,
    }
```

---

## 7. مثال تشغيلي كامل

```python
# بعد wave11_build() في pipeline hokom:

from wave11_ancestry import wave11_build

anc = wave11_build(
    words=["كَتَبَ", "الكاتبُ", "الرسالةَ"],
    synset_id="library.n.01",
    db_path="/path/to/data/pilot_roots.json"
)

result = run_full_pipeline(anc, synset_id="library.n.01")

if result["verdict"] == "IRAB_COMPLETE":
    for e in result["irab"].entries:
        print(f"  {e.word:<20} {e.irab_role:<12} {e.irab_case} ({e.irab_sign})")
        print(f"  └─ {e.irab_reason}")
```

**المخرج المتوقع:**
```
  كَتَبَ               فعل         مبني (سكون)
  └─ فعل ماضٍ مبني على الفتح
  الكاتبُ              فاعل        مرفوع (ضمة)
  └─ فاعل مرفوع وعلامة رفعه الضمة
  الرسالةَ             مفعول به    منصوب (فتحة)
  └─ مفعول به منصوب وعلامة نصبه الفتحة
```

---

## 8. الحراس والشروط

### LAYER 5 يُعيد `ifadah.is_frozen = False` إذا:
| الحارس | الشرط |
|--------|-------|
| GUARD_00 | الجذر غير موثَّق في مقاييس اللغة (`anc.root_verified = False`) |
| GUARD_01 | مسند فارغ |
| GUARD_02 | مسند إليه فارغ |
| GUARD_03 | جملة فعلية بلا فاعل |
| GUARD_04 | جملة اسمية بلا خبر أو بلا مبتدأ |

### LAYER 6 يُعيد `verdict = "BLOCKED"` إذا:
| الحارس | الشرط |
|--------|-------|
| GUARD_L6_00 | layer5_frozen token غير صحيح |
| GUARD_L6_01 | raw_sentence فارغة |
| GUARD_L6_02 | musnad فارغ |
| GUARD_L6_03 | musnad_ilayh فارغ |
| GUARD_L6_04 | جملة فعلية بلا فاعل |
| GUARD_L6_05 | جملة اسمية بلا خبر |
| GUARD_L6_06 | لا يمكن إنتاج إعراب |

---

## 9. القواعد الإعرابية الست (LAYER 6)

| القاعدة | المحل | الحالة | العلامة |
|---------|-------|--------|---------|
| A — الفعل | فعل ماضٍ | مبني على الفتح | — |
| A — الفعل | فعل مضارع | مرفوع | ضمة |
| B — الفاعل | musnad_ilayh في الفعلية | مرفوع | ضمة |
| C — المفعول به | qayd[0] إذا لم يبدأ بحرف جر | منصوب | فتحة |
| D — المبتدأ | musnad_ilayh في الاسمية | مرفوع | ضمة |
| E — الخبر | musnad في الاسمية | مرفوع | ضمة |
| F — الجار والمجرور | qayd يبدأ بـ في/على/عن/من/إلى/ب/لـ | مجرور | كسرة |

---

## 10. ما يجب عدم لمسه

هذه الملفات والفروع محمية دستورياً — لا تُعدَّل ولا تُدمج ولا تُعاد كتابة:

```
❌  closure/hokom-taaqol-final-production-01  (C13)
❌  feature/constitutional-genus-property-semantics-01-2a6af17  (CGPS01)
❌  vendor/Taaqol-GPT
❌  scripts/canonical_gate.py  (لا يُشغَّل)
❌  مستودع C13 canonical artifacts أو execution ledger
```

LAYER 5 + LAYER 6 لا يتقاطعان مع أي من هذه المناطق. هما يعملان فقط **بعد**
`wave11_build()` وقبل أي حكم فقهي أو تفسيري.

---

## 11. تحقق سريع

```bash
cd /Users/husseinhiyassat/Downloads/arabic-mother-language-net

# LAYER 6 — 13 اختبار
python -m pytest tests/test_irab_judgment_kernel.py -v

# التحقق من التسلسل الكامل
python - <<'EOF'
import sys; sys.path.insert(0, '.')
from ifadah_types import Layer6Handoff, SentenceType, IsnadType
from irab_judgment_kernel import irab_judge

h = Layer6Handoff(
    root="كتب", synset_id="library.n.01",
    sentence_type=SentenceType.FI3LIYYA, isnad_type=IsnadType.HAQIQI,
    musnad="كَتَبَ", musnad_ilayh="الكاتبُ",
    qayd=("الرسالةَ",), raw_sentence="كَتَبَ الكاتبُ الرسالةَ",
)
r = irab_judge(h)
print(r.verdict)           # IRAB_COMPLETE
print(r.layer6_frozen)     # IRAB_JUDGMENT_KERNEL_LAYER6_BUILT_READY_FOR_HOKOM_HANDOFF
for e in r.entries:
    print(f"  {e.word} | {e.irab_role} | {e.irab_case} | {e.irab_sign}")
EOF
```

---

## 12. الخطوة التالية الطبيعية

الطبقتان LAYER 5+6 مُغلَقتان (FROZEN). الخطوة التالية الموصى بها:

**LAYER 7 — HokomJudgmentKernel**: يستقبل `IrabJudgmentResult` ويُصدر
حكماً على مستوى الجملة المفيدة (إعرابياً/دلالياً) — بالاعتماد على ما أنجزه LAYER 6
وبدون إعادة فتح أي طبقة سابقة.

---

*تاريخ التسليم: 2026-08-13*
*الحالة: LAYER 5 FROZEN ✅ — LAYER 6 FROZEN ✅ — جاهز للدمج*
