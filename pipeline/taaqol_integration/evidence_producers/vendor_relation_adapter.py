"""Hokom → vendor RelationCandidate adapter.

Attempts to construct the exact vendor-native input from a Hokom
RelationCompatibilityCarrier and invoke prove_relation_candidate.

Fail-closed if the vendor input cannot be constructed from the current
Hokom evidence (which is the honest outcome for Ayat al-Dayn under the
current runtime).
"""
from __future__ import annotations

import hashlib
import inspect
import subprocess
import time
from typing import Optional

from .carriers import RelationCompatibilityCarrier, VendorAdapterResult


def _sha256_of_file(p: str) -> str:
    try:
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for c in iter(lambda: f.read(65536), b""):
                h.update(c)
        return h.hexdigest()
    except Exception:
        return ""


def _vendor_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", "vendor/Taaqol-GPT", "rev-parse", "HEAD"],
            text=True, stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "UNKNOWN"


def invoke_native_relation_candidate(
    compatibility_carrier: RelationCompatibilityCarrier,
    contractable_unit_lookup: dict[str, object],
) -> VendorAdapterResult:
    """Invoke vendor prove_relation_candidate.

    Parameters
    ----------
    compatibility_carrier : RelationCompatibilityCarrier
        Hokom compatibility carrier for a source-derived pair.
    contractable_unit_lookup : dict[str, vendor.ContractableUnitGeometry]
        Map of token_id → vendor-native ContractableUnitGeometry instances.

    Returns
    -------
    VendorAdapterResult
        Records native_call_executed, exact input/output types, source path,
        vendor commit, and failure_code if the invocation failed.
    """
    start = time.time()
    result_module = "pipeline.taaqol_integration.evidence_producers.vendor_relation_adapter"
    result_symbol = "invoke_native_relation_candidate"

    # Resolve the two ContractableUnitGeometry instances
    left = contractable_unit_lookup.get(compatibility_carrier.left_contractable_unit_id)
    right = contractable_unit_lookup.get(compatibility_carrier.right_contractable_unit_id)
    if left is None or right is None:
        return VendorAdapterResult(
            adapter_module=result_module, adapter_symbol=result_symbol,
            native_module="taaqqul_slot_geometry.weight.relation_candidate",
            native_symbol="prove_relation_candidate",
            native_source_path="", native_source_sha256="",
            vendor_commit=_vendor_commit(),
            exact_input_type="ContractableUnitGeometry",
            exact_output_type="RelationVerdict",
            native_call_executed=False,
            duration_ms=(time.time() - start) * 1000,
            failure_code="MISSING_NATIVE_CONTRACTABLE_UNIT",
            provenance_ids=compatibility_carrier.provenance_ids,
            trace_ids=compatibility_carrier.trace_ids + (
                f"ADAPTER::invoke_native_relation_candidate::MISSING_CU",
            ),
        )

    # Attempt to import the vendor callable
    try:
        from taaqqul_slot_geometry.weight.relation_candidate import prove_relation_candidate
        native_source_path = inspect.getfile(prove_relation_candidate)
    except Exception as e:
        return VendorAdapterResult(
            adapter_module=result_module, adapter_symbol=result_symbol,
            native_module="taaqqul_slot_geometry.weight.relation_candidate",
            native_symbol="prove_relation_candidate",
            native_source_path="", native_source_sha256="",
            vendor_commit=_vendor_commit(),
            exact_input_type="ContractableUnitGeometry",
            exact_output_type="RelationVerdict",
            native_call_executed=False,
            duration_ms=(time.time() - start) * 1000,
            failure_code=f"VENDOR_IMPORT_FAILED::{type(e).__name__}::{e}",
            provenance_ids=compatibility_carrier.provenance_ids,
            trace_ids=compatibility_carrier.trace_ids + (
                f"ADAPTER::invoke_native_relation_candidate::IMPORT_FAILED",
            ),
        )

    native_source_sha256 = _sha256_of_file(native_source_path)

    # Invoke the vendor law
    try:
        native_output = prove_relation_candidate(left)
        exact_output_type = type(native_output).__name__
        return VendorAdapterResult(
            adapter_module=result_module, adapter_symbol=result_symbol,
            native_module="taaqqul_slot_geometry.weight.relation_candidate",
            native_symbol="prove_relation_candidate",
            native_source_path=native_source_path,
            native_source_sha256=native_source_sha256,
            vendor_commit=_vendor_commit(),
            exact_input_type=type(left).__name__,
            exact_output_type=exact_output_type,
            native_call_executed=True,
            duration_ms=(time.time() - start) * 1000,
            native_output=native_output,
            failure_code=None,
            provenance_ids=compatibility_carrier.provenance_ids + (
                f"VENDOR::{_vendor_commit()[:12]}",
            ),
            trace_ids=compatibility_carrier.trace_ids + (
                f"ADAPTER::invoke_native_relation_candidate::EXECUTED",
            ),
        )
    except Exception as e:
        return VendorAdapterResult(
            adapter_module=result_module, adapter_symbol=result_symbol,
            native_module="taaqqul_slot_geometry.weight.relation_candidate",
            native_symbol="prove_relation_candidate",
            native_source_path=native_source_path,
            native_source_sha256=native_source_sha256,
            vendor_commit=_vendor_commit(),
            exact_input_type=type(left).__name__,
            exact_output_type="RelationVerdict",
            native_call_executed=False,
            duration_ms=(time.time() - start) * 1000,
            failure_code=f"VENDOR_CALL_FAILED::{type(e).__name__}::{e}",
            provenance_ids=compatibility_carrier.provenance_ids,
            trace_ids=compatibility_carrier.trace_ids + (
                f"ADAPTER::invoke_native_relation_candidate::CALL_FAILED",
            ),
        )
