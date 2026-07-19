"""
Residual governance tests — يثبت أن الـ63 residual موثقة وثابتة.
"""
import json, pathlib, pytest

REPORT_PATH   = pathlib.Path('tests/baselines/p5_residuals_manifest.json')
MANIFEST_PATH = pathlib.Path('data/generated/02_mabniyat/mabniyat_examples_manifest.jsonl')

EXPECTED_BLOCKED_BY_P4    = 29
EXPECTED_APPROVED_DEFER   = 34
EXPECTED_TOTAL_RESIDUALS  = 63


def _load_report():
    assert REPORT_PATH.exists(), f"Residuals manifest missing: {REPORT_PATH}"
    return json.loads(REPORT_PATH.read_text(encoding='utf-8'))


def _load_manifest_statuses():
    import json as _json
    statuses = {}
    for line in MANIFEST_PATH.read_text(encoding='utf-8').splitlines():
        if line.strip():
            e = _json.loads(line)
            statuses[e['case_id']] = e['expectation_status']
    return statuses


def test_total_residual_count():
    r = _load_report()
    assert r['total'] == EXPECTED_TOTAL_RESIDUALS, \
        f"Expected {EXPECTED_TOTAL_RESIDUALS} residuals, got {r['total']}"


def test_blocked_by_p4_count():
    r = _load_report()
    count = r['by_status'].get('BLOCKED_BY_P4', 0)
    assert count == EXPECTED_BLOCKED_BY_P4, \
        f"Expected {EXPECTED_BLOCKED_BY_P4} BLOCKED_BY_P4, got {count}"


def test_approved_defer_count():
    r = _load_report()
    count = r['by_status'].get('APPROVED_DEFER', 0)
    assert count == EXPECTED_APPROVED_DEFER, \
        f"Expected {EXPECTED_APPROVED_DEFER} APPROVED_DEFER, got {count}"


def test_every_residual_has_named_reason():
    r = _load_report()
    missing = [item['case_id'] for item in r['residuals'] if not item.get('reason')]
    assert not missing, f"Residuals without named reason: {missing}"


def test_every_residual_has_surface():
    r = _load_report()
    missing = [item['case_id'] for item in r['residuals']
               if not item.get('surface') or item['surface'] == '?']
    bad = [cid for cid in missing
           if next((x for x in r['residuals'] if x['case_id']==cid), {}).get('status') not in
              ('APPROVED_DEFER',)]
    assert not bad, f"Non-DEFER residuals without surface: {bad}"


def test_no_residual_silently_disappeared():
    """يجب أن تكون كل الـresiduals موجودة في manifest."""
    r = _load_report()
    statuses = _load_manifest_statuses()
    missing = [item['case_id'] for item in r['residuals'] if item['case_id'] not in statuses]
    assert not missing, f"Residual case_ids not found in manifest: {missing}"


def test_residual_statuses_match_manifest():
    """كل residual يجب أن تكون حالته في manifest مطابقة."""
    r = _load_report()
    statuses = _load_manifest_statuses()
    ALLOWED_MAP = {
        'BLOCKED_BY_P4':  {'BLOCKED_BY_P4'},
        'APPROVED_DEFER': {'APPROVED_DEFER', 'UNDERLICENSED'},
    }
    mismatches = []
    for item in r['residuals']:
        cid     = item['case_id']
        res_status = item['status']
        mf_status  = statuses.get(cid, 'MISSING')
        allowed = ALLOWED_MAP.get(res_status, {res_status})
        if mf_status not in allowed:
            mismatches.append(f"{cid}: report={res_status}, manifest={mf_status}")
    assert not mismatches, "Residual status mismatches:\n" + "\n".join(mismatches)
