"""Implementation of the `gentem add` command to add modules to existing projects."""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from rich import print
from rich.panel import Panel

from gentem.template_engine import TemplateEngine
from gentem.utils.validators import (
    ValidationError,
    validate_module_type,
    validate_project_path,
)


# Valid module types
VALID_MODULES = {
    "docker",
    "docs",
    "testing",
    "logging",
    "database",
    "ci",
    "precommit",
    "poetry",
}


def detect_project_type(project_path: Path) -> Optional[str]:
    """Detect the project type from pyproject.toml.

    Args:
        project_path: Path to the project directory.

    Returns:
        Project type string or None if not detected.
    """
    pyproject_path = project_path / "pyproject.toml"

    if not pyproject_path.exists():
        return None

    content = pyproject_path.read_text(encoding="utf-8")

    # Check for FastAPI
    if 'fastapi' in content.lower():
        return "fastapi"

    # Check for CLI (has [project.scripts] entry points in pyproject.toml)
    if '[project.scripts]' in content or 'project.scripts' in content:
        return "cli"

    # Check for setup.py style console_scripts (legacy)
    if 'console_scripts' in content:
        return "cli"

    # Check for library (has py.requires or similar)
    if 'py.' in content and 'dependencies' in content:
        return "library"

    return "generic"


def detect_project_info(project_path: Path) -> dict[str, Any]:
    """Detect project information from existing project files.

    Args:
        project_path: Path to the project directory.

    Returns:
        Dictionary with project information.
    """
    project_type = detect_project_type(project_path)
    pyproject_path = project_path / "pyproject.toml"

    # Defaults
    info = {
        "project_name": project_path.name,
        "project_slug": project_path.name.lower().replace("_", "-"),
        "class_name": "".join(word.capitalize() for word in project_path.name.split("_")),
        "project_type": project_type or "generic",
        "author": "Gentem User",
        "email": f"user@{project_path.name.lower()}.dev",
        "description": "",
        "version": "0.1.0",
        "python_version": "3.10",
        "python_versions": ["3.10", "3.11", "3.12"],
        "year": datetime.now().year,
        "month": datetime.now().strftime("%B"),
    }

    if pyproject_path.exists():
        content = pyproject_path.read_text(encoding="utf-8")

        # Extract project name from [project] or [tool.poetry] section
        name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
        if name_match:
            info["project_name"] = name_match.group(1)
            info["project_slug"] = name_match.group(1).lower().replace("_", "-")
            info["class_name"] = "".join(
                word.capitalize() for word in name_match.group(1).split("_")
            )

        # Extract author
        author_match = re.search(r'author\s*=\s*["\']([^"\']+)["\']', content)
        if author_match:
            info["author"] = author_match.group(1)

        # Extract email
        email_match = re.search(r'email\s*=\s*["\']([^"\']+)["\']', content)
        if email_match:
            info["email"] = email_match.group(1)

        # Extract description
        desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
        if desc_match:
            info["description"] = desc_match.group(1)

        # Extract version
        version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if version_match:
            info["version"] = version_match.group(1)

        # Extract python requirement
        py_match = re.search(r'python\s*["\']?\^?["\']?\s*["\']?([0-9.]+)["\']?', content)
        if py_match:
            info["python_version"] = py_match.group(1)

    return info


def get_module_templates(module_type: str, project_type: str) -> list[tuple[str, str]]:
    """Get list of template files to render for a module.

    Args:
        module_type: Type of module to add.
        project_type: Type of project (fastapi, cli, library, generic).

    Returns:
        List of (template_path, output_path) tuples.
    """
    templates = []

    if module_type == "docker":
        templates = [
            ("add/docker/Dockerfile.j2", "Dockerfile"),
            ("add/docker/.dockerignore.j2", ".dockerignore"),
            ("add/docker/docker-compose.yml.j2", "docker-compose.yml"),
        ]

    elif module_type == "docs":
        templates = [
            ("add/docs/mkdocs.yml.j2", "mkdocs.yml"),
            ("add/docs/docs/index.md.j2", "docs/index.md"),
            ("add/docs/docs/api.md.j2", "docs/api.md"),
            ("add/docs/docs/getting-started.md.j2", "docs/getting-started.md"),
        ]

    elif module_type == "testing":
        templates = [
            ("add/testing/conftest.py.j2", "tests/conftest.py"),
            ("add/testing/test_core.py.j2", "tests/test_core.py"),
        ]
        if project_type == "fastapi":
            templates.append(("add/testing/test_api.py.j2", "tests/test_api.py"))

    elif module_type == "logging":
        templates = [
            ("add/logging/logging.yaml.j2", "logging.yaml"),
        ]
        if project_type == "fastapi":
            templates.append(("add/logging/app/logging.py.j2", "app/logging.py"))
        elif project_type == "cli":
            templates.append(("add/logging/src/logging_config.py.j2", "src/logging_config.py"))
        else:
            templates.append(("add/logging/src/logging_config.py.j2", "src/logging_config.py"))

    elif module_type == "database":
        templates = [
            ("add/database/alembic.ini.j2", "alembic.ini"),
            ("add/database/alembic/env.py.j2", "alembic/env.py"),
            ("add/database/alembic/script.py.mako.j2", "alembic/script.py.mako"),
        ]

    elif module_type == "ci":
        templates = [
            ("add/ci/.github/workflows/ci.yml.j2", ".github/workflows/ci.yml"),
        ]

    elif module_type == "precommit":
        templates = [
            ("add/precommit/.pre-commit-config.yaml.j2", ".pre-commit-config.yaml"),
        ]

    elif module_type == "poetry":
        templates = [
            ("add/poetry/pyproject.toml.j2", "pyproject.toml"),
        ]

    return templates


