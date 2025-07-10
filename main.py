import os
import sys
import re
__version__="0.1.1"

# --- ANSI Color Codes ---
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_MAGENTA = "\033[95m"
COLOR_CYAN = "\033[96m"
COLOR_RED = "\033[91m"

# --- Validation Functions ---
def is_valid_email(email):
    """Basic validation for email format."""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_version(version):
    """Basic validation for semantic versioning (X.Y.Z, X.Y.Z-pre.N, etc.)."""
    return re.match(r"^\d+\.\d+\.\d+(?:[-_][a-zA-Z0-9.]+)?$", version)

def is_valid_github_url(url):
    """Basic validation for GitHub repository URL format."""
    return re.match(r"^https://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+/?$", url)

def is_valid_python_entrypoint_reference(ref):
    """
    Validates if a string is a valid Python entry point reference.
    Format: importable.module:object.attr
    """
    # Requires at least one colon. Parts can contain alphanumeric, underscore, dot.
    # Starts with a letter or underscore, followed by alphanumeric, underscore, dot.
    # Colon separates module path from object/function name.
    return re.match(r"^[a-zA-Z_][a-zA-Z0-9_.]*:[a-zA-Z_][a-zA-Z0-9_.]*$", ref)


def get_input_with_env_default(prompt_text, env_var_name, description, clarification_text=None, mandatory=False, validator=None):
    """
    Prompts the user for input, pre-filling with an environment variable if available.
    Asks for confirmation if an environment variable is used.
    Includes a description for clarity and optional clarification text on a new line.
    Ensures input is not empty if 'mandatory' is True and validates with 'validator' if provided.
    """
    print(f"\n{COLOR_BLUE}{description}{COLOR_RESET}") # Description always on its own line above
    env_value = os.environ.get(env_var_name)
    
    if env_value:
        if validator and not validator(env_value):
            print(f"{COLOR_YELLOW}Warning: Environment variable '{env_var_name}' contains an invalid value: '{env_value}'. Please provide a new one.{COLOR_RESET}")
            env_value = None # Treat as if no env value was found
        else:
            while True:
                print(f"{COLOR_CYAN}{prompt_text}{COLOR_RESET}") # Main prompt text
                if clarification_text:
                    print(f"{COLOR_BLUE}{clarification_text}{COLOR_RESET}") # Clarification text on new line
                full_prompt = f"(found in {env_var_name}: {env_value}). Use this value? (Y/n): "
                response = input(f"{COLOR_YELLOW}> {COLOR_RESET}{full_prompt}").strip().lower() # User input line
                if response in ('y', ''):
                    return env_value
                elif response == 'n':
                    break
                else:
                    print(f"{COLOR_RED}Invalid input. Please enter 'y' or 'n'.{COLOR_RESET}")
    
    # If env_value not present or not confirmed, or invalid
    while True:
        print(f"{COLOR_CYAN}{prompt_text}{COLOR_RESET}") # Main prompt text
        if clarification_text:
            print(f"{COLOR_BLUE}{clarification_text}{COLOR_RESET}") # Clarification text on new line
        value = input(f"{COLOR_YELLOW}> {COLOR_RESET}").strip() # User input line
        if not value and mandatory:
            print(f"{COLOR_RED}This field cannot be empty. Please provide a value.{COLOR_RESET}")
        elif value and validator and not validator(value):
            print(f"{COLOR_RED}Invalid format. Please check the required format and try again.{COLOR_RESET}")
        else:
            return value

def get_mandatory_input(prompt_text, clarification_text=None, validator=None):
    """Prompts the user for a mandatory input, ensuring it's not empty and validates with 'validator' if provided."""
    while True:
        print(f"{COLOR_CYAN}{prompt_text}{COLOR_RESET}") # Main prompt text
        if clarification_text:
            print(f"{COLOR_BLUE}{clarification_text}{COLOR_RESET}") # Clarification text on new line
        value = input(f"{COLOR_YELLOW}> {COLOR_RESET}").strip() # User input line
        if not value:
            print(f"{COLOR_RED}This field cannot be empty. Please provide a value.{COLOR_RESET}")
        elif validator and not validator(value):
            print(f"{COLOR_RED}Invalid format. Please check the required format and try again.{COLOR_RESET}")
        else:
            return value

