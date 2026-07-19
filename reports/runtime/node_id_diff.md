# Node ID Diff: Before vs After Runtime Migration

## Summary
- Tests before: 4183 collected
- Tests after: 4218 collected
- New tests added: 35 (all in tests/runtime/)
- Tests removed: 0

## New Tests Added (tests/runtime/)

### test_clean_environment_contract.py (3)
- test_no_hidden_pythonpath_required
- test_deterministic_imports
- test_sys_path_readable

### test_native_strenum.py (4)
- test_native_strenum_importable
- test_native_strenum_module
- test_no_strenum_shim_in_sys_modules
- test_strenum_works_natively

### test_no_compatibility_injection.py (4)
- test_no_sitecustomize
- test_no_usercustomize
- test_enum_module_not_replaced
- test_no_enum_strenum_monkey_patch

### test_packaging_python_requires.py (3)
- test_python_311_minimum
- test_python_version_is_311_plus
- test_python_version_file_if_present

### test_python_runtime_imports.py (11)
- test_python_311_plus
- test_hokom_pipeline_importable
- test_p5_lexical_importable
- test_pre_root_importable
- test_p5_inflection_importable
- test_p5_masdar_importable
- test_p6_derivatives_importable
- test_word_class_importable
- test_word_class_models_importable
- test_no_shim_modules
- test_engine_ids_unchanged

### test_python_version_contract.py (3)
- test_python_version_at_least_311
- test_python_version_major_3
- test_python_minor_at_least_11

### test_taaqol_import_readiness.py (4)
- test_python_version_for_taaqol
- test_taaqol_vendor_path_exists
- test_taaqol_not_in_hokom_pipeline
- test_taaqol_live_integration_not_started

### test_taaqol_not_live_yet.py (3)
- test_hokom_pipeline_no_direct_taaqol_vendor_import
- test_no_taaqol_call_during_analysis
- test_taaqol_live_calls_zero

## Notes
- No tests removed or renamed
- All 4183 pre-existing tests preserved unchanged
- 10 of the 35 new tests require Python 3.11+ to pass (they correctly fail on Python 3.10,
  enforcing the runtime contract; they will pass on the user's macOS Python 3.12.4)
