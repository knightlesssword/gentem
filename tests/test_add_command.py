"""Tests for the gentem add command module."""

import tempfile
from pathlib import Path

import pytest

from gentem.commands.add import (
    detect_project_info,
    detect_project_type,
    get_module_templates,
)
from gentem.utils.validators import (
    ValidationError,
    validate_module_type,
    validate_project_path,
)


class TestValidateModuleType:
    """Tests for validate_module_type function."""

    def test_valid_module_docker(self):
        """Test that 'docker' is a valid module type."""
        assert validate_module_type("docker") == "docker"

    def test_valid_module_docs(self):
        """Test that 'docs' is a valid module type."""
        assert validate_module_type("docs") == "docs"

    def test_valid_module_testing(self):
        """Test that 'testing' is a valid module type."""
        assert validate_module_type("testing") == "testing"

    def test_valid_module_logging(self):
        """Test that 'logging' is a valid module type."""
        assert validate_module_type("logging") == "logging"

    def test_valid_module_database(self):
        """Test that 'database' is a valid module type."""
        assert validate_module_type("database") == "database"

    def test_valid_module_ci(self):
        """Test that 'ci' is a valid module type."""
        assert validate_module_type("ci") == "ci"

    def test_valid_module_precommit(self):
        """Test that 'precommit' is a valid module type."""
        assert validate_module_type("precommit") == "precommit"

    def test_valid_module_poetry(self):
        """Test that 'poetry' is a valid module type."""
        assert validate_module_type("poetry") == "poetry"

    def test_case_insensitive(self):
        """Test that module type is case insensitive."""
        assert validate_module_type("DOCKER") == "docker"
        assert validate_module_type("Docs") == "docs"
        assert validate_module_type("TESTING") == "testing"
        assert validate_module_type("CI") == "ci"

    def test_invalid_module(self):
        """Test that invalid module type raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            validate_module_type("invalid")
        assert "Invalid module type" in str(exc_info.value)

    def test_empty_module(self):
        """Test that empty module type raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_module_type("")


class TestValidateProjectPath:
    """Tests for validate_project_path function."""

    def test_valid_path_with_pyproject(self):
        """Test validation with a valid pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            (project_path / "pyproject.toml").write_text("[project]\nname = 'test'")

            result = validate_project_path(str(project_path))
            assert result == project_path

    def test_nonexistent_path(self):
        """Test that nonexistent path raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            validate_project_path("/nonexistent/path")
        assert "does not exist" in str(exc_info.value)

    def test_file_instead_of_directory(self):
        """Test that a file path raises ValidationError."""
        with tempfile.NamedTemporaryFile() as tmpfile:
            with pytest.raises(ValidationError) as exc_info:
                validate_project_path(tmpfile.name)
            assert "not a directory" in str(exc_info.value)

    def test_directory_without_project_file(self):
        """Test that directory without project file raises ValidationError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValidationError) as exc_info:
                validate_project_path(tmpdir)
            assert "does not appear to be a valid project" in str(exc_info.value)


class TestDetectProjectType:
    """Tests for detect_project_type function."""

    def test_detect_fastapi(self):
        """Test FastAPI project detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            (project_path / "pyproject.toml").write_text("[project]\nname = 'test'\ndependencies = ['fastapi']")

            result = detect_project_type(project_path)
            assert result == "fastapi"

    def test_detect_cli_project_scripts(self):
        """Test CLI project detection with [project.scripts]."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            content = """
[project]
name = 'test-cli'
[project.scripts]
test-cli = "test_cli.main:main"
"""
            (project_path / "pyproject.toml").write_text(content)

            result = detect_project_type(project_path)
            assert result == "cli"

    def test_detect_cli_console_scripts(self):
        """Test CLI project detection with console_scripts (setup.py style)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            content = """
[project]
name = 'test-cli'

[project.scripts]
test-cli = "test_cli.main:main"
"""
            # The implementation also checks for console_scripts
            content_with_console = content + "\n[tool.setup_scripts]\nconsole_scripts = ['test-cli']"
            (project_path / "pyproject.toml").write_text(content_with_console)

            result = detect_project_type(project_path)
            assert result == "cli"

    def test_detect_library(self):
        """Test library project detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            content = """
