"""Tests for the Jinja2 template engine module."""

import tempfile
from pathlib import Path

import pytest

from gentem.template_engine import TemplateEngine, get_template_engine


class TestTemplateEngineInit:
    """Tests for TemplateEngine initialization."""

    def test_default_template_dir(self):
        """Test that default template_dir is set correctly."""
        engine = TemplateEngine()
        expected_dir = Path(__file__).parent.parent / "src" / "gentem" / "templates"
        assert engine.template_dir == expected_dir

    def test_custom_template_dir(self):
        """Test with custom template directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = TemplateEngine(template_dir=tmpdir)
            assert engine.template_dir == Path(tmpdir)

    def test_jinja2_environment_configured(self):
        """Test that Jinja2 environment is properly configured."""
        engine = TemplateEngine()
        assert engine.env is not None
        assert engine.env.autoescape is True
        assert engine.env.trim_blocks is True
        assert engine.env.lstrip_blocks is True

    def test_file_system_loader(self):
        """Test that FileSystemLoader is set up correctly."""
        engine = TemplateEngine()
        assert engine.env.loader is not None
        # Verify loader is configured by successfully loading a template
        template = engine.get_template("base/gitignore.j2")
        assert template is not None


class TestGetTemplate:
    """Tests for the get_template method."""

    def test_get_existing_template(self):
        """Test retrieving an existing template."""
        engine = TemplateEngine()
        template = engine.get_template("base/gitignore.j2")
        assert template is not None

    def test_get_nonexistent_template(self):
        """Test error when template doesn't exist."""
        engine = TemplateEngine()
        with pytest.raises(Exception):
            engine.get_template("nonexistent/template.j2")


class TestRenderTemplate:
    """Tests for the render_template method."""

    def test_simple_variable_substitution(self):
        """Test basic variable substitution in template."""
        engine = TemplateEngine()
        # Use a template that actually uses project_slug - library pyproject
        content = engine.render_template(
            "library/pyproject.toml.j2",
            {"project_slug": "mytestproject", "author": "Test", "year": 2024,
             "description": "Test", "license": "MIT", "python_version": "3.10",
             "python_versions": ["3.10"], "library_enabled": True, "cli_enabled": False},
        )
        assert 'name = "mytestproject"' in content

    def test_template_with_context(self):
        """Test template rendering with full context."""
        engine = TemplateEngine()
        context = {
            "project_name": "My Test Project",
            "project_slug": "my-test-project",
            "author": "Test Author",
            "version": "1.0.0",
            "description": "A test project",
            "license": "MIT",
            "year": 2024,
            "python_version": "3.10",
            "python_versions": ["3.10", "3.11", "3.12"],
        }
        content = engine.render_template("base/license_mit.j2", context)
        assert "MIT License" in content
        assert "Test Author" in content
        assert "2024" in content

    def test_all_license_types(self):
        """Test all license template rendering."""
        engine = TemplateEngine()
        context = {
            "author": "Test Author",
            "year": 2024,
        }

        licenses = [
            ("base/license_mit.j2", "MIT License"),
            ("base/license_apache.j2", "Apache License"),
            ("base/license_bsd.j2", "BSD 3-Clause License"),
            ("base/license_gpl.j2", "GNU GENERAL PUBLIC LICENSE"),
        ]

        for template_path, expected in licenses:
            content = engine.render_template(template_path, context)
            assert expected in content, f"Failed for {template_path}"


class TestRenderFile:
    """Tests for the render_file method."""

    def test_render_to_file(self):
        """Test rendering a template to a file."""
        engine = TemplateEngine()
        context = {"project_slug": "testproject", "author": "Test", "year": 2024,
                   "description": "Test", "license": "MIT", "python_version": "3.10",
                   "python_versions": ["3.10"], "library_enabled": True, "cli_enabled": False}

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_output.txt"
            engine.render_file("library/pyproject.toml.j2", context, output_path)

            assert output_path.exists()
            content = output_path.read_text(encoding="utf-8")
            assert 'name = "testproject"' in content

    def test_creates_parent_directories(self):
        """Test that render_file creates parent directories."""
        engine = TemplateEngine()
        context = {"project_slug": "testproject"}

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "nested" / "deep" / "output.txt"
            engine.render_file("base/gitignore.j2", context, output_path)

            assert output_path.exists()


class TestListTemplates:
    """Tests for the list_templates method."""

    def test_list_all_templates(self):
        """Test listing all templates."""
        engine = TemplateEngine()
        templates = engine.list_templates()

        assert len(templates) > 0
        assert any("gitignore.j2" in t for t in templates)
        assert any("license_mit.j2" in t for t in templates)

    def test_list_subdirectory_templates(self):
        """Test listing templates in a subdirectory."""
        engine = TemplateEngine()
        templates = engine.list_templates("library")

        assert len(templates) > 0
        assert any("pyproject.toml.j2" in t for t in templates)
        # All templates should be in library subdirectory
        # Check that each template path contains "library" as a component
        for t in templates:
            parts = Path(t).parts
            assert len(parts) >= 1, f"Template path '{t}' has no parts"
            assert parts[0] == "library", f"Template path '{t}' doesn't start with 'library'"

    def test_list_nonexistent_subdirectory(self):
        """Test listing templates in nonexistent subdirectory returns empty."""
        engine = TemplateEngine()
        templates = engine.list_templates("nonexistent")

        assert templates == []

    def test_returns_jinja_files_only(self):
        """Test that only .j2 files are returned."""
        engine = TemplateEngine()
        templates = engine.list_templates()

        for t in templates:
            assert t.endswith(".j2"), f"Non-Jinja2 file found: {t}"


class TestGetTemplateEngine:
    """Tests for the get_template_engine global function."""

    def test_returns_template_engine(self):
        """Test that get_template_engine returns a TemplateEngine instance."""
        engine = get_template_engine()
        assert isinstance(engine, TemplateEngine)

    def test_returns_same_instance(self):
        """Test that get_template_engine returns the same instance."""
        engine1 = get_template_engine()
        engine2 = get_template_engine()
        assert engine1 is engine2
