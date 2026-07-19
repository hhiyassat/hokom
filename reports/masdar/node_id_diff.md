# HOKOM-MORPHOLOGY-MASDAR-OWNERSHIP-01 — Node ID Diff

## Summary

- **Before**: 3053 test node IDs
- **After**:  3183 test node IDs
- **Added**:  130 node IDs (all in `tests/p5_masdar/`)

## Added Node IDs by File

### test_masdar_constitutional.py (15 nodes)
- test_masdar_canonical_owner
- test_masdar_engine_id
- test_parallel_engines_zero
- test_external_dependencies_zero
- test_form_i_unlicensed_guesses_zero
- test_unlicensed_masdar_guesses_zero
- test_forced_single_masdar_results_zero
- test_multiple_licensed_masdars_supported
- test_subtype_contracts_verified
- test_semantic_modifications_zero
- test_data_files_exist
- test_engine_no_external_libraries
- test_engine_no_hardcoded_corpus
- test_engine_canonical_entrypoint_exists
- test_masdar_ownership_version

### test_masdar_data_reproducibility.py (8 nodes)
- test_registry_loaded_twice_same_rule_count
- test_registry_loaded_twice_same_lexicon_count
- test_registry_loaded_twice_same_pattern_count
- test_data_files_are_valid_jsonl
- test_rule_registry_deterministic_ids
- test_lexicon_deterministic_ids
- test_data_files_sha256_stable
- test_data_hashes_match_report

### test_masdar_engine_augmented.py (21 nodes)
- test_augmented_accepted[FORM_II-FA33ALA-TAF3IL]
- test_augmented_accepted[FORM_IV-AF3AL-IF3AL]
- test_augmented_accepted[FORM_V-TAFA33ALA-TAFA33UL]
- test_augmented_accepted[FORM_VI-TAFA3ALA-TAFA3UL]
- test_augmented_accepted[FORM_VII-INFA3ALA-INFI3AL]
- test_augmented_accepted[FORM_VIII-IFTA3ALA-IFTI3AL]
- test_augmented_accepted[FORM_IX-IF3ALLA-IF3ILAL]
- test_augmented_accepted[FORM_X-ISTAF3ALA-ISTIF3AL]
- test_augmented_accepted[QUADRILITERAL_FORM_I-FA3LALA-FA3LALA]
- test_form_iii_multiple_masdars
- test_fa3il_participle_blocked
- test_missing_licensed_root_blocked
- test_missing_licensed_pattern_blocked
- test_missing_verbhood_deferred
- test_verbal_lemma_no_host_passes
- test_weak_root_form_ii_deferred
- test_source_engine_always_hokom[FORM_II-FA33ALA]
- test_source_engine_always_hokom[FORM_X-ISTAF3ALA]

### test_masdar_engine_form_i.py (8 nodes)
- test_kataba_accepted
- test_kataba_single_multiplicity
- test_3alima_accepted
- test_unknown_root_deferred
- test_qatala_form_iii_multiple
- test_form_i_deterministic_ordering
- test_form_i_lexical_attestation_flag
- test_form_i_license_kind

### test_masdar_false_positives.py (8 nodes)
- test_no_verbal_anchor_not_accepted
- test_fa3il_participle_blocked
- test_validate_mode_root_mismatch_deferred
- test_null_root_never_accepted
- test_null_pattern_never_accepted
- test_blocked_has_no_licensed_masdars
- test_deferred_has_no_licensed_masdars
- test_form_i_unknown_root_never_guessed
- test_analyze_surface_mode_deferred

### test_masdar_models.py (22 nodes)
- test_canonical_owner, test_engine_id, test_ownership_version
- test_masdar_types, test_masdar_verdicts
- test_masdar_evidence_valid, test_masdar_evidence_with_detail
- test_masdar_evidence_invalid_type, test_masdar_evidence_invalid_sufficiency
- test_masdar_evidence_to_dict
- test_masdar_contradiction_valid, test_masdar_contradiction_invalid
- test_masdar_contradiction_to_dict
- test_realization_operation_valid, test_realization_operation_invalid
- test_trace_event, test_trace_event_no_detail
- test_ownership_gate_defaults, test_ownership_gate_frozen

### test_masdar_properties.py (11 nodes)
- test_determinism_same_verdict[FORM_I-FA3ALA]
- test_determinism_same_verdict[FORM_II-FA33ALA]
- test_determinism_same_verdict[FORM_X-ISTAF3ALA]
- test_determinism_same_candidate_count[FORM_II-FA33ALA]
- test_determinism_same_candidate_count[FORM_X-ISTAF3ALA]
- test_no_accept_after_root_null
- test_root_preserved_in_licensed_masdars
- test_json_roundtrip_preserves_verdict
- test_json_roundtrip_preserves_multiplicity
- test_json_roundtrip_preserves_source_engine
- test_trace_always_present
- test_trace_steps_sequential

### test_masdar_rule_registry.py (22 nodes)
- test_registry_loads through test_pattern_count (22 tests)

### test_masdar_serialization.py (8 nodes)
- test_to_dict_is_json_serializable through test_request_serializable

### test_masdar_subtypes.py (10 nodes)
- test_masdar_mimi_deferred through test_marra_missing_evidence_contains_paradigm

## Status
All 130 added node IDs: PASS
