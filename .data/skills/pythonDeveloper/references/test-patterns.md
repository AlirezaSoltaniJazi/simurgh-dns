# Test Patterns Reference — simurgh-dns

## Test File Structure

```python
"""Tests for DNS protocol parser."""

import struct

import pytest

from simurgh.protocol.parser import parse_header, parse_name
from simurgh.protocol.types import DNSQuestion, RecordType


class TestParseHeader:
    """Tests for DNS header parsing."""

    def test_parses_valid_header(self, dns_header_bytes: bytes) -> None:
        result = parse_header(dns_header_bytes)

        assert result["id"] == 0x1234
        assert result["qr"] == 0
        assert result["qdcount"] == 1

    def test_raises_on_short_packet(self) -> None:
        with pytest.raises(ValueError, match="too short"):
            parse_header(b"\x00" * 5)

    def test_parses_response_flag(self) -> None:
        # QR bit set = response
        data = struct.pack("!HHHHHH", 0x1234, 0x8000, 0, 0, 0, 0)
        result = parse_header(data)

        assert result["qr"] == 1

    def test_parses_all_flag_fields(self) -> None:
        # Flags: QR=1, OPCODE=0, AA=1, TC=0, RD=1, RA=1, RCODE=0
        flags = 0x8580
        data = struct.pack("!HHHHHH", 0x1234, flags, 1, 2, 0, 0)
        result = parse_header(data)

        assert result["qr"] == 1
        assert result["aa"] == 1
        assert result["rd"] == 1
        assert result["ra"] == 1
        assert result["rcode"] == 0


class TestParseName:
    """Tests for DNS name parsing with compression."""

    def test_parses_simple_name(self) -> None:
        # example.com = \x07example\x03com\x00
        data = b"\x07example\x03com\x00"
        name, offset = parse_name(data, 0)

        assert name == "example.com"
        assert offset == len(data)

    def test_parses_pointer_compression(self) -> None:
        # Name at offset 0, then pointer at offset 13
        data = b"\x07example\x03com\x00\xc0\x00"
        name, offset = parse_name(data, 13)

        assert name == "example.com"
        assert offset == 15

    def test_raises_on_truncated_name(self) -> None:
        data = b"\x07exam"
        with pytest.raises(ValueError, match="extends beyond"):
            parse_name(data, 0)
```

## Conftest Fixtures

Located in `tests/conftest.py`.

```python
"""Shared test fixtures for simurgh-dns."""

import struct
from pathlib import Path

import pytest

from simurgh.cache import DNSCache
from simurgh.config import SimurghConfig
from simurgh.protocol.types import DNSRecord, RecordType


@pytest.fixture
def sample_config() -> SimurghConfig:
    """Minimal test configuration."""
    return SimurghConfig(
        host="127.0.0.1",
        port=15353,
        upstream_dns="8.8.8.8",
        cache_size=100,
    )


@pytest.fixture
def dns_cache() -> DNSCache:
    """Empty DNS cache for testing."""
    return DNSCache(max_size=100)


@pytest.fixture
def dns_header_bytes() -> bytes:
    """Valid DNS query header bytes."""
    return struct.pack(
        "!HHHHHH",
        0x1234,  # ID
        0x0100,  # Flags: RD=1
        1,       # QDCOUNT
        0,       # ANCOUNT
        0,       # NSCOUNT
        0,       # ARCOUNT
    )


@pytest.fixture
def a_record() -> DNSRecord:
    """Sample A record for example.com."""
    return DNSRecord(
        name="example.com",
        rtype=RecordType.A,
        rclass=1,
        ttl=300,
        rdata=b"\x5d\xb8\xd8\x22",  # 93.184.216.34
    )


@pytest.fixture
def sample_query_bytes() -> bytes:
    """Complete DNS query packet for example.com A record."""
    header = struct.pack("!HHHHHH", 0x1234, 0x0100, 1, 0, 0, 0)
    question = b"\x07example\x03com\x00" + struct.pack("!HH", 1, 1)
    return header + question


@pytest.fixture
def tmp_config_file(tmp_path: Path) -> Path:
    """Temporary config file for testing."""
    config_file = tmp_path / ".env"
    config_file.write_text(
        "SIMURGH_HOST=127.0.0.1\n"
        "SIMURGH_PORT=15353\n"
        "SIMURGH_UPSTREAM_DNS=8.8.8.8\n"
    )
    return config_file
```

## Async Test Patterns

```python
"""Tests for async DNS server."""

import asyncio

import pytest

from simurgh.server import DNSProtocol, start_server


class TestDNSProtocol:
    """Tests for the UDP protocol handler."""

    async def test_receives_and_responds(
        self,
        sample_query_bytes: bytes,
        sample_config: "SimurghConfig",
    ) -> None:
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: DNSProtocol(resolver=MockResolver()),
            local_addr=("127.0.0.1", 0),
        )

        try:
            addr = transport.get_extra_info("sockname")
            # Send query and verify response
            # ...
        finally:
            transport.close()

    async def test_handles_malformed_packet(self) -> None:
        protocol = DNSProtocol(resolver=MockResolver())
        # Should not raise — log and send SERVFAIL
        protocol.datagram_received(b"\x00\x01", ("127.0.0.1", 12345))
```

## Mocking Patterns

```python
"""Tests with mocking for upstream DNS."""

from unittest.mock import AsyncMock, patch

import pytest

from simurgh.resolver import Resolver
from simurgh.models import ResolveResult


class TestResolver:
    """Tests for query resolver."""

    async def test_returns_cached_result(
        self,
        sample_config: "SimurghConfig",
        dns_cache: "DNSCache",
        a_record: "DNSRecord",
    ) -> None:
        dns_cache.put("example.com", 1, [a_record], ttl=300)
        resolver = Resolver(config=sample_config, cache=dns_cache)

        result = await resolver.resolve_name("example.com", 1)

        assert result.success
        assert result.cached is True

    @patch("simurgh.upstream.query_upstream")
    async def test_forwards_to_upstream_on_miss(
        self,
        mock_upstream: AsyncMock,
        sample_config: "SimurghConfig",
    ) -> None:
        mock_upstream.return_value = ResolveResult(
            query="example.com",
            record_type="A",
            answers=["93.184.216.34"],
            ttl=300,
        )
        resolver = Resolver(config=sample_config)

        result = await resolver.resolve_name("example.com", 1)

        assert result.success
        mock_upstream.assert_awaited_once()

    async def test_returns_error_on_timeout(
        self,
        sample_config: "SimurghConfig",
    ) -> None:
        sample_config.timeout = 0.001  # Very short timeout
        resolver = Resolver(config=sample_config)

        result = await resolver.resolve_name("nonexistent.invalid", 1)

        assert not result.success
        assert "timeout" in result.error.lower()
```

## pytest Configuration

In `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
filterwarnings = [
    "error",
    "ignore::DeprecationWarning",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks integration tests requiring network",
]
```