def generate_pyproject_toml(package_name, package_version, your_name, your_email, short_description, package_github_url, cli_command_name=None, cli_entry_point=None):
    """Generates the content for pyproject.toml."""
    pyproject_content = f"""
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{package_name}"
version = "{package_version}"
authors = [
  {{ name="{your_name}", email="{your_email}" }},
]
description = "{short_description}"
readme = "README.md"

# Optional: Define minimum Python version, classifiers, and dependencies.
# requires-python = ">=3.8, <3.13" # Example: Python 3.8 to 3.12
# classifiers = [
#     "Programming Language :: Python :: 3",
#     "License :: OSI Approved :: MIT License",
#     "Operating System :: OS Independent",
#     "Topic :: Multimedia :: Sound/Audio :: Speech",
#     "Environment :: Console",
# ]
# dependencies = [
#     "torch",
#     "transformers",
#     "soundfile",
#     "sounddevice",
#     "numpy",
#     "huggingface_hub",
#     "parler_tts",
#     "llama-cpp-python",
#     "orpheus-cpp",
# ]

# Optional: If your package is a command-line tool, define entry points.
# This makes your script executable directly from the command line after installation.
# [project.scripts]
# Example: your-cli-command = "your_package_name.main:run_cli"
# Adjust 'your_package_name.main' to match your actual package structure and entry point.
"""
    if cli_command_name and cli_entry_point:
        pyproject_content += f"""
[project.scripts]
{cli_command_name} = "{cli_entry_point}"
"""

    pyproject_content += f"""
[project.urls]
"Homepage" = "{package_github_url}"
"Bug Tracker" = "{package_github_url}/issues"
"""
    return pyproject_content.strip()

