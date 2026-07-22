"""
Performance and memory baseline for SGA claim-bundle construction.
Uses timeit and tracemalloc — no external pytest-benchmark dependency.
HOKOM-TAAQOL-SGA-POST-CLOSURE-HARDENING-01 — HARDEN-09+10
"""
import statistics
import timeit
import tracemalloc


# ── HARDEN-09: Performance baseline ──────────────────────────────────────────

def test_bundle_construction_baseline():
    """
    Median bundle construction latency must be under 10ms.
    Warm-up: 10 iterations. Measurement: 100 iterations.
    """
    from pipeline.sga.adapters import build_claim_bundle

    hokom_result = {
        "word": "اسْتَغْفَرَ",
        "segment_host": "اسْتَغْفَرَ",
        "word_class": "VERB",
        "root_candidate": "غ-ف-ر",
        "wazn": "اسْتَفْعَلَ",
        "bab": "نَصَرَ",
    }

    # Warm-up
    for _ in range(10):
        build_claim_bundle(hokom_result, "ROOT_CLAIM", "ROOT_CLAIM")

    # Measure 100 iterations
    times = []
    for _ in range(100):
        start = timeit.default_timer()
        build_claim_bundle(hokom_result, "ROOT_CLAIM", "ROOT_CLAIM")
        times.append(timeit.default_timer() - start)

    median_ms = statistics.median(times) * 1000
    mean_ms   = statistics.mean(times)   * 1000
    stdev_ms  = statistics.stdev(times)  * 1000

    print(
        f"\nBundle construction (100 iterations): "
        f"median={median_ms:.3f}ms  mean={mean_ms:.3f}ms  stdev={stdev_ms:.3f}ms"
    )

    # Soft limit: must be under 10ms median
    assert median_ms < 10.0, (
        f"Bundle construction too slow: median={median_ms:.3f}ms (limit=10ms)"
    )


def test_bundle_construction_sound_root():
    """Simple sound-root bundle should be under 5ms median."""
    from pipeline.sga.adapters import build_claim_bundle

    hokom_result = {
        "word": "كَتَبَ",
        "segment_host": "كَتَبَ",
        "word_class": "VERB",
        "root_candidate": "ك-ت-ب",
    }

    for _ in range(10):
        build_claim_bundle(hokom_result, "ROOT_CLAIM", "ROOT_CLAIM")

    times = []
    for _ in range(100):
        start = timeit.default_timer()
        build_claim_bundle(hokom_result, "ROOT_CLAIM", "ROOT_CLAIM")
        times.append(timeit.default_timer() - start)

    median_ms = statistics.median(times) * 1000
    print(f"\nSimple bundle: median={median_ms:.3f}ms")
    assert median_ms < 5.0, f"Simple bundle too slow: {median_ms:.3f}ms (limit=5ms)"


def test_bundle_construction_with_h11_h15():
    """Full H11-H15 bundle (bab, masdar, derivative, morphosyntax) must be under 15ms median."""
    from pipeline.sga.adapters import build_claim_bundle

    hokom_result = {
        "word": "مَكْتُوبٌ",
        "segment_host": "مَكْتُوبٌ",
        "word_class": "ISM",
        "root_candidate": "ك-ت-ب",
        "wazn": "مَفْعُول",
        "derivative": "ism_maf3ul",
        "bab": "نَصَرَ",
        "masdar": "كِتَابَة",
        "number": "SINGULAR",
        "gender": "MASCULINE",
        "lemma": "كَتَبَ",
    }

    for _ in range(10):
        build_claim_bundle(hokom_result, "DERIVATIVE_CLAIM", "DERIVATIVE_CLAIM")

    times = []
    for _ in range(100):
        start = timeit.default_timer()
        build_claim_bundle(hokom_result, "DERIVATIVE_CLAIM", "DERIVATIVE_CLAIM")
        times.append(timeit.default_timer() - start)

    median_ms = statistics.median(times) * 1000
    print(f"\nH11-H15 bundle: median={median_ms:.3f}ms")
    assert median_ms < 15.0, f"H11-H15 bundle too slow: {median_ms:.3f}ms (limit=15ms)"


# ── HARDEN-10: Memory baseline ────────────────────────────────────────────────

