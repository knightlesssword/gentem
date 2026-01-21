"""Integration tests for template rendering with Jinja2 features."""

import tempfile
from pathlib import Path

import pytest

from gentem.template_engine import TemplateEngine


class TestTemplateRendering:
    """Tests for template rendering with various Jinja2 features."""

    @pytest.fixture
    def engine(self):
        """Create a TemplateEngine instance for testing."""
        return TemplateEngine()

    @pytest.fixture
    def context(self):
        """Create a standard context for testing."""
        return {
            "project_name": "My Test Project",
            "project_slug": "my-test-project",
            "class_name": "MyTestProject",
            "author": "John Doe",
            "email": "user@my-test-project.dev",
            "description": "A test project for testing Jinja2 templates",
            "version": "1.0.0",
            "python_version": "3.10",
            "python_versions": ["3.10", "3.11", "3.12"],
            "license": "MIT",
            "year": 2024,
            "async_mode": True,
            "has_database": True,
            "db_type": "asyncpg",
            "library_enabled": True,
            "cli_enabled": False,
            "script_enabled": False,
        }


class TestVariableSubstitution(TestTemplateRendering):
    """Tests for basic variable substitution in templates."""

    def test_gitignore_is_static(self, engine, context):
        """Test that gitignore template is static (no project-specific entries)."""
        content = engine.render_template("base/gitignore.j2", context)
        # Gitignore is static, just check it contains standard entries
        assert "__pycache__" in content
        assert ".venv" in content
        assert "*.py[cod]" in content  # Python bytecode pattern

    def test_license_mit_substitution(self, engine, context):
        """Test MIT license template substitution."""
        content = engine.render_template("base/license_mit.j2", context)
        assert "MIT License" in content
        assert "John Doe" in content
        assert "2024" in content

    def test_license_apache_substitution(self, engine, context):
        """Test Apache license template substitution."""
        content = engine.render_template("base/license_apache.j2", context)
        assert "Apache License" in content
        assert "John Doe" in content  # Now includes author
        assert "2024" in content  # Now includes year
        assert "Version 2.0" in content


class TestConditionalRendering(TestTemplateRendering):
    """Tests for Jinja2 conditional blocks in templates."""

    def test_library_pyproject_conditionals(self, engine, context):
        """Test library pyproject.toml conditional rendering."""
        # Test with library enabled
        content = engine.render_template("library/pyproject.toml.j2", context)
        assert "my-test-project" in content  # name from project_slug
        assert "A test project for testing Jinja2 templates" in content  # description
        assert "John Doe" in content  # author
        assert "user@my-test-project.dev" in content  # email

    def test_cli_pyproject_conditionals(self, engine, context):
        """Test CLI pyproject.toml conditional rendering."""
        context["cli_enabled"] = True
        context["library_enabled"] = False

        content = engine.render_template("cli/pyproject.toml.j2", context)
        assert "my-test-project" in content
        assert "John Doe" in content

    def test_fastapi_main_conditionals(self, engine, context):
        """Test FastAPI main.py conditional rendering."""
        # Test with async_mode=True and has_database=True
        content = engine.render_template("fastapi/app/main.py.j2", context)

        # Should have lifespan context manager
        assert "@asynccontextmanager" in content or "async def lifespan" in content
        # Should have database initialization
        assert "init_db" in content or "close_db" in content

    def test_fastapi_main_no_async(self, engine, context):
        """Test FastAPI main.py without async mode."""
        context["async_mode"] = False
        context["has_database"] = False

        content = engine.render_template("fastapi/app/main.py.j2", context)

        # Should NOT have lifespan
        assert "lifespan" not in content.lower()


class TestLoopRendering(TestTemplateRendering):
    """Tests for Jinja2 loops in templates."""

    def test_pyproject_python_versions_loop(self, engine, context):
        """Test that python_versions loop renders correctly."""
        content = engine.render_template("library/pyproject.toml.j2", context)

        # Check all versions are present
        assert "Programming Language :: Python :: 3.10" in content
        assert "Programming Language :: Python :: 3.11" in content
        assert "Programming Language :: Python :: 3.12" in content


class TestFileGeneration(TestTemplateRendering):
    """Tests for actual file generation from templates."""

    def test_generate_library_project(self, engine, context):
        """Test generating a full library project structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "my-test-project"
            output_path.mkdir()

            # Generate all library files
            template_files = [
                ("base/gitignore.j2", ".gitignore"),
                ("library/pyproject.toml.j2", "pyproject.toml"),
                ("library/README.md.j2", "README.md"),
                ("library/src/__init__.py.j2", "src/__init__.py"),
            ]

            for template_path, output_file in template_files:
                engine.render_file(
                    template_path,
                    context,
                    output_path / output_file,
                )

            # Verify files were created
            assert (output_path / ".gitignore").exists()
            assert (output_path / "pyproject.toml").exists()
            assert (output_path / "README.md").exists()
            assert (output_path / "src" / "__init__.py").exists()

            # Verify content - gitignore is static, check pyproject.toml for project_slug
            pyproject_content = (output_path / "pyproject.toml").read_text()
            assert "my-test-project" in pyproject_content

    def test_generate_fastapi_project(self, engine, context):
        """Test generating a full FastAPI project structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "my-api"
            output_path.mkdir()

            # Generate FastAPI files
            template_files = [
                ("fastapi/pyproject.toml.j2", "pyproject.toml"),
                ("fastapi/app/main.py.j2", "app/main.py"),
                ("fastapi/app/core/config.py.j2", "app/core/config.py"),
            ]

            for template_path, output_file in template_files:
                engine.render_file(
                    template_path,
                    context,
                    output_path / output_file,
                )

            # Verify files were created
            assert (output_path / "pyproject.toml").exists()
            assert (output_path / "app" / "main.py").exists()
            assert (output_path / "app" / "core" / "config.py").exists()

    def test_generate_cli_project(self, engine, context):
        """Test generating a CLI project structure."""
        context["cli_enabled"] = True
        context["library_enabled"] = False

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "my-cli"
            output_path.mkdir()

            template_files = [
                ("cli/pyproject.toml.j2", "pyproject.toml"),
                ("cli/src/main.py.j2", "src/main.py"),
                ("cli/src/cli.py.j2", "src/cli.py"),
            ]

            for template_path, output_file in template_files:
                engine.render_file(
                    template_path,
                    context,
                    output_path / output_file,
                )

            # Verify files were created
            assert (output_path / "pyproject.toml").exists()
            assert (output_path / "src" / "main.py").exists()
            assert (output_path / "src" / "cli.py").exists()


class TestTemplateEdgeCases(TestTemplateRendering):
    """Tests for edge cases in template rendering."""

    def test_empty_context(self, engine):
        """Test rendering with minimal context."""
        context = {"project_slug": "test"}

        content = engine.render_template("base/gitignore.j2", context)
        assert "test" in content

    def test_special_characters_in_values(self, engine):
        """Test handling of special characters in context values."""
        context = {
            "project_slug": "my-project",
            "author": "John Doe, Jr.",
            "description": "A project with 'quotes' and \"double quotes\"",
        }

        content = engine.render_template("base/license_mit.j2", context)
        assert "John Doe, Jr." in content

    def test_unicode_in_context(self, engine):
        """Test handling of unicode characters."""
        context = {
            "project_slug": "test",
            "author": "José García",
            "description": "A project with unicode: é à ü ñ",
        }

        content = engine.render_template("base/license_mit.j2", context)
        assert "José García" in content
