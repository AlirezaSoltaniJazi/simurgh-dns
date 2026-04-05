"""Tests for simurgh_dns.models."""

import dataclasses

import pytest

from simurgh_dns.models import BenchmarkResult


class TestBenchmarkResult:
    def test_create_successful(self, sample_result: BenchmarkResult) -> None:
        assert sample_result.provider == "TestDNS"
        assert sample_result.ip == "1.2.3.4"
        assert sample_result.avg == 25.5
        assert sample_result.reliability == 100.0

    def test_create_failed(self, failed_result: BenchmarkResult) -> None:
        assert failed_result.avg == float("inf")
        assert failed_result.reliability == 0.0
        assert failed_result.latencies == ()

    def test_failed_property_true(self, failed_result: BenchmarkResult) -> None:
        assert failed_result.failed is True

    def test_failed_property_false(self, sample_result: BenchmarkResult) -> None:
        assert sample_result.failed is False

    def test_frozen(self, sample_result: BenchmarkResult) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            sample_result.avg = 999.0  # type: ignore[misc]

    def test_slots(self) -> None:
        assert hasattr(BenchmarkResult, "__slots__")
