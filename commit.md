feat: Add GitHub Actions workflow for PyPI index updates and project setup

A new GitHub Actions workflow was added to automate publishing to PyPI and updating the index. The workflow:
- Builds and packages the Python project
- Clones and updates the PyPI index repository
- Generates HTML index files with package links and hashes
- Commits and pushes changes to the index repository

The following changes were made:
- Added `publish_to_pypi_pages.yml` workflow file
- Created `pyproject.toml` project configuration file
- Renamed `main()` function to `run()` in `main.py` for consistency

This enables automatic PyPI index updates when new releases are published.