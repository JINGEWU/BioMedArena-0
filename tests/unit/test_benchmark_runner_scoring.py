from harness.eval.benchmark_runner import BenchmarkRunner


def test_runner_uses_conservative_exact_match():
    assert BenchmarkRunner._check_correctness("active", "inactive") is False
    assert BenchmarkRunner._check_correctness("0", "10") is False
    assert BenchmarkRunner._check_correctness("active", "The answer is active.") is True


def test_runner_numeric_alias_uses_numeric_scorer():
    assert BenchmarkRunner._check_correctness("0.001", "The answer is 1e-3.", "numeric") is True
