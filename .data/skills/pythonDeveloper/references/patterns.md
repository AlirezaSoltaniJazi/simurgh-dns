# Patterns Reference — simurgh-dns

## 1. Result Object Pattern

Operations that can fail return dataclasses instead of raising exceptions.

```python
from dataclasses import dataclass


@dataclass
class ResolveResult:
    """Result of a DNS query resolution."""

    query: str
    record_type: str
    answers: list[str]
    ttl: int = 0
    cached: bool = False
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.error is None


# Usage
def resolve_query(domain: str, record_type: str) -> ResolveResult:
    try:
        answers = _lookup(domain, record_type)
        return ResolveResult(
            query=domain,
            record_type=record_type,
            answers=answers,
            ttl=300,
        )
    except LookupError as e:
        return ResolveResult(
            query=domain,
            record_type=record_type,
            answers=[],
            error=str(e),
        )
```

## 2. Frozen Dataclass for Protocol Types

All DNS protocol structures are immutable.

```python
from dataclasses import dataclass
from enum import IntEnum


class RecordType(IntEnum):
    """DNS record types (RFC 1035+)."""

    A = 1
    NS = 2
    CNAME = 5
    SOA = 6
    MX = 15
    TXT = 16
    AAAA = 28
    SRV = 33


@dataclass(frozen=True, slots=True)
class DNSQuestion:
    """A single DNS question entry."""

    name: str
    qtype: RecordType
    qclass: int = 1  # IN class


@dataclass(frozen=True, slots=True)
class DNSRecord:
    """A single DNS resource record."""

    name: str
    rtype: RecordType
    rclass: int
    ttl: int
    rdata: bytes

    @property
    def is_expired(self) -> bool:
        """Check if record TTL has expired (requires external timestamp)."""
        return self.ttl <= 0
```

## 3. Binary Parsing with struct

DNS packets use network byte order (big-endian).

```python
import struct

# Pre-compile struct formats for performance
HEADER_FORMAT = struct.Struct("!HHHHHH")  # 12 bytes: ID, flags, counts
QUESTION_FOOTER = struct.Struct("!HH")     # 4 bytes: qtype, qclass
RECORD_HEADER = struct.Struct("!HHIH")     # 10 bytes: type, class, ttl, rdlength


def parse_header(data: bytes) -> dict[str, int]:
    """Parse DNS header from raw bytes."""
    if len(data) < HEADER_FORMAT.size:
        raise ValueError(f"DNS header too short: {len(data)} bytes")

    id_, flags, qdcount, ancount, nscount, arcount = HEADER_FORMAT.unpack_from(data)

    return {
        "id": id_,
        "flags": flags,
        "qr": (flags >> 15) & 1,
        "opcode": (flags >> 11) & 0xF,
        "aa": (flags >> 10) & 1,
        "tc": (flags >> 9) & 1,
        "rd": (flags >> 8) & 1,
        "ra": (flags >> 7) & 1,
        "rcode": flags & 0xF,
        "qdcount": qdcount,
        "ancount": ancount,
        "nscount": nscount,
        "arcount": arcount,
    }


def parse_name(data: bytes, offset: int) -> tuple[str, int]:
    """Parse a DNS domain name with pointer compression support."""
    labels: list[str] = []
    original_offset = offset
    jumped = False

    while True:
        if offset >= len(data):
            raise ValueError("DNS name extends beyond packet")

        length = data[offset]

        if length == 0:
            if not jumped:
                offset += 1
            break
        elif (length & 0xC0) == 0xC0:
            # Pointer compression
            if offset + 1 >= len(data):
                raise ValueError("DNS pointer extends beyond packet")
            pointer = struct.unpack_from("!H", data, offset)[0] & 0x3FFF
            if not jumped:
                original_offset = offset + 2
            offset = pointer
            jumped = True
        else:
            offset += 1
            if offset + length > len(data):
                raise ValueError("DNS label extends beyond packet")
            labels.append(data[offset:offset + length].decode("ascii"))
            offset += length

    name = ".".join(labels)
    return (name, original_offset if jumped else offset)
```

## 4. Async Server Pattern

Non-blocking DNS server using asyncio.

