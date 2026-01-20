# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-01-20

### Added

- New interactive project creation wizard via `gentem init` command with guided prompts ([`ba68bd5`](https://github.com/knightlesssword/gentem/commit/ba68bd5))
- Presets for quick project setup: minimal, cli-tool, fastapi, and script
- Comprehensive documentation for all CLI commands ([`docs/COMMANDS.md`](docs/COMMANDS.md))
- Updated `.gitignore` with additional entries for test environments

### Changed

- Enhanced CLI with new `init` subcommand ([`src/gentem/cli.py`](src/gentem/cli.py))
- Extended FastAPI command with improved database support ([`src/gentem/commands/fastapi.py`](src/gentem/commands/fastapi.py))

## [0.1.3] - 2026-01-14

### Fixed

- Corrected the `include` directive in `pyproject.toml` from `"app*"` to `"gentem*"` to properly recognize project subdirectories ([`7f3f6b5`](https://github.com/knightlesssword/gentem/commit/7f3f6b5))
- Updated CLI short option for `--async` flag from `-a` to `-A` ([`7f3f6b5`](https://github.com/knightlesssword/gentem/commit/7f3f6b5))
- Updated CLI short option for `--database` flag from `-d` to `-D` ([`7f3f6b5`](https://github.com/knightlesssword/gentem/commit/7f3f6b5))

## [0.1.2] - 2026-01-13

### Security

- **Yanked Release**: This version was yanked due to a critical packaging error. The `pyproject.toml` included `"app*"` instead of `"gentem*"`, causing the package to fail on fresh installations. Do not use this version.

## [0.1.1] - 2026-01-13

### Changed

- Updated author name from "gentem contributors" to the project maintainer's name ([`d88d3b6`](https://github.com/knightlesssword/gentem/commit/d88d3b6))

## [0.1.0] - 2026-01-13

### Added

- Initial project release ([`8c40087`](https://github.com/knightlesssword/gentem/commit/8c40087))
- Base project structure for default (normal) projects
- FastAPI project template support
- CLI tool for project scaffolding (`cli.py`)
- Template engine for project generation (`template_engine.py`)
- Input validators for CLI arguments (`utils/validators.py`)
- CI/CD workflow configuration (`.github/workflows/ci.yml`)
- Comprehensive test suite (`tests/`)