def add_module(
    module_type: str,
    project_path: str = ".",
    dry_run: bool = False,
    verbose: bool = False,
    force: bool = False,
) -> None:
    """Add a module to an existing project.

    Args:
        module_type: Type of module to add (docker, docs, testing, logging, database, ci, precommit, poetry).
        project_path: Path to the existing project.
        dry_run: Preview without creating files.
        verbose: Show verbose output.
        force: Overwrite existing files without prompting.
    """
    # Validate inputs
    try:
        module_type = validate_module_type(module_type)
        project_path = validate_project_path(project_path)
    except ValidationError as e:
        print(f"[red]Error: {e}[/]")
        raise SystemExit(1) from e

    # Detect project information
    context = detect_project_info(project_path)

    if verbose:
        print(f"Project path: {project_path}")
        print(f"Project type: {context['project_type']}")
        print(f"Project name: {context['project_name']}")
        print(f"Module type: {module_type}")
        print(f"Force mode: {force}")

    # Get templates for this module
    template_files = get_module_templates(module_type, context["project_type"])

    if not template_files:
        print(f"[red]Error: No templates found for module type: {module_type}[/]")
        raise SystemExit(1)

    # Show summary
    print(
        Panel(
            f"[bold]Adding {module_type} module to:[/] [cyan]{project_path.name}[/]\n"
            f"[dim]Project type:[/] {context['project_type']}\n"
            f"[dim]Version:[/] {context['version']}",
            title="Gentem (add)",
            expand=False,
        )
    )

    if dry_run:
        print("[yellow]DRY RUN - No files will be created[/]")
        print(f"\nFiles that would be created/modified:")
        for _, output_file in template_files:
            output_path = project_path / output_file
            if output_path.exists():
                print(f"  - [yellow]{output_file}[/] (update)")
            else:
                print(f"  - [green]{output_file}[/] (create)")
        return

    # Initialize template engine
    engine = TemplateEngine()

    # Render and write files
    try:
        for template_path, output_file in template_files:
            output_path = project_path / output_file

            # Check if file exists and we're not forcing
            if output_path.exists() and not force:
                print(f"  [yellow]?[/] {output_file} (exists, use --force to overwrite)")
                continue

            # Render content
            content = engine.render_template(template_path, context)

            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write the file
            output_path.write_text(content, encoding="utf-8")

            action = "Updated" if output_path.exists() else "Created"
            print(f"  [green]✓[/] {action}: {output_file}")

        print(f"\n[green]✓ {module_type} module added successfully![/]")

        # Show next steps
        next_steps = get_next_steps(module_type, context["project_type"])
        if next_steps:
            print("\nNext steps:")
            for step in next_steps:
                print(f"  {step}")

    except Exception as e:
        print(f"[red]Error adding module: {e}[/]")
        raise SystemExit(1) from e


def add_modules(
    module_types: list[str],
    project_path: str = ".",
    dry_run: bool = False,
    verbose: bool = False,
    force: bool = False,
) -> None:
    """Add multiple modules to an existing project.

    Args:
        module_types: List of module types to add.
        project_path: Path to the existing project.
        dry_run: Preview without creating files.
        verbose: Show verbose output.
        force: Overwrite existing files without prompting.
    """
    for module_type in module_types:
        add_module(
            module_type=module_type,
            project_path=project_path,
            dry_run=dry_run,
            verbose=verbose,
            force=force,
        )
        if module_type != module_types[-1]:
            print()  # Add spacing between modules


def get_next_steps(module_type: str, project_type: str) -> list[str]:
    """Get next steps after adding a module.

    Args:
        module_type: Type of module added.
        project_type: Type of project.

    Returns:
        List of next step instructions.
    """
    steps = []

    if module_type == "docker":
        steps.append("docker build -t myapp .")
        steps.append("docker-compose up -d")

    elif module_type == "docs":
        steps.append("pip install mkdocs mkdocstrings")
        steps.append("mkdocs serve")

    elif module_type == "testing":
        steps.append("pip install pytest pytest-asyncio")
        steps.append("pytest tests/")

    elif module_type == "logging":
        steps.append("Install requirements: pip install pyyaml rich")

    elif module_type == "database":
        steps.append("pip install alembic")
        steps.append("alembic revision --autogenerate -m 'initial'")
        steps.append("alembic upgrade head")

    elif module_type == "ci":
        steps.append("git add .")
        steps.append("git commit -m 'Add CI workflow'")
        steps.append("git push origin main")

    elif module_type == "precommit":
        steps.append("pip install pre-commit")
        steps.append("pre-commit install")
        steps.append("pre-commit run --all-files")

    elif module_type == "poetry":
        steps.append("pip install poetry")
        steps.append("poetry install")
        steps.append("poetry add <package>")

    return steps
