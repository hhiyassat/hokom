"""
Governance test: canonical runtime contract verification.
Runs ONLY on the canonical runtime (macOS, Python 3.12.4, .venv-py312).
On other runtimes these tests are expected to fail — they must NOT skip.
Failing here indicates the wrong runtime is being used for canonical closure.
"""
import sys
import pytest


def test_python_version_is_canonical():
    """Python must be exactly 3.12.4 in canonical core suite."""
    v = sys.version_info
    assert (v.major, v.minor, v.micro) == (3, 12, 4), (
        f"Not canonical Python: {sys.version}. "
        f"Required: 3.12.4. "
        f"This test MUST NOT skip — it must fail on wrong runtime. "
        f"Run canonical gate on macOS .venv-py312."
    )


def test_virtual_env_is_canonical():
    """Must be running in .venv-py312."""
    assert '.venv-py312' in sys.executable, (
        f"Not in canonical venv: {sys.executable}. "
        f"Required: .venv-py312."
    )


def test_canonical_entrypoint_importable():
    """hokom_pipeline.hokom must be importable."""
    from hokom_pipeline import hokom
    assert callable(hokom)


def test_canonical_entrypoint_returns_dict():
    """hokom() must return a dict for a simple token."""
    from hokom_pipeline import hokom
    result = hokom('كَاتِبٌ')
    assert isinstance(result, dict), f"hokom() returned {type(result)}, expected dict"


def test_canonical_entrypoint_has_segment_fields():
    """hokom() result must contain required segment fields."""
    from hokom_pipeline import hokom
    result = hokom('بِدَيْنٍ')
    required_fields = ['segment_host', 'morphology_surface', 'morphology_blocked']
    for f in required_fields:
        assert f in result, f"hokom() result missing field: {f!r}. Full keys: {list(result.keys())}"
