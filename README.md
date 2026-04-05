# simurgh-dns

A cross-platform CLI tool to benchmark public DNS servers and set the fastest one.

## Features

- Benchmarks **15 DNS providers** (30 server IPs) with concurrent testing
- Measures **latency** (avg/min/max) and **reliability** per server
- Beautiful terminal output with Rich tables and progress bars
- **Cross-platform DNS configuration** — set the best DNS on macOS, Linux, and Windows
- JSON output mode for scripting and automation
- Installable via `pip` — works anywhere Python runs

## Installation

```bash
pip install simurgh-dns
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv pip install simurgh-dns
```

## Quick Start

Run the benchmark:

```bash
simurgh-dns
```

This will:

1. Benchmark all DNS servers (3 rounds by default)
2. Display a ranked table of results
3. Offer to set the fastest DNS on your system

## Usage

```bash
# Run benchmark with custom rounds
simurgh-dns --rounds 5

# Output results as JSON
simurgh-dns --json

# Benchmark only (don't offer to change DNS)
simurgh-dns --no-set

# Directly set a specific DNS server
simurgh-dns --set 1.1.1.1

# Reset DNS to DHCP default
simurgh-dns --reset

# Show version
simurgh-dns --version
```

You can also run it as a Python module:

```bash
python -m simurgh_dns
```

## Supported Platforms

| Platform | Benchmark | Set DNS | Method |
|----------|-----------|---------|--------|
| macOS | Yes | Yes | `networksetup` |
| Linux | Yes | Yes | `resolvectl` / `/etc/resolv.conf` |
| Windows | Yes | Yes | `netsh` |

> **Note:** Setting DNS requires elevated privileges (`sudo` on macOS/Linux, Administrator on Windows).

## DNS Providers

| Provider | Primary | Secondary |
|----------|---------|-----------|
| Google | 8.8.8.8 | 8.8.4.4 |
| Cloudflare | 1.1.1.1 | 1.0.0.1 |
| Quad9 | 9.9.9.9 | 149.112.112.112 |
| OpenDNS | 208.67.222.222 | 208.67.220.220 |
| AdGuard | 94.140.14.14 | 94.140.15.15 |
| NextDNS | 45.90.28.0 | 45.90.30.0 |
| CleanBrowsing | 185.228.168.9 | 185.228.169.9 |
| Comodo Secure | 8.26.56.26 | 8.20.247.20 |
| Level3 | 4.2.2.1 | 4.2.2.2 |
| Verisign | 64.6.64.6 | 64.6.65.6 |
| Norton/LifeLock | 199.85.126.10 | 199.85.127.10 |
| Yandex | 77.88.8.8 | 77.88.8.1 |
| DNS.WATCH | 84.200.69.80 | 84.200.70.40 |
| Freenom | 80.80.80.80 | 80.80.81.81 |
| Alternate DNS | 76.76.19.19 | 76.223.122.150 |

## Requirements

- Python 3.13+

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License. See [LICENSE](LICENSE) for details.
