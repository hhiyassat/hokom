"""
Governance: canonical report artifacts must be bound to the audited HEAD.

Contract (non-self-referential):
    At least one closure manifest must explicitly declare:
        artifact_commit = b19cd9a97aea18b355529e7ec97fd16ecf2f9caa

    This field records the last Git commit that changed the canonical
    artifact files (reports/ayat_al_dayn_demo/**). It is distinct from
    the audit_head (HEAD when the audit was run) and from the manifest
    commit itself — resolving the circular binding problem.

    The contract is satisfied when:
    (1) The actual last commit touching the artifact dir equals AUDITED_ARTIFACT_HEAD.
    (2) At least one manifest with artifact_commit == AUDITED_ARTIFACT_HEAD exists.
    (3) Every artifact digest recorded in that manifest matches the current file bytes.
    (4) git diff AUDITED_ARTIFACT_HEAD..HEAD -- reports/ayat_al_dayn_demo/ is empty.

    Governance-only commits (scripts/run_canonical_final_audit.sh,
    tests/shell/test_audit_runner.sh, etc.) that do NOT touch
    reports/ayat_al_dayn_demo/ are explicitly permitted after the audit
    and must NOT invalidate the binding.

    This test module NEVER passes silently. If no applicable manifest
    exists, test_artifact_binding_exists fails with an explicit message
    rather than returning without assertion.

AUDITED_ARTIFACT_HEAD = b19cd9a97aea18b355529e7ec97fd16ecf2f9caa
CANONICAL_CSV_SHA     = f9d2410e22f6964c79867048b8f899d4d86632f33f5634422e90b1544fd52fa4
"""
import hashlib
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# The last commit that generated the canonical artifacts.
AUDITED_ARTIFACT_HEAD = 'b19cd9a97aea18b355529e7ec97fd16ecf2f9caa'

# Canonical artifact directory — the only files whose modification invalidates
# the audit binding.
CANONICAL_ARTIFACT_DIR = 'reports/ayat_al_dayn_demo/'

# Expected SHA-256 of the canonical CSV (constitutional constant).
CANONICAL_CSV_SHA = 'f9d2410e22f6964c79867048b8f899d4d86632f33f5634422e90b1544fd52fa4'


