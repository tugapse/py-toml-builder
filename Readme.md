# Python Package & GitHub PyPI Index Setup Tool

## 📦 Overview
This tool automates the setup of a Python package with PyPI index integration. It generates:
- `pyproject.toml` for package metadata
- GitHub Actions workflow for automatic PyPI index updates

Key features:
- CLI entry point configuration
- GitHub Pages PyPI index integration
- Environment variable pre-filling
- Interactive input validation

## 📦 Installation
1. Ensure Python 3.12 is installed
2. Run the script directly:
```bash
python main.py
```

## 🚀 Usage
1. Run the script:
```bash
python main.py
```
2. Follow the interactive prompts to:
- Enter package details
- Configure GitHub settings
- Choose CLI options (optional)
3. The script will:
- Generate `pyproject.toml`
- Create `.github/workflows/publish_to_pypi_pages.yml`
- Output setup instructions

## ⚙️ Configuration
The script will prompt for:
- Package name (used in PyPI index)
- Initial version (semantic versioning)
- Author details
- Package description
- GitHub repository URL
- GitHub username
- PyPI index repo name
- PAT secret name

Optional CLI configuration:
- Command name (e.g., `tts-cli`)
- Entry point path (e.g., `your_package_name.main:run_cli`)

## 📚 Additional Resources
- [GitHub Pages PyPI Index Setup Guide](https://docs.github.com/en/enterprise-admin/setting-up-a-private-pypi-index)
- [PyPI Index Configuration Documentation](https://packaging.python.org/tutorials/pypirc/)
- [GitHub Actions Workflow Reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

## 📌 Notes
1. Ensure you have:
   - A GitHub Personal Access Token (PAT) with `repo` scope
   - A GitHub repository for your PyPI index
2. After setup:
   - Commit generated files to your package repository
   - Create a GitHub Release to trigger the workflow
   - Verify PyPI index updates in your index repo

This tool simplifies package setup while maintaining flexibility for custom configurations.