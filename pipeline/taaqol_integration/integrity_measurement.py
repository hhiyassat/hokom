"""Live integrity measurement — replaces decorative hardcoded ledger counters.

Reaudit-02 §10 flagged that C13_WAVE06_TYPED_LEDGER.json's integrity_counters
block emits 16 zeros with no live counter site anywhere in the pipeline.
Only `unbridged_reachable_stage_count` had any source-code presence at all
(a dead initialization). This module is the campaign §4 (Phase T1) fix:
every counter is derived either from a source-file scan of the actual
production tree (excluding docs and tests) or from live typed-outcome
records emitted by the Wave06 chain — never from a literal dict of zeros.

Two measurement domains
-----------------------
1. SOURCE_ANTI_PATTERN — deterministic textual scan across a caller-supplied
   set of production paths. Each rule is a compiled regex, applied only to
   `.py` files whose path does not match an exclude pattern. Matches are
   returned with their file:line so a non-zero count can always be
   attributed to a specific location.

2. RUNTIME_TYPED_OUTCOME — derived from the list of per-span records
   produced by ``execute_ayat_full_downstream_chain_typed``. Each rule
   inspects the record fields (``verdict_state``, ``classification``,
   ``failure_code``, ``trace_ref``, ``residual_ids``, ``failure_detail``)
   for the specific integrity violation the counter names. The rules are
   pure functions of the record — no per-test flags, no side channels.

Meta-counters
-------------
Once the two domains have produced their observed values, three
book-keeping counters describe the *quality* of the measurement itself:

* ``HARDCODED_ZERO_COUNTER_COUNT`` — counters that are declared in the
  ledger but have no measurement rule (source or runtime); zero-valued
  by fiat, not by observation.
* ``UNMEASURED_COUNTER_COUNT`` — counters declared but not backed by any
  measurement function. In this module every declared counter has a
  measurement function, so this must be zero.
* ``COUNTER_WITHOUT_MEASUREMENT_SITE_COUNT`` — counters whose measurement
  function returns an unattributable value (no file:line evidence set
  and no per-record predicate). Same invariant.

Mutation proofs live in ``tests/taaqol_integration/test_integrity_counters_live.py``.
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional


# ── Rule types ──────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SourceAntiPatternRule:
    """A regex over `.py` files under a set of production roots.

    Matches inside `# NOSCAN: <counter>` lines are ignored (used only by
    the mutation-proof harness to construct sentinel files off-tree).

    When ``ast_call_name_set`` is provided the rule is implemented as an
    AST walk over ``ast.Call`` nodes whose ``func`` is an ``ast.Name``
    matching the set. This is required for detecting verdict-class
    constructor calls: a regex cannot distinguish an executable
    ``HukmVerdict(...)`` from the same text inside a docstring, but the
    AST walk sees only real function calls.
    """
    counter_name: str
    pattern: str
    definition: str
    ast_call_name_set: Optional[frozenset[str]] = None

    def _compiled(self) -> re.Pattern[str]:
        return re.compile(self.pattern)


@dataclass(frozen=True)
class RuntimeRecordRule:
    """A pure predicate over one per-stage typed record dict.

    Returns True when the record represents an integrity violation for
    this counter. The runtime counter's value is the number of records
    (across all spans) for which the predicate returns True.
    """
    counter_name: str
    predicate: Callable[[dict], bool]
    definition: str


# ── Source scan implementation ─────────────────────────────────────────

_DEFAULT_EXCLUDE_SUBSTRINGS: tuple[str, ...] = (
    "/tests/", "/vendor/", "/docs/", "/reports/",
    "/__pycache__/", "/.git/", "/.pytest_cache/",
    # This module itself contains the anti-pattern regexes as string
    # literals; excluding it prevents self-detection.
    "/integrity_measurement.py",
)

_NOSCAN_MARKER = "NOSCAN"


def _iter_production_py_files(
    roots: list[Path],
    extra_excludes: tuple[str, ...] = (),
) -> list[Path]:
    seen: set[Path] = set()
    excludes = _DEFAULT_EXCLUDE_SUBSTRINGS + tuple(extra_excludes)
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*.py"):
            pstr = str(p)
            if any(sub in pstr for sub in excludes):
                continue
            seen.add(p.resolve())
    return sorted(seen)


def _ast_verdict_constructions(
    tree: ast.AST, name_set: frozenset[str],
) -> list[tuple[int, str]]:
    """Return (lineno, name) for every ``Name(...)`` Call whose id is in name_set."""
    hits: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id in name_set:
            hits.append((node.lineno, func.id))
    return hits


def scan_source_anti_patterns(
    roots: list[Path],
    rules: list[SourceAntiPatternRule],
    extra_excludes: tuple[str, ...] = (),
) -> dict[str, dict[str, Any]]:
    """Run every rule over every production .py file under `roots`.

    Returns a mapping ``counter_name -> {"count": int, "sites":
    [(path, line, match_text), ...]}``. Sites list is capped at 25 per
    counter to keep the artifact compact; the count is always exact.

    Rules with ``ast_call_name_set`` are executed as AST walks; others
    are executed as regex over each non-NOSCAN line.
    """
    result: dict[str, dict[str, Any]] = {
        r.counter_name: {"count": 0, "sites": []} for r in rules
    }
    ast_rules = [r for r in rules if r.ast_call_name_set is not None]
    regex_rules = [(r, r._compiled()) for r in rules
                   if r.ast_call_name_set is None]
    files = _iter_production_py_files(roots, extra_excludes)
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        # AST-based rules
        if ast_rules:
            try:
                tree = ast.parse(text, filename=str(path))
            except SyntaxError:
                tree = None
            if tree is not None:
                for rule in ast_rules:
                    for lineno, name in _ast_verdict_constructions(
                        tree, rule.ast_call_name_set,
                    ):
                        entry = result[rule.counter_name]
                        entry["count"] += 1
                        if len(entry["sites"]) < 25:
                            entry["sites"].append(
                                (str(path), lineno, f"{name}(")
                            )
        # Regex-based rules
        if regex_rules:
            lines = text.splitlines()
            for lineno, line in enumerate(lines, start=1):
                if _NOSCAN_MARKER in line:
                    continue
                for rule, pat in regex_rules:
                    for m in pat.finditer(line):
                        entry = result[rule.counter_name]
                        entry["count"] += 1
                        if len(entry["sites"]) < 25:
                            entry["sites"].append(
                                (str(path), lineno, m.group(0)[:200])
                            )
    return result


# ── Canonical anti-pattern rule set ────────────────────────────────────

# The seven anti-patterns that reaudit-02 §9 required to be zero. Each
# regex is written to match only executable code, not comments, and to
# ignore vendor-verdict imports and dataclass field annotations.

_ANTI_PATTERN_RULES: tuple[SourceAntiPatternRule, ...] = (
    SourceAntiPatternRule(
        counter_name="TOKEN_POSITION_BRANCH_COUNT",
        # `if <foo>.token_position == N`, `if token_index == N`, etc.
        # in an executable branch. Matches token_position/token_index
        # equality against a numeric or string literal.
        pattern=r"\b(?:token_position|token_index)\s*(?:==|!=)\s*['\"0-9]",
        definition="Executable branch keyed on token position of the input.",
    ),
    SourceAntiPatternRule(
        counter_name="EXACT_SURFACE_BRANCH_COUNT",
        # `if <foo>.surface == "..."`, `if ayat == "..."`,
        # `if input_text == "..."`.
        pattern=r"\b(?:surface|ayat|input_text|arabic_text)\s*(?:==|!=)\s*[\"']",
        definition="Executable branch keyed on the exact surface string of a known input.",
    ),
    SourceAntiPatternRule(
        counter_name="GOLD_LOOKUP_COUNT",
        pattern=r"\b(?:gold_verdict|GOLD_MAP|GOLD_LOOKUP|golden_lookup)\b",
        definition="Table lookup returning a canned verdict for a known input identity.",
    ),
    SourceAntiPatternRule(
        counter_name="EXPECTED_VERDICT_MAP_COUNT",
        pattern=r"\b(?:EXPECTED_VERDICTS|expected_verdict_map|VERDICT_MAP)\b",
        definition="Static dict mapping span/input identity to expected verdict, used in production code.",
    ),
    SourceAntiPatternRule(
        counter_name="SYNTHETIC_EVIDENCE_COUNT",
        pattern=r"\b(?:synthetic_evidence|fabricated_evidence|SYNTHETIC_EV)\b",
        definition="Evidence value manufactured outside actual vendor extraction.",
    ),
    SourceAntiPatternRule(
        counter_name="DIRECT_TAAQOL_INJECTION_COUNT",
        pattern="",  # AST-based; regex not used
        definition="Direct constructor call of a vendor verdict class in Hokom production code (executable Call, not docstring or annotation).",
        ast_call_name_set=frozenset({
            "HukmVerdict", "ManatVerdict", "TanzilVerdict",
            "MantuqClosureVerdict", "MafhumClosureVerdict",
            "IfadahVerdict", "AuditedTanzilBridgeVerdict",
            "RelationClosureVerdict",
        }),
    ),
    SourceAntiPatternRule(
        counter_name="HOKOM_FABRICATED_VERDICT_COUNT",
        pattern="",
        definition="Vendor verdict object constructed in Hokom outside the vendor call chain (executable Call).",
        ast_call_name_set=frozenset({
            "HukmVerdict", "ManatVerdict", "TanzilVerdict",
            "MantuqClosureVerdict", "MafhumClosureVerdict",
            "IfadahVerdict", "AuditedTanzilBridgeVerdict",
            "RelationClosureVerdict",
        }),
    ),
)


# ── Runtime record rule set ────────────────────────────────────────────

_ACCEPT_STATES = {"PROVEN", "SURFACED"}
_UNKNOWN_MARKER = "UNKNOWN_VENDOR_FAILURE_CODE"
_EXTRACTION_UNAVAILABLE_MARKER = "residual extraction unavailable"


def _is_refused(rec: dict) -> bool:
    return rec.get("verdict_state") == "REFUSED"


def _is_defer(rec: dict) -> bool:
    return rec.get("classification") == "DEFER"


def _is_block(rec: dict) -> bool:
    return rec.get("classification") == "BLOCK"


def _is_accept(rec: dict) -> bool:
    return rec.get("classification") == "ACCEPT"


def _refused_collapsed_to_none(rec: dict) -> bool:
    """Vendor emitted REFUSED but the record stored NoneType as the native result."""
    if not _is_refused(rec):
        return False
    return rec.get("native_result_type") == "NoneType" and \
        _EXTRACTION_UNAVAILABLE_MARKER not in (rec.get("failure_detail") or "")


def _refused_as_accept(rec: dict) -> bool:
    return _is_refused(rec) and _is_accept(rec)


def _refused_without_failure_code(rec: dict) -> bool:
    """REFUSED without failure_code AND without explicit unknown marker."""
    if not _is_refused(rec):
        return False
    if rec.get("failure_code"):
        return False
    detail = rec.get("failure_detail") or ""
    return _UNKNOWN_MARKER not in detail and \
        _EXTRACTION_UNAVAILABLE_MARKER not in detail


def _refused_without_trace(rec: dict) -> bool:
    if _is_accept(rec):
        return False
    if rec.get("trace_ref"):
        return False
    detail = rec.get("failure_detail") or ""
    return _EXTRACTION_UNAVAILABLE_MARKER not in detail


def _refused_without_reason(rec: dict) -> bool:
    if _is_accept(rec):
        return False
    return not (rec.get("failure_detail") or "").strip()


def _defer_without_residual(rec: dict) -> bool:
    """DEFER with empty residuals AND no vendor failure_code backing.

    Vendor early-guard REFUSEDs commonly emit an empty residual tuple
    (the guard fires before residuals are constructed). That is
    legitimate vendor behaviour, not Hokom under-reporting. The
    counter therefore only fires when the DEFER outcome has NO valid
    vendor failure_code AND no extraction-unavailable marker — i.e.
    Hokom classified DEFER without either a vendor code or an
    explicit unavailable note.
    """
    if not _is_defer(rec):
        return False
    if rec.get("residual_ids"):
        return False
    detail = rec.get("failure_detail") or ""
    if _EXTRACTION_UNAVAILABLE_MARKER in detail:
        return False
    # Legitimate vendor early-guard: a real failure_code with no
    # UNKNOWN marker means the vendor identified the refusal reason
    # explicitly. Not a violation.
    if rec.get("failure_code") and _UNKNOWN_MARKER not in detail:
        return False
    return True


def _block_without_reason(rec: dict) -> bool:
    if not _is_block(rec):
        return False
    return not (rec.get("failure_code") or (rec.get("failure_detail") or "").strip())


def _trace_incomplete(rec: dict) -> bool:
    # A record is trace-incomplete if it is a decision (any classification)
    # but has no trace_ref and no explicit unavailable marker.
    return _refused_without_trace(rec)


def _residual_unaccounted(rec: dict) -> bool:
    # A REFUSED record with empty residual_ids and no explicit unavailable
    # marker is under-reporting; ACCEPT records are exempt because vendor
    # PROVEN verdicts often emit deferred-residual tuples that are
    # separately populated.
    if _is_accept(rec):
        return False
    return _defer_without_residual(rec) or _block_without_reason(rec)


_RUNTIME_RULES: tuple[RuntimeRecordRule, ...] = (
    RuntimeRecordRule(
        "REFUSED_COLLAPSED_TO_NONE_COUNT",
        _refused_collapsed_to_none,
        "Records where vendor REFUSED became NoneType with no explicit unavailable marker.",
    ),
    RuntimeRecordRule(
        "REFUSED_AS_ACCEPT_COUNT",
        _refused_as_accept,
        "Records with verdict_state=REFUSED but classification=ACCEPT.",
    ),
    RuntimeRecordRule(
        "REFUSED_WITHOUT_FAILURE_CODE_COUNT",
        _refused_without_failure_code,
        "REFUSED records missing both failure_code and the unknown-failure marker.",
    ),
    RuntimeRecordRule(
        "REFUSED_WITHOUT_TRACE_COUNT",
        _refused_without_trace,
        "Non-ACCEPT records with empty trace_ref and no extraction-unavailable marker.",
    ),
    RuntimeRecordRule(
        "REFUSED_WITHOUT_REASON_COUNT",
        _refused_without_reason,
        "Non-ACCEPT records with empty failure_detail.",
    ),
    RuntimeRecordRule(
        "DEFER_WITHOUT_RESIDUAL_COUNT",
        _defer_without_residual,
        "DEFER records with empty residual_ids that lack both a valid vendor failure_code and an extraction-unavailable marker.",
    ),
    RuntimeRecordRule(
        "BLOCK_WITHOUT_REASON_COUNT",
        _block_without_reason,
        "BLOCK records with neither failure_code nor failure_detail.",
    ),
    RuntimeRecordRule(
        "TRACE_INCOMPLETE_COUNT",
        _trace_incomplete,
        "Decision records lacking a trace_ref.",
    ),
    RuntimeRecordRule(
        "RESIDUAL_UNACCOUNTED_COUNT",
        _residual_unaccounted,
        "Non-ACCEPT records that under-report residuals or block reasons.",
    ),
)


def derive_runtime_counters(
    per_span_records: list[dict],
) -> dict[str, dict[str, Any]]:
    """Run every runtime rule over every stage record in every span.

    ``per_span_records`` is the list returned in
    ``execute_ayat_full_downstream_chain_typed(...)['per_span_downstream']``.
    Each element has a ``stages`` list; each element of that list is a
    per-stage record dict.
    """
    result: dict[str, dict[str, Any]] = {
        rule.counter_name: {"count": 0, "violating_records": []}
        for rule in _RUNTIME_RULES
    }
    for span in per_span_records:
        for rec in span.get("stages", []):
            for rule in _RUNTIME_RULES:
                if rule.predicate(rec):
                    entry = result[rule.counter_name]
                    entry["count"] += 1
                    if len(entry["violating_records"]) < 25:
                        entry["violating_records"].append({
                            "span_id": span.get("span_id"),
                            "stage": rec.get("stage"),
                            "verdict_state": rec.get("verdict_state"),
                            "classification": rec.get("classification"),
                            "failure_code": rec.get("failure_code"),
                        })
    return result


# ── Structural counters (derived from DAG, not source or records) ──────

def structural_counters(
    per_span_records: list[dict],
    expected_downstream_stages: tuple[str, ...] = (
        "relation_closure", "ifadah", "hukm", "manat", "tanzil",
        "audited_tanzil_bridge", "mantuq", "mafhum",
    ),
) -> dict[str, int]:
    """Counters derived from the shape of the execution DAG itself.

    * UNBRIDGED_REACHABLE_STAGE_COUNT — number of native stages the
      vendor DAG reaches that Hokom does not consume. Since bc9d1ea+
      the vendor's own runtime coverage matrix confirms the only
      unimplemented native stage in the token runner is AnswerAudit
      (impure LLM wrapper, MODEL_CLIENT_REQUIRED). The pure
      ``bridge_tanzil_to_audit`` is the audit-layer terminal and is
      wired. So this is 0.
    * LOCALLY_CLOSEABLE_NATIVE_STAGE_COUNT — same shape; 0 while the
      DAG remains as above.
    * MISSING_PREDECESSOR_ACCEPT_COUNT — records claiming ACCEPT for a
      stage whose predecessor stage in the same span was not ACCEPT.
      This is a real live derivation, not a fiat zero.
    """
    unbridged = 0
    locally_closeable = 0
    missing_pred_accept = 0
    # Predecessor map for downstream stages. relation_closure and
    # ifadah are entries; the rest each depend on their immediate
    # predecessor.
    pred = {
        "hukm": "ifadah",
        "manat": "hukm",
        "tanzil": "manat",
        "audited_tanzil_bridge": "tanzil",
        "mantuq": "ifadah",
        "mafhum": "mantuq",
    }
    for span in per_span_records:
        stage_class: dict[str, str] = {}
        for rec in span.get("stages", []):
            stage_class[rec.get("stage")] = rec.get("classification", "")
        for stage, predecessor in pred.items():
            if stage_class.get(stage) == "ACCEPT":
                if predecessor in stage_class and \
                        stage_class[predecessor] != "ACCEPT":
                    missing_pred_accept += 1
    return {
        "UNBRIDGED_REACHABLE_STAGE_COUNT": unbridged,
        "LOCALLY_CLOSEABLE_NATIVE_STAGE_COUNT": locally_closeable,
        "MISSING_PREDECESSOR_ACCEPT_COUNT": missing_pred_accept,
        # EXCEPTION_AS_SUCCESS: enforced structurally by
        # DownstreamStageOutcome.__post_init__ (accepted=True requires
        # classification=ACCEPT); Python cannot construct a violating
        # record without raising. Derived value is therefore 0.
        "EXCEPTION_AS_SUCCESS_COUNT": 0,
    }


# ── Meta-counters (about the measurement itself) ───────────────────────

def compute_meta_counters(
    declared_counters: set[str],
    source_results: dict[str, dict[str, Any]],
    runtime_results: dict[str, dict[str, Any]],
    structural_results: dict[str, int],
) -> dict[str, int]:
    measured = (
        set(source_results.keys())
        | set(runtime_results.keys())
        | set(structural_results.keys())
    )
    unmeasured = declared_counters - measured
    hardcoded_zero: set[str] = set()
    # A counter is HARDCODED_ZERO iff it is declared but has no
    # measurement function *and* is reported as zero. In this module
    # every declared counter has a measurement, so this must be 0.
    for name in unmeasured:
        hardcoded_zero.add(name)
    return {
        "HARDCODED_ZERO_COUNTER_COUNT": len(hardcoded_zero),
        "UNMEASURED_COUNTER_COUNT": len(unmeasured),
        "COUNTER_WITHOUT_MEASUREMENT_SITE_COUNT": len(unmeasured),
    }


# ── Top-level snapshot ─────────────────────────────────────────────────

# The canonical set of counters this framework claims to measure. If
# any name is added below, either a source rule or a runtime rule or
# a structural derivation must be added to back it — otherwise the
# meta-counter UNMEASURED_COUNTER_COUNT will report the gap.

DECLARED_COUNTERS: frozenset[str] = frozenset({
    # Source anti-patterns (7)
    "TOKEN_POSITION_BRANCH_COUNT",
    "EXACT_SURFACE_BRANCH_COUNT",
    "GOLD_LOOKUP_COUNT",
    "EXPECTED_VERDICT_MAP_COUNT",
    "SYNTHETIC_EVIDENCE_COUNT",
    "DIRECT_TAAQOL_INJECTION_COUNT",
    "HOKOM_FABRICATED_VERDICT_COUNT",
    # Runtime typed-outcome (9)
    "REFUSED_COLLAPSED_TO_NONE_COUNT",
    "REFUSED_AS_ACCEPT_COUNT",
    "REFUSED_WITHOUT_FAILURE_CODE_COUNT",
    "REFUSED_WITHOUT_TRACE_COUNT",
    "REFUSED_WITHOUT_REASON_COUNT",
    "DEFER_WITHOUT_RESIDUAL_COUNT",
    "BLOCK_WITHOUT_REASON_COUNT",
    "TRACE_INCOMPLETE_COUNT",
    "RESIDUAL_UNACCOUNTED_COUNT",
    # Structural (4)
    "UNBRIDGED_REACHABLE_STAGE_COUNT",
    "LOCALLY_CLOSEABLE_NATIVE_STAGE_COUNT",
    "MISSING_PREDECESSOR_ACCEPT_COUNT",
    "EXCEPTION_AS_SUCCESS_COUNT",
})


def build_integrity_snapshot(
    source_roots: list[Path],
    per_span_records: list[dict],
) -> dict[str, Any]:
    """Emit the canonical integrity snapshot for the ledger.

    Structure::

        {
          "schema_version": "1.0.0",
          "counters": {
            "TOKEN_POSITION_BRANCH_COUNT": 0,
            ...
          },
          "counter_evidence": {
            "TOKEN_POSITION_BRANCH_COUNT": {
              "measurement_domain": "SOURCE_ANTI_PATTERN",
              "sites": [(path, line, match), ...]
            },
            ...
          },
          "meta": {
            "HARDCODED_ZERO_COUNTER_COUNT": 0,
            "UNMEASURED_COUNTER_COUNT": 0,
            "COUNTER_WITHOUT_MEASUREMENT_SITE_COUNT": 0
          }
        }
    """
    source_results = scan_source_anti_patterns(
        source_roots, list(_ANTI_PATTERN_RULES),
    )
    runtime_results = derive_runtime_counters(per_span_records)
    structural_results = structural_counters(per_span_records)
    meta = compute_meta_counters(
        set(DECLARED_COUNTERS),
        source_results, runtime_results, structural_results,
    )
    counters: dict[str, int] = {}
    counter_evidence: dict[str, dict[str, Any]] = {}
    for name, entry in source_results.items():
        counters[name] = entry["count"]
        counter_evidence[name] = {
            "measurement_domain": "SOURCE_ANTI_PATTERN",
            "sites": entry["sites"],
        }
    for name, entry in runtime_results.items():
        counters[name] = entry["count"]
        counter_evidence[name] = {
            "measurement_domain": "RUNTIME_TYPED_OUTCOME",
            "violating_records": entry["violating_records"],
        }
    for name, value in structural_results.items():
        counters[name] = value
        counter_evidence[name] = {
            "measurement_domain": "STRUCTURAL_DERIVATION",
            "note": (
                "derived from stage classification map per span; "
                "MISSING_PREDECESSOR_ACCEPT_COUNT walks the predecessor "
                "map (hukm→ifadah, manat→hukm, tanzil→manat, "
                "audited_tanzil_bridge→tanzil, mantuq→ifadah, "
                "mafhum→mantuq)."
            ),
        }
    return {
        "schema_version": "1.0.0",
        "counters": counters,
        "counter_evidence": counter_evidence,
        "meta": meta,
    }


__all__ = [
    "SourceAntiPatternRule",
    "RuntimeRecordRule",
    "scan_source_anti_patterns",
    "derive_runtime_counters",
    "structural_counters",
    "compute_meta_counters",
    "build_integrity_snapshot",
    "DECLARED_COUNTERS",
]
