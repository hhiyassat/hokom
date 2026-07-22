# HARDEN-09: Performance Baseline
Stage: HOKOM-TAAQOL-SGA-POST-CLOSURE-HARDENING-01

## Benchmark Environment
- Platform: Linux 6.8.0-124-generic aarch64
- Python: 3.10.12
- Method: timeit.default_timer(), 10 warm-up + 100 measurement iterations

## Results

### Augmented Form (اسْتَغْفَرَ, Form X)
- Median: 0.040ms
- Mean:   0.041ms
- StDev:  0.004ms
- Limit:  10.0ms → PASS

### Simple Sound Root (كَتَبَ)
- Median: 0.037ms
- Limit:  5.0ms → PASS

### Full H11-H15 Bundle (مَكْتُوبٌ with bab/masdar/derivative/morphosyntax)
- Median: 0.044ms
- Limit:  15.0ms → PASS

## Notes
- All latencies well under limits (250x–340x headroom)
- No external I/O during bundle construction
- claim_key computation (SHA-256) is the dominant operation
