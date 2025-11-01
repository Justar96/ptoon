# Publishing ptoon to PyPI

This guide explains how to publish the ptoon package to PyPI (Python Package Index).

## Prerequisites

### 1. PyPI Accounts

Create accounts on both platforms:

- **TestPyPI** (for testing): https://test.pypi.org/account/register/
- **PyPI** (production): https://pypi.org/account/register/

### 2. GitHub Environments

The publish workflow uses GitHub environments with trusted publishing (no API tokens needed!).

#### Set up environments in GitHub:

1. Go to your repository Settings > Environments
2. Create two environments:
   - `testpypi` - for TestPyPI releases
   - `pypi` - for production PyPI releases
3. For each environment, configure:
   - **Deployment protection rules** (optional but recommended):
     - Required reviewers (for production releases)
     - Wait timer (optional delay before deployment)

#### Configure Trusted Publishers:

**For TestPyPI:**
1. Log in to https://test.pypi.org
2. Go to Account Settings > Publishing
3. Add a new pending publisher:
   - PyPI Project Name: `ptoon`
   - Owner: `Justar96`
   - Repository: `ptoon`
   - Workflow: `publish.yml`
   - Environment: `testpypi`

**For PyPI:**
1. Log in to https://pypi.org
2. Go to Account Settings > Publishing
3. Add a new pending publisher:
   - PyPI Project Name: `ptoon`
   - Owner: `Justar96`
   - Repository: `ptoon`
   - Workflow: `publish.yml`
   - Environment: `pypi`

> Note: After the first successful publish, the project will be registered and future publishes will use the same trusted publisher configuration.

## Release Process

### Step 1: Prepare the Release

1. **Update version number** in two places:
   - `pyproject.toml` (line 7): `version = "X.Y.Z"`
   - `ptoon/__init__.py` (line 44): `__version__ = "X.Y.Z"`

2. **Update changelog** in `docs/changelog.rst`:
   ```rst
   Version X.Y.Z (YYYY-MM-DD)
   --------------------------

   **New Features:**

   - Feature description

   **Bug Fixes:**

   - Bug fix description

   **Breaking Changes:**

   - Breaking change description (if any)
   ```

3. **Run tests locally**:
   ```bash
   uv run pytest
   uv run ruff check .
   uv run mypy ptoon
   ```

4. **Build and test locally**:
   ```bash
   # Clean previous builds
   rm -rf dist/ build/ *.egg-info

   # Build the package
   uv run python -m build

   # Verify the package contents
   uv run python -m zipfile -l dist/ptoon-X.Y.Z-py3-none-any.whl

   # Test installation in a clean environment
   python -m venv test_env
   test_env/bin/pip install dist/ptoon-X.Y.Z-py3-none-any.whl
   test_env/bin/python -c "import ptoon; print(ptoon.__version__)"
   rm -rf test_env
   ```

### Step 2: Commit and Tag

1. **Commit version changes**:
   ```bash
   git add pyproject.toml ptoon/__init__.py docs/changelog.rst
   git commit -m "Bump version to X.Y.Z"
   ```

2. **Create and push tag**:
   ```bash
   git tag -a vX.Y.Z -m "Release version X.Y.Z"
   git push origin main
   git push origin vX.Y.Z
   ```

### Step 3: Test on TestPyPI (Recommended)

Before publishing to production PyPI, test on TestPyPI:

1. Go to GitHub Actions: https://github.com/Justar96/ptoon/actions
2. Select the "Publish to PyPI" workflow
3. Click "Run workflow"
4. Select:
   - Branch: `main`
   - Environment: `testpypi`
5. Click "Run workflow"

6. **Verify the TestPyPI upload**:
   - Check the package: https://test.pypi.org/project/ptoon/
   - Test installation:
     ```bash
     pip install --index-url https://test.pypi.org/simple/ ptoon
     ```

### Step 4: Publish to PyPI

**Option A: Automatic (via GitHub Release)**

