#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
transitions.py — آلة الحالات للمقاطع الصوتية العربية

مفردات: C  V  VV
حالات:
  S1  بعد C الأولى      → V أو VV فقط
  S2  بعد V أو VV       → C فقط
  S3  بعد C غير الأولى  → C (نهاية) أو V أو VV
"""

# ── آلة الحالات ───────────────────────────────────────────────────────────
#
#            ┌─────────────────────────────┐
#   START    │                             │
#     │      ▼        V/VV                 │
#     C ──► S1 ──────────────► S2          │
#            │                  │          │
#           (C forbidden)       C          │
#                               │          │
#                               ▼          │
#                              S3 ─── V/VV─┘
#                               │
#                               C  (word end only)
#                               │
#                              END

# None = ممنوع
TRANSITIONS = {
    'S1': {'C': None,  'V': 'S2', 'VV': 'S2'},
    'S2': {'C': 'S3',  'V': None, 'VV': None},
    'S3': {'C': 'END', 'V': 'S2', 'VV': 'S2'},
}

# حالات القبول (يجوز وقف الكلمة عندها)
ACCEPT = {'S2', 'S3', 'END'}


# ── توليد الكلمات ─────────────────────────────────────────────────────────

def generate(max_len: int = 8) -> dict[int, list[str]]:
    """
    أنتِج جميع الكلمات الممكنة حتى طول max_len.
    كل كلمة تبدأ بـ C ثم تسير وفق آلة الحالات.
    """
    results: dict[int, list[str]] = {}

    # (تسلسل, الحالة الحالية)
    queue = [(['C'], 'S1')]   # نبدأ دائمًا بـ C وننتقل إلى S1

    while queue:
        seq, state = queue.pop()

        # إذا حالة قبول → سجِّل الكلمة
        if state in ACCEPT:
            length = len(seq)
            word   = ''.join(seq)
            results.setdefault(length, [])
            if word not in results[length]:
                results[length].append(word)

        # إذا بلغ الحد الأقصى → لا توسيع
        if len(seq) >= max_len:
            continue

        # وسِّع بكل انتقال ممكن
        if state in TRANSITIONS:
            for token, next_state in TRANSITIONS[state].items():
                if next_state is None:
                    continue           # ممنوع
                if next_state == 'END':
                    # C في الآخر: أضف وأوقف
                    word = ''.join(seq) + token
                    length = len(seq) + 1
                    results.setdefault(length, [])
                    if word not in results[length]:
                        results[length].append(word)
                else:
                    queue.append((seq + [token], next_state))

    return dict(sorted(results.items()))


# ── العرض ─────────────────────────────────────────────────────────────────

def show():
    print('\n' + '═' * 55)
    print('  آلة الحالات')
    print('═' * 55)
    print(f"  {'الحالة':<8} {'C':^14} {'V':^14} {'VV':^14}")
    print('  ' + '─' * 50)
    labels = {'S2': '✓', 'S3': '✓', 'END': '✓ (نهاية)', None: '✗'}
    for state, row in TRANSITIONS.items():
        cells = [labels.get(row[t], '?') for t in ('C', 'V', 'VV')]
        print(f"  {state:<8} {cells[0]:^14} {cells[1]:^14} {cells[2]:^14}")

    print('\n  البداية: C إلزامية → S1')
    print('  حالات القبول: S2  S3  END')

    words = generate(8)
    total = sum(len(v) for v in words.values())

    print('\n' + '═' * 55)
    print(f'  الكلمات الممكنة (حتى 8 وحدات) — الإجمالي: {total}')
    print('═' * 55)
    for length, pats in words.items():
        pats_sorted = sorted(pats)
        print(f'\n  [{length} وحدات] ({len(pats_sorted)}):')
        print('  ' + '   '.join(pats_sorted))
    print()


if __name__ == '__main__':
    show()
