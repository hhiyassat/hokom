"""
Governance: no skip markers tied to EXTERNAL ENGINES (HR2S, etc.)
are allowed in the canonical core suite.

Note on Python-version guards: skipif(sys.version_info < (3, 11)) is
PERMITTED in the canonical core. On the canonical runtime (Python 3.12.4)
these conditions evaluate FALSE and the tests run normally.
Python-version tests that ASSERT a specific version (not skipif) must live
in tests/compatibility/.
"""
import re
from pathlib import Path

REPO_ROOT  = Path(__file__).resolve().parent.parent.parent
TESTS_DIR  = REPO_ROOT / 'tests'

# EXTERNAL ENGINE identifiers whose presence in a skip decorator is forbidden.
# Only these specific identifiers — not Python-version guards.
_FORBIDDEN_IDS = [
    'HR2S_NOT_INSTALLED',
    'SKIP_HR2S',
    'hr2s_not_installed',
]

# Directories explicitly allowed to have these patterns
ALLOWED_DIRS = {'compatibility', 'external_oracle', 'governance'}

# Pattern: a pytest skip decorator line that contains a forbidden identifier.
# We match `@pytest.mark.skip*` lines or `pytestmark = pytest.mark.skip*` lines
# that also contain one of the forbidden identifiers.
_SKIP_DECORATOR = re.compile(r'@pytest\.mark\.skip|pytestmark.*skip', re.IGNORECASE)


def _find_violations():
    violations = []
    for py_file in TESTS_DIR.rglob('*.py'):
        parts = set(py_file.relative_to(TESTS_DIR).parts)
        if parts & ALLOWED_DIRS:
            continue

        content = py_file.read_text(encoding='utf-8', errors='ignore')
        for i, line in enumerate(content.splitlines(), 1):
            # Only flag lines that are actual skip decorators / markers
            if not _SKIP_DECORATOR.search(line):
                continue
            for fid in _FORBIDDEN_IDS:
                if fid in line:
                    violations.append(
                        f"{py_file.relative_to(REPO_ROOT)}:{i}: {line.strip()[:100]}"
                    )
    return violations


def test_no_external_engine_skips_in_canonical_core():
    """No external-engine skip decorators (HR2S_NOT_INSTALLED etc.) in canonical core."""
    violations = _find_violations()
    assert violations == [], (
        "External-engine skip decorators found in canonical core "
        "(move these tests to tests/external_oracle/):\n"
        + "\n".join(violations[:20])
    )
