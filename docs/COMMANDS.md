# Gentem CLI Commands Reference

A comprehensive guide to all command combinations available when installing the `gentem` package.

## Installation

```bash
pip install gentem
```

## Entry Points

After installation, you can access gentem using:

| Command | Description |
|---------|-------------|
| `gentem` | Main CLI entry point (from `[project.scripts]` in pyproject.toml) |
| `python -m gentem` | Module-based entry point |

## Base Commands

### Version Information

```bash
gentem --version    # Show version and exit
gentem -V           # Short form
```

### Help

```bash
gentem --help       # Show main help
gentem new --help   # Show help for 'new' command
gentem fastapi --help   # Show help for 'fastapi' command
gentem init --help      # Show help for 'init' command
```

---

## Command: `gentem new`

Create a new Python project (library, CLI tool, or script).

### Basic Usage

```bash
gentem new <PROJECT_NAME>
```

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--type` | `-t` | Project type: `library`, `cli`, or `script` | `library` |
| `--author` | `-a` | Author name for the project | "" |
| `--description` | `-d` | Description for the project | "" |
| `--license` | `-l` | License type: `mit`, `apache`, `gpl`, or `none` | `mit` |
| `--dry-run` | - | Preview the project structure without creating files | `False` |
| `--verbose` | `-v` | Show verbose output | `False` |

### Command Combinations

```bash
# Create a library project
gentem new mylib

# Create a CLI tool project
gentem new mycli --type cli

# Create a simple script project
gentem new myscript --type script

# With author
gentem new mylib --author "John Doe"

# With description
gentem new mylib --description "My awesome library"

# With license
gentem new mylib --license mit
gentem new mylib --license apache
gentem new mylib --license gpl
gentem new mylib --license none

# All options combined
gentem new mylib \
    --type library \
    --author "John Doe" \
    --description "My library" \
    --license mit

# Preview without creating files
gentem new mylib --type library --dry-run

# Verbose output
gentem new mylib -v

# Short form options
gentem new mylib -t library -a "John Doe" -d "My library" -l mit -v
```

---

## Command: `gentem fastapi`

Create a new FastAPI project with opinionated structure.

### Basic Usage

```bash
gentem fastapi <PROJECT_NAME>
```

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--async` | `-A` | Use async mode with lifespan | `False` |
| `--db` | `-D` | Database type: `asyncpg` (for async SQLAlchemy) | "" |
| `--author` | `-a` | Author name for the project | "" |
| `--description` | `-d` | Description for the project | "" |
| `--dry-run` | - | Preview the project structure without creating files | `False` |
| `--verbose` | `-v` | Show verbose output | `False` |

### Command Combinations

```bash
# Create a basic FastAPI project
gentem fastapi myapi

# Create with async mode and lifespan
gentem fastapi myapi --async
gentem fastapi myapi -A

# Create with database support (asyncpg)
gentem fastapi myapi --db asyncpg
gentem fastapi myapi -D asyncpg

# With author
gentem fastapi myapi --author "John Doe"

# With description
gentem fastapi myapi --description "My FastAPI API"

# All options combined
gentem fastapi myapi \
    --async \
    --db asyncpg \
    --author "John Doe" \
    --description "My FastAPI API"

# Preview without creating files
gentem fastapi myapi --dry-run

# Verbose output
gentem fastapi myapi -v

# Short form options
gentem fastapi myapi -A -D asyncpg -a "John Doe" -d "API" -v
```

---

## Command: `gentem init`

Interactive wizard for creating new projects.

### Basic Usage

```bash
gentem init
```

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--skip-prompts` | `-s` | Skip prompts and use default values | `False` |
| `--preset` | `-p` | Preset to use: `minimal`, `cli-tool`, `fastapi` | "" |
| `--dry-run` | - | Preview the project structure without creating files | `False` |
| `--verbose` | `-v` | Show verbose output | `False` |

### Command Combinations

```bash
# Interactive mode (default)
gentem init