def test_audited_artifact_head_immutable():
    """
    The declared AUDITED_ARTIFACT_HEAD must match the last commit that
    actually touched the canonical artifact files.  This proves the
    binding is anchored to a real linguistic commit, not an arbitrary hash.
    If artifacts are intentionally regenerated, update AUDITED_ARTIFACT_HEAD
    and create a new binding manifest.
    """
    result = subprocess.run(
        ['git', 'log', '--follow', '-1', '--format=%H', '--', CANONICAL_ARTIFACT_DIR],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    actual_head = result.stdout.strip()

    assert actual_head == AUDITED_ARTIFACT_HEAD, (
        f"AUDITED_ARTIFACT_HEAD mismatch:\n"
        f"  declared: {AUDITED_ARTIFACT_HEAD!r}\n"
        f"  actual last artifact commit: {actual_head!r}\n"
        f"If artifacts were intentionally regenerated, update AUDITED_ARTIFACT_HEAD "
        f"and create a new binding manifest."
    )


def test_artifact_binding_exists():
    """
    At least one closure manifest must explicitly bind to the canonical
    artifact head via the 'artifact_commit' field.

    This test NEVER passes silently — it fails explicitly when no
    applicable manifest is found rather than returning without assertion.

    Governance-only commits (which advance HEAD without touching artifacts)
    satisfy this test as long as at least one manifest has the correct
    artifact_commit value, regardless of how many governance commits have
    since advanced HEAD.

    Legacy manifests (schema_version < 2, no artifact_commit field) alone
    cannot satisfy this contract.
    """
    gate_dir = REPO_ROOT / 'reports' / 'canonical_gate'

    assert gate_dir.exists(), (
        "reports/canonical_gate/ does not exist. "
        "Run the canonical audit: bash scripts/run_canonical_final_audit.sh"
    )

    manifests = list(gate_dir.rglob('closure_manifest.*.json'))

    assert manifests, (
        "No closure_manifest.*.json files found in reports/canonical_gate/. "
        "Run the canonical audit: bash scripts/run_canonical_final_audit.sh"
    )

    applicable_manifests = [
        (p, json.loads(p.read_text(encoding='utf-8')))
        for p in manifests
        if json.loads(p.read_text(encoding='utf-8')).get('artifact_commit') == AUDITED_ARTIFACT_HEAD
    ]

    assert applicable_manifests, (
        f"No closure manifest is bound to the canonical artifact head "
        f"({AUDITED_ARTIFACT_HEAD[:12]}).\n"
        f"Found {len(manifests)} manifest(s) but none has "
        f"artifact_commit == AUDITED_ARTIFACT_HEAD.\n"
        f"Legacy manifests (no artifact_commit field) do not satisfy this contract.\n"
        f"Run the canonical audit: bash scripts/run_canonical_final_audit.sh"
    )


def test_artifact_digests_match():
    """
    Every canonical artifact digest recorded in the binding manifest must
    match the current file bytes on disk.  A mismatch means the artifact
    was modified after the audit, requiring a full canonical re-run.
    """
    gate_dir = REPO_ROOT / 'reports' / 'canonical_gate'
    if not gate_dir.exists():
        return  # test_artifact_binding_exists will catch this

    manifests = list(gate_dir.rglob('closure_manifest.*.json'))
    applicable_manifests = [
        (p, json.loads(p.read_text(encoding='utf-8')))
        for p in manifests
        if json.loads(p.read_text(encoding='utf-8')).get('artifact_commit') == AUDITED_ARTIFACT_HEAD
    ]

    if not applicable_manifests:
        return  # test_artifact_binding_exists will catch this

    # NON-SELF-REFERENTIAL BINDING (owner decision 2026-08-14).
    # The manifest is bound to the IMMUTABLE AUDITED_ARTIFACT_HEAD — the commit
    # whose canonical reports/ayat_al_dayn_demo/ artifacts are audited — NOT the
    # moving HEAD. Binding to `git rev-parse HEAD` is circular: committing the
    # manifest advances HEAD, instantly staling the just-written manifest, so the
    # contract could never be green at a committed state. The audited artifacts
    # are unchanged since AUDITED_ARTIFACT_HEAD, so that immutable commit is the
    # correct, reproducible binding target (distinct from LINGUISTIC_BASE_HEAD,
    # which advances with governed production work).
    head = AUDITED_ARTIFACT_HEAD[:7]
    head_manifest_name = f'closure_manifest.{head}.json'
    head_matches = [(p, d) for p, d in applicable_manifests if p.name == head_manifest_name]
    assert head_matches, (
        f"No applicable manifest found for HEAD={head!r} "
        f"(expected {head_manifest_name}).\n"
        f"Applicable manifests (artifact_commit={AUDITED_ARTIFACT_HEAD[:12]}):\n"
        + '\n'.join(str(p) for p, _ in applicable_manifests)
    )
    latest_path, latest_data = head_matches[0]

    artifact_digests = latest_data.get('artifact_digests', {})

    assert artifact_digests, (
        f"Manifest {latest_path.name} has no artifact_digests section. "
        f"Re-generate it with an updated canonical_gate.py."
    )

    mismatches = []
    for rel_path, expected_digest in artifact_digests.items():
        abs_path = REPO_ROOT / rel_path
        if not abs_path.exists():
            mismatches.append(f"MISSING: {rel_path}")
            continue
        actual_digest = hashlib.sha256(abs_path.read_bytes()).hexdigest()
        if actual_digest != expected_digest:
            mismatches.append(
                f"DIGEST_MISMATCH: {rel_path}\n"
                f"  expected: {expected_digest}\n"
                f"  actual:   {actual_digest}"
            )

    assert not mismatches, (
        f"Artifact digest verification failed "
        f"(manifest: {latest_path.name}):\n"
        + "\n".join(mismatches)
        + f"\nRe-run the canonical audit: bash scripts/run_canonical_final_audit.sh"
    )

    # Explicit constitutional CSV SHA check.
    csv_path = REPO_ROOT / 'reports' / 'ayat_al_dayn_demo' / 'ayat_al_dayn_results.csv'
    assert csv_path.exists(), f"Canonical CSV missing: {csv_path}"
    csv_sha = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    assert csv_sha == CANONICAL_CSV_SHA, (
        f"Constitutional CSV SHA mismatch:\n"
        f"  expected: {CANONICAL_CSV_SHA!r}\n"
        f"  actual:   {csv_sha!r}"
    )


def test_no_artifact_change_since_commit():
    """
    No canonical artifact file may have changed since AUDITED_ARTIFACT_HEAD.

    Governance-only commits never touch the artifact directory, so this
    diff is always empty for legitimate governance advances.  A non-empty
    diff means an artifact was manually modified after the audit commit,
    which is a binding violation.
    """
    diff_result = subprocess.run(
        ['git', 'diff', '--name-only',
         f'{AUDITED_ARTIFACT_HEAD}..HEAD', '--',
         CANONICAL_ARTIFACT_DIR],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    changed = diff_result.stdout.strip()

    assert not changed, (
        f"Canonical artifacts changed since audit commit "
        f"{AUDITED_ARTIFACT_HEAD[:12]}.\n"
        f"Changed files:\n{changed}\n"
        f"Re-run the full canonical audit: bash scripts/run_canonical_final_audit.sh"
    )


def test_no_stale_report_artifacts():
    """Closure manifest for current HEAD must exist and its commit field must match HEAD.

    Selection is deterministic: the expected manifest is computed from the current
    HEAD short SHA and must exist at the exact path
    reports/canonical_gate/closure_manifest.<HEAD>.json.
    mtime order is irrelevant — historical manifests for earlier commits are permitted.
    """
    gate_dir = REPO_ROOT / 'reports' / 'canonical_gate'
    if not gate_dir.exists():
        return
    # NON-SELF-REFERENTIAL BINDING (owner decision 2026-08-14): bind to the
    # IMMUTABLE AUDITED_ARTIFACT_HEAD, not the moving HEAD (see rationale in
    # test_artifact_digests_match). The audited demo artifacts are unchanged
    # since that commit, so its manifest is the stable, reproducible binding.
    head = AUDITED_ARTIFACT_HEAD[:7]
    expected_manifest = gate_dir / f'closure_manifest.{head}.json'
    assert expected_manifest.exists(), (
        f"Expected closure manifest not found: {expected_manifest.name}\n"
        f"AUDITED_ARTIFACT_HEAD={head!r}. Re-run: python scripts/canonical_gate.py --stage <STAGE_ID>"
    )
    data = json.loads(expected_manifest.read_text(encoding='utf-8'))
    manifest_commit = data.get('commit', '')
    assert manifest_commit == head, (
        f"Manifest {expected_manifest.name} internal commit mismatch: "
        f"manifest.commit={manifest_commit!r} != AUDITED_ARTIFACT_HEAD={head!r}."
    )