```python
import asyncio
from dataclasses import dataclass


@dataclass
class ServerConfig:
    """DNS server configuration."""

    host: str = "127.0.0.1"
    port: int = 5353
    upstream: str = "8.8.8.8"
    cache_size: int = 10000
    timeout: float = 5.0


class DNSProtocol(asyncio.DatagramProtocol):
    """Async UDP DNS protocol handler."""

    def __init__(self, resolver: "Resolver") -> None:
        self.resolver = resolver
        self.transport: asyncio.DatagramTransport | None = None

    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        self.transport = transport

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        asyncio.ensure_future(self._handle_query(data, addr))

    async def _handle_query(
        self,
        data: bytes,
        addr: tuple[str, int],
    ) -> None:
        try:
            response = await self.resolver.resolve(data)
            if self.transport is not None:
                self.transport.sendto(response, addr)
        except Exception:
            # Log error, send SERVFAIL response
            pass


async def start_server(config: ServerConfig) -> None:
    """Start the async DNS server."""
    resolver = Resolver(config)
    loop = asyncio.get_running_loop()

    transport, _ = await loop.create_datagram_endpoint(
        lambda: DNSProtocol(resolver),
        local_addr=(config.host, config.port),
    )

    try:
        await asyncio.Event().wait()  # Run forever
    finally:
        transport.close()
```

## 5. TTL-Aware Cache Pattern

```python
import time
from dataclasses import dataclass, field


@dataclass
class CacheEntry:
    """A cached DNS record with expiry."""

    records: list["DNSRecord"]
    expires_at: float

    @property
    def is_expired(self) -> bool:
        return time.monotonic() > self.expires_at

    @property
    def remaining_ttl(self) -> int:
        return max(0, int(self.expires_at - time.monotonic()))


class DNSCache:
    """TTL-aware DNS record cache."""

    def __init__(self, max_size: int = 10000) -> None:
        self._cache: dict[tuple[str, int], CacheEntry] = {}
        self._max_size = max_size

    def get(self, name: str, rtype: int) -> list["DNSRecord"] | None:
        key = (name.lower(), rtype)
        entry = self._cache.get(key)
        if entry is None:
            return None
        if entry.is_expired:
            del self._cache[key]
            return None
        return entry.records

    def put(self, name: str, rtype: int, records: list["DNSRecord"], ttl: int) -> None:
        if len(self._cache) >= self._max_size:
            self._evict_expired()
        key = (name.lower(), rtype)
        self._cache[key] = CacheEntry(
            records=records,
            expires_at=time.monotonic() + ttl,
        )

    def _evict_expired(self) -> None:
        now = time.monotonic()
        expired = [k for k, v in self._cache.items() if now > v.expires_at]
        for key in expired:
            del self._cache[key]

    def flush(self) -> int:
        count = len(self._cache)
        self._cache.clear()
        return count
```

## 6. Registry Pattern

Centralized registries for extensible record type handling.

```python
from collections.abc import Callable

# Record type parser registry
RECORD_PARSERS: dict[int, Callable[[bytes, int, int], "DNSRecord"]] = {}


def register_parser(rtype: int) -> Callable:
    """Decorator to register a record type parser."""

    def decorator(func: Callable[[bytes, int, int], "DNSRecord"]) -> Callable:
        RECORD_PARSERS[rtype] = func
        return func

    return decorator


@register_parser(RecordType.A)
def parse_a_record(data: bytes, offset: int, rdlength: int) -> "DNSRecord":
    """Parse an A (IPv4) record."""
    if rdlength != 4:
        raise ValueError(f"Invalid A record length: {rdlength}")
    # ... parsing logic
```

## 7. Configuration with pydantic-settings

```python
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SimurghConfig(BaseSettings):
    """Application configuration loaded from environment."""

    model_config = SettingsConfigDict(
        env_prefix="SIMURGH_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    host: str = "127.0.0.1"
    port: int = 5353
    upstream_dns: str = "8.8.8.8"
    cache_size: int = 10000
    log_level: str = "INFO"
    blocklist_path: Path | None = None
    timeout: float = 5.0

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError(f"Port must be 1-65535, got {v}")
        return v
```