[project]
name = 'test'
requires-python = '>=3.9'
"""
            (project_path / "pyproject.toml").write_text(content)

            result = detect_project_type(project_path)
            assert result == "generic"


class TestDetectProjectInfo:
    """Tests for detect_project_info function."""

    def test_detect_project_info(self):
        """Test that project info is detected from pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            content = """
[project]
name = 'my-test-project'
version = '1.2.3'
author = 'Test Author'
description = 'A test project'
"""
            (project_path / "pyproject.toml").write_text(content)

            info = detect_project_info(project_path)

            assert info["project_name"] == "my-test-project"
            assert info["project_slug"] == "my-test-project"
            assert info["version"] == "1.2.3"
            assert info["author"] == "Test Author"
            assert info["description"] == "A test project"

    def test_detect_project_info_defaults(self):
        """Test that defaults are used when info not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            (project_path / "pyproject.toml").write_text("[project]\nname = 'test'")

            info = detect_project_info(project_path)

            assert info["project_name"] == "test"
            assert info["version"] == "0.1.0"
            assert info["author"] == "Gentem User"


class TestGetModuleTemplates:
    """Tests for get_module_templates function."""

    def test_docker_templates(self):
        """Test Docker module templates."""
        templates = get_module_templates("docker", "generic")

        assert len(templates) == 3
        template_paths = [t[0] for t in templates]
        assert any("Dockerfile" in p for p in template_paths)
        assert any("docker-compose" in p for p in template_paths)

    def test_docs_templates(self):
        """Test Docs module templates."""
        templates = get_module_templates("docs", "generic")

        assert len(templates) == 4
        template_paths = [t[0] for t in templates]
        assert any("mkdocs.yml" in p for p in template_paths)
        assert any("index.md" in p for p in template_paths)

    def test_testing_templates(self):
        """Test Testing module templates."""
        templates = get_module_templates("testing", "generic")

        assert len(templates) == 2
        template_paths = [t[0] for t in templates]
        assert any("conftest.py" in p for p in template_paths)
        assert any("test_core.py" in p for p in template_paths)

    def test_testing_templates_fastapi(self):
        """Test Testing module templates for FastAPI."""
        templates = get_module_templates("testing", "fastapi")

        # Should include test_api.py for FastAPI
        assert len(templates) == 3
        template_paths = [t[0] for t in templates]
        assert any("test_api.py" in p for p in template_paths)

    def test_logging_templates(self):
        """Test Logging module templates."""
        templates = get_module_templates("logging", "generic")

        assert len(templates) == 2
        template_paths = [t[0] for t in templates]
        assert any("logging.yaml" in p for p in template_paths)

    def test_logging_templates_fastapi(self):
        """Test Logging module templates for FastAPI."""
        templates = get_module_templates("logging", "fastapi")

        assert len(templates) == 2
        template_paths = [t[0] for t in templates]
        # Should use app/logging.py for FastAPI
        assert any("app/logging.py" in p for p in template_paths)

    def test_logging_templates_cli(self):
        """Test Logging module templates for CLI."""
        templates = get_module_templates("logging", "cli")

        assert len(templates) == 2
        template_paths = [t[0] for t in templates]
        # Should use src/logging_config.py for CLI
        assert any("src/logging_config.py" in p for p in template_paths)

    def test_database_templates(self):
        """Test Database module templates."""
        templates = get_module_templates("database", "generic")

        assert len(templates) == 3
        template_paths = [t[0] for t in templates]
        assert any("alembic.ini" in p for p in template_paths)
        assert any("env.py" in p for p in template_paths)

    def test_ci_templates(self):
        """Test CI module templates."""
        templates = get_module_templates("ci", "generic")

        assert len(templates) == 1
        template_paths = [t[0] for t in templates]
        assert any("ci.yml" in p for p in template_paths)
        assert any(".github/workflows" in p for p in template_paths)

    def test_precommit_templates(self):
        """Test Pre-commit module templates."""
        templates = get_module_templates("precommit", "generic")

        assert len(templates) == 1
        template_paths = [t[0] for t in templates]
        assert any(".pre-commit-config.yaml" in p for p in template_paths)

    def test_poetry_templates(self):
        """Test Poetry module templates."""
        templates = get_module_templates("poetry", "generic")

        assert len(templates) == 1
        template_paths = [t[0] for t in templates]
        assert any("pyproject.toml" in p for p in template_paths)

    def test_invalid_module(self):
        """Test that invalid module returns empty list."""
        templates = get_module_templates("invalid", "generic")
        assert templates == []
