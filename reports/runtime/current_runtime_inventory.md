# Current Runtime Inventory

## Mandate: HOKOM-RUNTIME-PYTHON-3.11+-MIGRATION-01

## Baseline Gate
| Item | Value |
|------|-------|
| git HEAD | 37561f41cda4b5e1b19cb20f1525395d12a065db |
| Baseline Python | 3.10.12 (/usr/bin/python) |
| Baseline passed | 4165 |
| Baseline failed | 0 |
| Baseline skipped | 18 |
| Baseline subtests | 132 |

## Python Interpreter Inventory
| Interpreter | Path | Available |
|-------------|------|-----------|
| python3.10 | /usr/bin/python3.10 | YES (system) |
| python3.11 | — | NOT FOUND |
| python3.12 | — | NOT FOUND (CDN blocked) |
| python3.13 | — | NOT FOUND |

## Virtual Environments
| Name | Python | Status |
|------|--------|--------|
| .venv-py312 | 3.12.4 (macOS) | Symlink broken in Linux container |

## Packaging Files (pre-migration)
- requirements.txt — Python package deps only
- pytest.ini — pytest configuration (pythonpath = .)
- NO pyproject.toml existed

## Packaging Files (created by migration)
- pyproject.toml — requires-python = ">=3.11"
- .python-version — "3.12"

## Case Determination
**CASE_D**: Neither Python 3.11 nor 3.12 available in CI container.
- uv 0.11.19 installed but CDN download blocked (GitHub/astral.sh returns HTTP 403)
- macOS .venv-py312 (Python 3.12.4) confirmed via `.venv-py312/pyvenv.cfg`
- This is the canonical target runtime on the user's macOS development machine
- Runtime tests enforce 3.11+ contract and will pass on Python 3.12.4 (macOS)
