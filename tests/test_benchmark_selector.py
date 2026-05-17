import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import MagicMock
from datetime import datetime
from benchmark_selector import BenchmarkMatcher
from dto_specs import BenchFull


def make_bench(hashrate, threads):
    return BenchFull(
        os="windows",
        ram=16.0,
        done_ts=datetime.now(),
        hashrate=hashrate,
        threads=threads,
        cpu_cores=6,
        cpu_threads=12,
    )


@pytest.fixture
def matcher():
    machine = MagicMock()
    machine.processor = "Ryzen 5 5600"
    benchmarks = [make_bench(h, 12) for h in [1000, 1200, 1100, 1300, 900, 1150, 1050, 1250, 1180, 1220]]
    return BenchmarkMatcher(benchmark=benchmarks, machine=machine)


def test_select_hashrate_returns_int(matcher):
    result = matcher.select_hashrate()
    assert isinstance(result, int)


def test_select_hashrate_ignores_bottom_10_percent(matcher):
    result = matcher.select_hashrate()
    assert result >= 1000


def test_select_power_known_cpu(matcher):
    assert matcher.select_power() == 65


def test_select_power_unknown_cpu():
    machine = MagicMock()
    machine.processor = "Intel Core i9-9900K"
    matcher = BenchmarkMatcher(benchmark=[], machine=machine)
    assert matcher.select_power() == 0


def test_select_threads_returns_mode(matcher):
    assert matcher.select_threads() == 12
