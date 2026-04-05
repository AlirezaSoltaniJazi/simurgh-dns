# Contributing to simurgh-dns

Thank you for your interest in contributing! This guide will help you get set up and productive.

## Development Setup

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (package manager)

### Getting Started

1. Clone the repository:

```bash
git clone https://github.com/AlirezaSoltaniJazi/simurgh-dns.git
cd simurgh-dns
```

2. Install dependencies (including dev tools):

```bash
uv sync --all-extras
```

3. Install pre-commit hooks:

```bash
uv run pre-commit install
```

4. Verify everything works:

```bash
uv run pytest
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

## Code Style

- **Formatter/Linter:** [ruff](https://docs.astral.sh/ruff/) (configured in `pyproject.toml`)
- **Line length:** 88 characters
- **Quotes:** Double quotes
- **Type hints:** Modern Python 3.13+ syntax (`str | None`, `list[str]`, etc.)
- **Imports:** Absolute imports only, sorted by ruff/isort
- **Docstrings:** Google-style, only where the logic isn't self-evident

Pre-commit hooks will automatically format and lint your code on commit.

### Manual Formatting

```bash
# Format code
uv run ruff format src/ tests/

# Lint and auto-fix
uv run ruff check --fix src/ tests/
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=simurgh_dns

# Run a specific test file
uv run pytest tests/test_models.py

# Run tests matching a pattern
uv run pytest -k "test_benchmark"
```

## Project Structure

```
src/simurgh_dns/
├── __init__.py          # Package version
├── __main__.py          # python -m support
├── cli.py               # CLI entry point (argparse)
├── benchmark.py         # DNS benchmark engine
├── servers.py           # DNS provider registry
├── models.py            # Data models (BenchmarkResult)
├── display.py           # Rich terminal rendering
└── platform_dns/        # Cross-platform DNS setting
    ├── base.py          # Abstract base class
    ├── macos.py         # macOS (networksetup)
    ├── linux.py         # Linux (resolvectl / resolv.conf)
    └── windows.py       # Windows (netsh)
```

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with clear, focused commits
3. Ensure all tests pass and linting is clean
4. Open a pull request with a clear description of the change
5. Wait for review

## Reporting Issues

Please open an issue on GitHub with:

- A clear description of the problem or feature request
- Steps to reproduce (for bugs)
- Your OS and Python version
- Any relevant error output
