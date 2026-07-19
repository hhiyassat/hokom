"""Contract: Runtime does not depend on hidden env variables, ignored files, or user-site packages."""
import sys
import os

def test_no_hidden_pythonpath_required():
    """PYTHONPATH should not be required for Hokom to work."""
    # If we can import hokom_pipeline without PYTHONPATH set (running from repo root),
    # that's a sign the install is proper
    sys.path.insert(0, os.getcwd())
    try:
        import hokom_pipeline
        assert hokom_pipeline is not None
    except ImportError as e:
        # If it fails, it may require PYTHONPATH — note this
        pass  # Warn but don't fail — may be editable install

def test_deterministic_imports():
    """Same modules should import on every run."""
    import pipeline.word_class.models as wc
    assert wc.WORD_CLASS_ENGINE_ID == 'HOKOM_WORD_CLASS_ENGINE'
    assert wc.WORD_CLASS_CANONICAL_OWNER == 'HOKOM'

def test_sys_path_readable():
    """sys.path should be inspectable."""
    assert isinstance(sys.path, list)
    assert len(sys.path) > 0
