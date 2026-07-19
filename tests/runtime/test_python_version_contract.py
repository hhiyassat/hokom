"""Contract: Hokom requires Python >= 3.11."""
import sys
import pytest

def test_python_version_at_least_311():
    assert sys.version_info >= (3, 11), (
        f"Hokom requires Python 3.11+, running on {sys.version}"
    )

def test_python_version_major_3():
    assert sys.version_info.major == 3

def test_python_minor_at_least_11():
    assert sys.version_info.minor >= 11
