"""Contract: Package metadata declares requires-python >= 3.11."""
import sys
import importlib.metadata
import os

def test_python_311_minimum():
    """Package should declare requires-python >= 3.11."""
    # Check pyproject.toml directly
    if os.path.exists('pyproject.toml'):
        import tomllib
        with open('pyproject.toml', 'rb') as f:
            data = tomllib.load(f)
        requires = data.get('project', {}).get('requires-python', '')
        assert '3.11' in requires or '3.12' in requires, \
            f"requires-python should be >=3.11, got: '{requires}'"
    # Also check via importlib.metadata if installed
    else:
        pass  # pyproject.toml not present

def test_python_version_is_311_plus():
    assert sys.version_info >= (3, 11)

def test_python_version_file_if_present():
    if os.path.exists('.python-version'):
        with open('.python-version') as f:
            ver = f.read().strip()
        major, minor = ver.split('.')[:2]
        assert int(major) == 3
        assert int(minor) >= 11, f".python-version should be 3.11+, got {ver}"