1. Go to https://github.com/Justar96/ptoon/releases/new
2. Select the tag you created: `vX.Y.Z`
3. Release title: `Version X.Y.Z`
4. Description: Copy the changelog for this version
5. Click "Publish release"
6. The GitHub Action will automatically build and publish to PyPI

**Option B: Manual (via GitHub Actions)**

1. Go to GitHub Actions: https://github.com/Justar96/ptoon/actions
2. Select the "Publish to PyPI" workflow
3. Click "Run workflow"
4. Select:
   - Branch: `main` (or the tag `vX.Y.Z`)
   - Environment: `pypi`
5. Click "Run workflow"

### Step 5: Verify the Release

1. **Check PyPI**: https://pypi.org/project/ptoon/
2. **Test installation**:
   ```bash
   pip install ptoon
   python -c "import ptoon; print(ptoon.__version__)"
   ```
3. **Update README badge** (optional):
   ```markdown
   [![PyPI version](https://badge.fury.io/py/ptoon.svg)](https://pypi.org/project/ptoon/)
   ```

## Troubleshooting

### Build fails with "metadata missing"

This is usually a configuration issue in `pyproject.toml`. Verify:
- All required fields are present (name, version, description, etc.)
- Project URLs are properly formatted
- Author email is valid

### Trusted publishing fails

If the trusted publisher configuration fails:
1. Verify the environment name matches exactly
2. Check that the repository owner and name are correct
3. Ensure the workflow file path is correct (`publish.yml`)
4. Make sure the PyPI project name is available or already claimed by you

### Package already exists on PyPI

PyPI doesn't allow overwriting published versions. You must:
1. Increment the version number
2. Create a new tag
3. Publish the new version

## Manual Publishing (Alternative)

If you prefer to publish manually without GitHub Actions:

1. **Install dependencies**:
   ```bash
   uv sync --extra dev
   ```

2. **Build the package**:
   ```bash
   uv run python -m build
   ```

3. **Upload to TestPyPI** (test first):
   ```bash
   uv run twine upload --repository testpypi dist/*
   ```
   Username: `__token__`
   Password: Your TestPyPI API token

4. **Upload to PyPI** (production):
   ```bash
   uv run twine upload dist/*
   ```
   Username: `__token__`
   Password: Your PyPI API token

### Creating API Tokens (for manual publishing)

**TestPyPI:**
1. Log in to https://test.pypi.org
2. Go to Account Settings > API tokens
3. Create a new API token with scope for the `ptoon` project
4. Save the token securely (starts with `pypi-`)

**PyPI:**
1. Log in to https://pypi.org
2. Go to Account Settings > API tokens
3. Create a new API token with scope for the `ptoon` project
4. Save the token securely (starts with `pypi-`)

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR version** (X.0.0): Incompatible API changes
- **MINOR version** (0.X.0): New functionality, backward compatible
- **PATCH version** (0.0.X): Bug fixes, backward compatible

Examples:
- `0.0.1` - Initial development release
- `0.1.0` - First minor release with new features
- `1.0.0` - First stable release
- `1.0.1` - Bug fix for 1.0.0
- `1.1.0` - New features added to 1.0.0

## Checklist

Before each release, verify:

- [ ] All tests pass (`uv run pytest`)
- [ ] Linting passes (`uv run ruff check .`)
- [ ] Type checking passes (`uv run mypy ptoon`)
- [ ] Version updated in `pyproject.toml` and `ptoon/__init__.py`
- [ ] Changelog updated in `docs/changelog.rst`
- [ ] Changes committed and pushed to `main`
- [ ] Git tag created and pushed
- [ ] Package tested on TestPyPI (optional but recommended)
- [ ] GitHub Release created or workflow manually triggered
- [ ] Package verified on PyPI
- [ ] Installation tested from PyPI

## References

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Trusted Publishing Guide](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions Publishing](https://packaging.python.org/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
