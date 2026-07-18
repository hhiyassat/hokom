#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
relation_contract.py — P5 Contract Declaration Layer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

القاعدة المعمارية:
  P5 هي طبقة إعلان العقد — لا طبقة استنتاج نحوي.
  P5 تُجيب فقط على: "ما العقد الذي فتحه هذا الرمز؟"
  P5 لا تُجيب على:  "كيف سيُستوفى هذا العقد؟"

ما تُعلنه P5 (مسموح):
  contract_id    — معرِّف مستقر مربوط بالهوية المعجمية للعامل (= operator_id)
  contract_state — حالة العقد (OPEN دائمًا من P5)

ما لا يظهر في P5 (ممنوع):
  kind | expects | effect | governs | case | mood | role | grammar_profile
  — هذه تنتمي إلى طبقات التراخيص البنيوية اللاحقة

RelationContract(contract_id, contract_state):
  contract_id    — مثل: INNA | LAM | KAY | WA | LA | MIN …
                   يُشتق من operator_id في operator_id_map.py
  contract_state — 'OPEN' دائمًا من P5 (العقد مفتوح، لم يُستوفَ بعد)
"""

from __future__ import annotations
from dataclasses import dataclass


# ══════════════════════════════════════════════════════════════════════════════
# هيكل العقد
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class RelationContract:
    """
    عقد العلاقة الذي يفتحه حرف/أداة مبنية.

    contract_id    : = operator_id — معرِّف معجمي مستقر
    contract_state : 'OPEN' — العقد منعقد ولم يُستوفَ بعد

    لا يوجد حقل kind أو expects أو أي توقع نحوي.
    التوقعات البنيوية تعمل على مستوى طبقات لاحقة (HR2S فصاعدًا).
    """
    contract_id:    str   # = operator_id (INNA / LAM / KAY / …)
    contract_state: str   # دائمًا 'OPEN' من P5


# ══════════════════════════════════════════════════════════════════════════════
# دالة الإنشاء
# ══════════════════════════════════════════════════════════════════════════════

def make_contract(operator_id: str) -> RelationContract:
    """
    أنشئ عقد علاقة مفتوحًا للعامل المحدد.

    Parameters:
      operator_id — المعرِّف المعجمي المستقر (من operator_id_map.get_profile)

    Returns:
      RelationContract(contract_id=operator_id, contract_state='OPEN')
    """
    return RelationContract(
        contract_id    = operator_id,
        contract_state = 'OPEN',
    )
