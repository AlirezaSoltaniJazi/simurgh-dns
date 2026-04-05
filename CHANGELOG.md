# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-04-05

### Added

- Update repo addresses

### Fixed

- Corrected GitHub repository URLs to `AlirezaSoltaniJazi/simurgh-dns`

## [0.1.0] - 2026-04-05

### Added

- Initial release of simurgh-dns
- DNS benchmark engine with concurrent testing of 15 providers (30 servers)
- Rich terminal output with ranked results table and progress bar
- Cross-platform DNS configuration (macOS, Linux, Windows)
- JSON output mode (`--json`)
- CLI flags: `--rounds`, `--set`, `--reset`, `--no-set`, `--version`
- Pre-commit hooks with ruff linting and formatting
- CI/CD workflows for testing and PyPI publishing
