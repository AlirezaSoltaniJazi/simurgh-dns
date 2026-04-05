# Publishing simurgh-dns to PyPI

This guide covers how to build and publish the package to PyPI.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed
- A [PyPI account](https://pypi.org/account/register/)
- A [TestPyPI account](https://test.pypi.org/account/register/) (recommended for testing)

## Build

```bash
uv build
```

This creates both a source distribution and a wheel in the `dist/` directory:

```
dist/
├── simurgh_dns-0.1.0.tar.gz
└── simurgh_dns-0.1.0-py3-none-any.whl
```

## Test on TestPyPI (Recommended)

Before publishing to the real PyPI, test with TestPyPI:

```bash
uv publish --publish-url https://test.pypi.org/legacy/
```

You will be prompted for your TestPyPI API token.

Verify the upload:

```bash
pip install --index-url https://test.pypi.org/simple/ simurgh-dns
```

## Publish to PyPI

Once verified:

```bash
uv publish
```

You will be prompted for your PyPI API token.

## Automated Publishing (GitHub Actions)

The project includes a GitHub Actions workflow (`.github/workflows/publish.yml`) that automatically publishes to PyPI when a version tag is pushed:

```bash
# Update version in src/simurgh_dns/__init__.py and pyproject.toml
# Commit the version bump
git tag v0.1.0
git push origin v0.1.0
```

The workflow uses PyPI trusted publishing (OIDC). To set this up:

1. Go to your PyPI project settings
2. Add a new trusted publisher
3. Set the GitHub repository and workflow file name

## Version Bumping

1. Update `version` in `pyproject.toml`
2. Update `__version__` in `src/simurgh_dns/__init__.py`
3. Commit with message: `Bump version to X.Y.Z`
4. Tag: `git tag vX.Y.Z`
5. Push: `git push origin main --tags`
