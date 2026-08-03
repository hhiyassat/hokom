from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any

class CapabilityStatus(str, Enum):
    PROVIDED = "PROVIDED"
    DEFERRED = "DEFERRED"
    BLOCKED = "BLOCKED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    AMBIGUOUS = "AMBIGUOUS"

@dataclass(frozen=True)
class CapabilityResult:
    capability_id: str
    status: CapabilityStatus
    value: Optional[Any]          # The actual typed value
    value_ar: Optional[str]       # Arabic label
    value_en: Optional[str]       # English label
    evidence_ids: tuple[str, ...]
    residuals: tuple[str, ...]
    source_module: str

    def is_provided(self) -> bool:
        return self.status == CapabilityStatus.PROVIDED

    def is_deferred(self) -> bool:
        return self.status == CapabilityStatus.DEFERRED