def generate_workflow_yml(github_username, pypi_index_repo_name, pat_secret_name):
    """Generates the content for the GitHub Actions workflow file."""
    workflow_content = f"""
name: Publish to GitHub Pages PyPI Index

on:
  release:
    types: [published] # This workflow runs when a new GitHub Release is published
  workflow_dispatch: # Allows manual triggering from GitHub Actions tab

jobs:
  build_and_publish:
    runs-on: ubuntu-latest
    permissions:
      contents: write # Needed for actions/checkout and git push

    steps:
      - name: Checkout Package Repository
        uses: actions/checkout@v4
        with:
          # Ensure full history is fetched for build tools if needed
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12' # Use a specific Python version, e.g., '3.10'

      - name: Install build tools and HTML parser
        run: |
          pip install build twine wheel toml beautifulsoup4

      - name: Build sdist and wheel
        run: |
          python -m build
        # The built packages will be in the 'dist/' directory of the package repo

      - name: Checkout PyPI Index Repository
        uses: actions/checkout@v4
        with:
          repository: {github_username}/{pypi_index_repo_name}
          path: my-python-index-repo # Local path to clone the index repo
          token: ${{ secrets.{pat_secret_name} }} # Use the PAT secret

      - name: Copy dists and Update PyPI Index HTML Files
        run: |
          # Get the package name directly from the original pyproject.toml
          # The original repo is one directory level up from 'my-python-index-repo'
          PACKAGE_NAME_RAW=$(python -c "import toml; print(toml.load('./pyproject.toml')['project']['name'])")
          PACKAGE_NAME=$(echo "$PACKAGE_NAME_RAW" | tr '_' '-' | tr '[:upper:]' '[:lower:]')
          export PACKAGE_NAME # Make it available as an environment variable for the Python script

          echo "Processing package: $PACKAGE_NAME"

          # Create package-specific directory in the index repo
          mkdir -p my-python-index-repo/$PACKAGE_NAME

          # Copy built distribution files into the package-specific directory
          cp dist/* my-python-index-repo/$PACKAGE_NAME/

          # Navigate into the cloned index repo to perform HTML updates
          cd my-python-index-repo

          # Execute Python script to handle HTML updates
          python - <<EOF
          import os
          import hashlib
          from bs4 import BeautifulSoup
          import sys

          # PACKAGE_NAME is now available as a shell variable, passed into the script
          PACKAGE_NAME = os.environ.get("PACKAGE_NAME")
          if not PACKAGE_NAME:
              print("Error: PACKAGE_NAME environment variable is not set for the Python script.")
              sys.exit(1)

          print(f"Python script processing for package: {{PACKAGE_NAME}}")

          # --- Handle package-specific index.html ---
          package_dir_path = PACKAGE_NAME # Relative path within my-python-index-repo
          package_index_html_path = os.path.join(package_dir_path, "index.html")

          # Always regenerate the package's index.html to ensure it's up-to-date with current dist files
          html_content = f\"\"\"
          <!DOCTYPE html>
          <html>
          <head>
              <title>Links for {{PACKAGE_NAME}}</title>
          </head>
          <body>
              <h1>Links for {{PACKAGE_NAME}}</h1>
          </body>
          </html>
          \"\"\"
          soup = BeautifulSoup(html_content, 'html.parser')
          body = soup.find('body')

          if os.path.exists(package_dir_path):
              for filename in sorted(os.listdir(package_dir_path)):
                  if filename.endswith(('.whl', '.tar.gz')):
                      filepath = os.path.join(package_dir_path, filename)
                      with open(filepath, 'rb') as f:
                          sha256_hash = hashlib.sha256(f.read()).hexdigest()
                      link = soup.new_tag("a", href=f"{{filename}}#sha256={{sha256_hash}}")
                      link.string = filename
                      body.append(link)
                      body.append(soup.new_tag("br"))
          else:
              print(f"Warning: Package directory '{{package_dir_path}}' not found within index repo. Skipping package index creation.")

          with open(package_index_html_path, "w") as f:
              f.write(str(soup))
          print(f"Successfully updated {{package_index_html_path}}")

          # --- Update the root index.html ---
          root_index_path = "index.html"
          root_soup = None
          if os.path.exists(root_index_path):
              with open(root_index_path, "r") as f:
                  root_soup = BeautifulSoup(f, 'html.parser')
          else:
              root_soup = BeautifulSoup("<!DOCTYPE html><html><head><title>Simple Index</title></head><body><h1>Simple Index</h1></body></html>", 'html.parser')

          root_body = root_soup.find('body')

          # Check if link already exists for this package
          existing_link = root_body.find('a', href=f"{{PACKAGE_NAME}}/".lower()) # Ensure lowercase for comparison
          if not existing_link:
              link_tag = root_soup.new_tag("a", href=f"{{PACKAGE_NAME}}/")
              link_tag.string = PACKAGE_NAME
              root_body.append(link_tag)
              root_body.append(soup.new_tag("br")) # Use soup.new_tag for <br>
              with open(root_index_path, "w") as f:
                  f.write(str(root_soup))
              print(f"Added new link for {{PACKAGE_NAME}} to {{root_index_path}}")
          else:
              print(f"Link for {{PACKAGE_NAME}} already exists in {{root_index_path}}. No update needed for root index.")
          EOF

      - name: Configure Git for committing
        run: |
          cd my-python-index-repo
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git config user.name "github-actions[bot]"
          git add .
          git commit -m "Auto-update PyPI index for ${{ github.event.repository.name }} v${{ github.event.release.tag_name || 'latest' }} [skip ci]" || echo "No changes to commit" # '|| echo' prevents failure if no changes
          git push
"""
    return workflow_content.strip()