# Skip prompts with defaults
gentem init --skip-prompts

# Use a preset
gentem init --preset minimal
gentem init --preset cli-tool
gentem init --preset fastapi
gentem init -p fastapi

# Preview without creating files
gentem init --dry-run
gentem init -p fastapi --dry-run

# Verbose output
gentem init -v

# Skip prompts with preset and verbose
gentem init --skip-prompts --preset fastapi -v
```

---

## All Commands Quick Reference

```
gentem                           # Main entry point
gentem --version                 # Show version
gentem --help                    # Show help

gentem new <NAME>                # Create new project
gentem new <NAME> --type <TYPE>  # With project type
gentem new <NAME> -t cli         # CLI tool project
gentem new <NAME> -t library     # Library project
gentem new <NAME> -t script      # Script project

gentem fastapi <NAME>            # Create FastAPI project
gentem fastapi <NAME> --async    # With async mode
gentem fastapi <NAME> --db <DB>  # With database

gentem init                      # Interactive wizard
gentem init --preset <PRESET>    # With preset
gentem init -s                   # Skip prompts
```

---

## Testing the Package

### Running Tests

```bash
pytest
```

### Test Configuration

From `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

### What Happens When You Run Tests

1. **Test Discovery**: Pytest automatically discovers tests in:
   - Directory: `tests/`
   - Files matching: `test_*.py`
   - Functions matching: `test_*`

2. **Test Files**:
   - [`tests/test_new_command.py`](../tests/test_new_command.py) - Tests for the `new` command module
     - `TestGenerateSlug` - Tests for slug generation
     - `TestGenerateClassName` - Tests for class name generation
     - `TestGenerateContext` - Tests for context generation
     - `TestGetProjectFiles` - Tests for file list generation
   - [`tests/test_validators.py`](../tests/test_validators.py) - Tests for the validators module
     - `TestValidatePythonIdentifier` - Tests for Python identifier validation
     - `TestValidateProjectName` - Tests for project name validation
     - `TestValidateLicenseType` - Tests for license type validation
     - `TestValidateProjectType` - Tests for project type validation
     - `TestValidateDbType` - Tests for database type validation
   - [`tests/test_init_command.py`](../tests/test_init_command.py) - Tests for the `init` command module
     - `TestGetProjectName` - Tests for project name prompt
     - `TestGetDescription` - Tests for description prompt
     - `TestGetAuthor` - Tests for author prompt
     - `TestGetProjectType` - Tests for project type selection
     - `TestGetPythonVersions` - Tests for Python version selection
     - `TestGetLicense` - Tests for license selection
     - `TestGetAddCli` - Tests for CLI support prompt
     - `TestGetAddDocker` - Tests for Docker support prompt
     - `TestGetAddDocs` - Tests for documentation prompt
     - `TestGetTestingFramework` - Tests for testing framework selection
     - `TestGetLinting` - Tests for linting tool selection
     - `TestGetCiProvider` - Tests for CI/CD provider selection
     - `TestGetFastapiOptions` - Tests for FastAPI options
     - `TestShowPreview` - Tests for preview display
     - `TestRunInit` - Tests for the main `run_init` function
     - `TestCustomStyle` - Tests for custom style

3. **Output Format**:
   - `-v` (verbose): Shows detailed output for each test
   - `--tb=short` (short traceback): Shows abbreviated error traces

4. **Development Dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

### Test Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gentem

# Run specific test file
pytest tests/test_new_command.py

# Run specific test class
pytest tests/test_validators.py::TestValidateProjectName

# Run specific test function
pytest tests/test_validators.py::TestValidateProjectName::test_valid_project_names
```

### CI/CD Testing

From [`.github/workflows/ci.yml`](../.github/workflows/ci.yml), the package is tested on:
- Python 3.9, 3.10, 3.11, 3.12
- With pytest and coverage reporting