def test_memory_single_bundle():
    """Single bundle allocation must be under 500KB."""
    from pipeline.sga.adapters import build_claim_bundle

    # Warm up to avoid import overhead in measurement
    build_claim_bundle({"word": "كَتَبَ", "segment_host": "كَتَبَ"}, "ROOT_CLAIM", "ROOT_CLAIM")

    tracemalloc.start()
    snapshot1 = tracemalloc.take_snapshot()

    bundle = build_claim_bundle(
        {"word": "كَتَبَ", "segment_host": "كَتَبَ", "root_candidate": "ك-ت-ب"},
        "ROOT_CLAIM", "ROOT_CLAIM",
    )

    snapshot2 = tracemalloc.take_snapshot()
    tracemalloc.stop()

    stats = snapshot2.compare_to(snapshot1, "lineno")
    total_kb = sum(s.size_diff for s in stats if s.size_diff > 0) / 1024

    print(f"\nSingle bundle memory allocation: {total_kb:.2f} KB")

    # Keep a reference so bundle is not GC'd before snapshot
    _ = bundle.claim_key

    # Soft limit: single bundle must allocate less than 500KB
    assert total_kb < 500, f"Excessive memory for single bundle: {total_kb:.2f}KB (limit=500KB)"


def test_memory_repeated_evaluations():
    """100 repeated bundle constructions must not grow memory by more than 1MB."""
    from pipeline.sga.adapters import build_claim_bundle

    # Warm up
    for _ in range(5):
        build_claim_bundle({"word": "كَتَبَ", "segment_host": "كَتَبَ"}, "ROOT_CLAIM", "ROOT_CLAIM")

    tracemalloc.start()
    snapshot1 = tracemalloc.take_snapshot()

    bundles = []
    for _ in range(100):
        b = build_claim_bundle(
            {"word": "كَتَبَ", "segment_host": "كَتَبَ"},
            "ROOT_CLAIM", "ROOT_CLAIM",
        )
        bundles.append(b)

    snapshot2 = tracemalloc.take_snapshot()
    tracemalloc.stop()

    stats = snapshot2.compare_to(snapshot1, "lineno")
    growth_kb = sum(s.size_diff for s in stats if s.size_diff > 0) / 1024

    print(f"\n100-evaluation memory growth: {growth_kb:.2f} KB")

    # Must not grow more than 1MB across 100 calls (no unbounded leak)
    assert growth_kb < 1024, (
        f"Potential memory leak: {growth_kb:.2f}KB after 100 evals (limit=1024KB)"
    )


def test_memory_mixed_corpus():
    """Mixed corpus of 20 different tokens must not exceed 2MB total growth."""
    from pipeline.sga.adapters import build_claim_bundle

    corpus = [
        ("كَتَبَ", "ROOT_CLAIM"),
        ("قَالَ", "ROOT_CLAIM"),
        ("اللَّهُ", "WORD_CLASS_CLAIM"),
        ("مَنْ", "FUNCTIONAL_OWNER_CLAIM"),
        ("الْكِتَابُ", "ROOT_CLAIM"),
        ("مَكْتُوبٌ", "DERIVATIVE_CLAIM"),
        ("كَاتِبٌ", "DERIVATIVE_CLAIM"),
        ("رَبَّهُ", "ROOT_CLAIM"),
        ("وَكَتَبَ", "ROOT_CLAIM"),
        ("يَكْتُبُ", "ROOT_CLAIM"),
        ("بِاللَّهِ", "WORD_CLASS_CLAIM"),
        ("هُوَ", "FUNCTIONAL_OWNER_CLAIM"),
        ("اسْتَغْفَرَ", "ROOT_CLAIM"),
        ("انْكَسَرَ", "ROOT_CLAIM"),
        ("النُّورُ", "ROOT_CLAIM"),
        ("الشَّمْسُ", "ROOT_CLAIM"),
        ("قَالَهَا", "ROOT_CLAIM"),
        ("مَتَى", "FUNCTIONAL_OWNER_CLAIM"),
        ("رَدَّ", "ROOT_CLAIM"),
        ("دَعَا", "ROOT_CLAIM"),
    ]

    # Warm up
    for word, kind in corpus:
        build_claim_bundle({"word": word, "segment_host": word}, kind, kind)

    tracemalloc.start()
    snapshot1 = tracemalloc.take_snapshot()

    bundles = []
    for word, kind in corpus:
        bundles.append(
            build_claim_bundle({"word": word, "segment_host": word}, kind, kind)
        )

    snapshot2 = tracemalloc.take_snapshot()
    tracemalloc.stop()

    stats = snapshot2.compare_to(snapshot1, "lineno")
    growth_kb = sum(s.size_diff for s in stats if s.size_diff > 0) / 1024

    print(f"\nMixed corpus (20 tokens) memory growth: {growth_kb:.2f} KB")

    assert growth_kb < 2048, (
        f"Mixed corpus excessive memory: {growth_kb:.2f}KB (limit=2048KB)"
    )