def run():
    try:
        while True: # Loop for restart option
            print(f"{COLOR_GREEN}--- Python Package & GitHub Pages PyPI Publisher Setup ---{COLOR_RESET}")
            print("This script will generate 'pyproject.toml' and '.github/workflows/publish_to_pypi_pages.yml'.")
            print("-" * 60)

            # Part 1: Your Python Package Details (All mandatory with validation)
            package_name = get_mandatory_input(
                "1. What is the name of your Python package?",
                clarification_text="(This will be used in pyproject.toml and for the index URL, e.g., 'my-awesome-package')"
            )
            package_version = get_mandatory_input(
                "2. What is the initial version of your package?",
                clarification_text="(e.g., '0.1.0')",
                validator=is_valid_version
            )
            
            # Clarified prompts for author details with email validation
            your_name = get_mandatory_input(
                "3. What is your full name?",
                clarification_text="(This will be listed as a package author in pyproject.toml)"
            )
            your_email = get_mandatory_input(
                "4. What is your email address?",
                clarification_text="(This will be listed as a package author in pyproject.toml)",
                validator=is_valid_email
            )
            
            short_description = get_mandatory_input(
                "5. Provide a short, one-sentence description of your package:"
            )

            cli_command_name = None
            cli_entry_point = None
            # Question 6 defaults to 'n' if empty, and validates 'y'/'n'
            while True:
                has_cli_input = input("6. Does your package have a command-line entry point? (y/N): ").strip().lower()
                if has_cli_input in ('y', 'n', ''):
                    has_cli = True if has_cli_input == 'y' else False # Default to False if not 'y'
                    break
                else:
                    print(f"{COLOR_RED}Invalid input. Please enter 'y' or 'n'.{COLOR_RESET}")

            if has_cli:
                cli_command_name = get_mandatory_input(
                    "   What is the command name?", 
                    clarification_text="   (e.g., 'your-cli-command')"
                )
                cli_entry_point = get_mandatory_input(
                    "   What is the Python path to the entry function?", 
                    clarification_text="   (e.g., 'your_package_name.main:run_cli' - remember the colon ':'!)", # Emphasize colon
                    validator=is_valid_python_entrypoint_reference # New validation
                )

            package_github_url = get_mandatory_input(
                "7. What is the full GitHub URL for *this* Python package's repository?",
                clarification_text="(e.g., 'https://github.com/your-username/your-package-repo')",
                validator=is_valid_github_url
            )
            print("-" * 60)

            # Part 2: Shared GitHub Configuration (Environment Variable Pre-fill & Confirm)
            print(f"\n{COLOR_GREEN}--- Shared GitHub Configuration (can be pre-filled from environment variables) ---{COLOR_RESET}")
            print("These settings are typically consistent across all your projects using the same PyPI index.")
            
            github_username = get_input_with_env_default(
                "Your GitHub Username", 
                "GITHUB_USERNAME", 
                "  * Your GitHub username.",
                clarification_text="    (e.g., 'octocat'). Used to construct the GitHub Pages URL.",
                mandatory=True
            )
            pypi_index_repo_name = get_input_with_env_default(
                "GitHub Pages Index Repository Name", 
                "PYPI_INDEX_REPO_NAME", 
                "  * The name of the GitHub repository you use to host your custom PyPI index.",
                clarification_text="    (e.g., 'python-index').",
                mandatory=True
            )
            pat_secret_name = get_input_with_env_default(
                "GitHub PAT Secret Name", 
                "PAT_SECRET_NAME", 
                "  * The name of the GitHub Secret in your *package* repository.",
                clarification_text="    (e.g., 'GH_PAT_INDEX_REPO'). This secret stores your Personal Access Token.",
                mandatory=True
            )
            print("-" * 60)

            # --- Final Summary and Confirmation ---
            print(f"\n{COLOR_MAGENTA}--- Summary of Information Provided ---{COLOR_RESET}")
            print("Based on your input, the script will generate files to automate publishing your package.")
            print("Please review the details below:")
            print("-" * 60)
            print(f"\n{COLOR_CYAN}**Python Package Details (for `pyproject.toml`):**{COLOR_RESET}")
            print(f"  Package Name:         {package_name}")
            print(f"  Package Version:      {package_version}")
            print(f"  Author Name:          {your_name}")
            print(f"  Author Email:         {your_email}")
            print(f"  Description:          {short_description}")
            if cli_command_name:
                print(f"  CLI Command:          {cli_command_name}")
                print(f"  CLI Entry Point:      {cli_entry_point}")
            print(f"  Package GitHub URL:   {package_github_url}")
            print(f"\n{COLOR_CYAN}**GitHub Automation Details (for `.github/workflows/publish_to_pypi_pages.yml`):**{COLOR_RESET}")
            print(f"  GitHub Username:      {github_username}")
            print(f"  PyPI Index Repo:      {pypi_index_repo_name}")
            print(f"  PAT Secret Name:      {pat_secret_name}")
            print("-" * 60)

            confirm = input(f"{COLOR_YELLOW}Does this look correct? (y/n) [y=continue, n=restart]: {COLOR_RESET}").strip().lower()
            if confirm in ('y', ''):
                break # Exit the loop and proceed
            elif confirm == 'n':
                print(f"{COLOR_YELLOW}\nRestarting input process...{COLOR_RESET}\n")
                continue # Loop again
            else:
                print(f"{COLOR_RED}Invalid input. Please enter 'y' or 'n'. Restarting...{COLOR_RESET}\n")
                continue # Loop again

        # Generate pyproject.toml content
        pyproject_content = generate_pyproject_toml(
            package_name=package_name,
            package_version=package_version,
            your_name=your_name,
            your_email=your_email,
            short_description=short_description,
            package_github_url=package_github_url,
            cli_command_name=cli_command_name,
            cli_entry_point=cli_entry_point
        )

        # Generate workflow YAML content
        workflow_content = generate_workflow_yml(
            github_username=github_username,
            pypi_index_repo_name=pypi_index_repo_name,
            pat_secret_name=pat_secret_name
        )

        # Create files
        pyproject_path = "pyproject.toml"
        workflow_dir = os.path.join(".github", "workflows")
        workflow_path = os.path.join(workflow_dir, "publish_to_pypi_pages.yml")

        # Write pyproject.toml
        with open(pyproject_path, "w") as f:
            f.write(pyproject_content)
        print(f"\n{COLOR_GREEN}Created: {pyproject_path}{COLOR_RESET}")

        # Create .github/workflows directory if it doesn't exist
        os.makedirs(workflow_dir, exist_ok=True)

        # Write workflow YAML
        with open(workflow_path, "w") as f:
            f.write(workflow_content)
        print(f"{COLOR_GREEN}Created: {workflow_path}{COLOR_RESET}")

        print(f"\n{COLOR_GREEN}--- Setup Complete! ---{COLOR_RESET}")
        print("Please follow these crucial next steps:")
        print(f"{COLOR_CYAN}1.  **Project Structure:** Ensure your Python code is correctly structured.{COLOR_RESET}")
        print("    For example, if your package name is 'my-package', your main code should be in:")
        print("    `./src/my_package/__init__.py` and other modules like `./src/my_package/main.py`")
        print("    If you specified a CLI entry point, ensure that path is correct.")
        print(f"{COLOR_CYAN}2.  **GitHub Pages Setup:** Go to your GitHub Pages index repository (e.g., `https://github.com/{github_username}/{pypi_index_repo_name}`).{COLOR_RESET}")
        print("    In 'Settings' -> 'Pages', ensure GitHub Pages is enabled from the `main` branch (or your default branch) and the `/root` folder.")
        print(f"{COLOR_CYAN}3.  **GitHub PAT Secret:** You *must* have created a GitHub Personal Access Token (PAT) with `repo` scope (or fine-grained `contents: write` for your index repo).{COLOR_RESET}")
        print(f"    Add this PAT as a secret named `{pat_secret_name}` in your *current* Python package's GitHub repository settings (Settings -> Secrets and variables -> Actions).")
        print(f"{COLOR_CYAN}4.  **Commit & Push:** Commit the newly generated `pyproject.toml` and `.github/workflows/publish_to_pypi_pages.yml` files to your *current* Python package's GitHub repository.{COLOR_RESET}")
        print("    `git add .`")
        print("    `git commit -m \"Initial project setup with PyPI Pages automation\"`")
        print("    `git push origin main` (or your default branch)")
        print(f"{COLOR_CYAN}5.  **Trigger Workflow:** Create a new GitHub Release in your *current* Python package's GitHub repository (e.g., `v{package_version}`). This will trigger the GitHub Actions workflow.{COLOR_RESET}")
        print(f"\n{COLOR_GREEN}Good luck with your project!{COLOR_RESET}")
    except KeyboardInterrupt:
            print(f"\n{COLOR_GREEN}Closing script!{COLOR_RESET}")
            exit(0)       
    except Exception as e:
        print(f"{COLOR_RED}\nAn error occurred: {e}{COLOR_RESET}", file=sys.stderr)
        print(f"{COLOR_RED}Setup failed. Please check permissions or try again.{COLOR_RESET}", file=sys.stderr)

if __name__ == "__main__":
    run()
