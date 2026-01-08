# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude CLI Helper is a Python CLI tool to manage Claude Desktop and Claude Code CLI settings. Features:
- Interactive setup wizard
- Read/write settings.json
- Configure MCP servers
- Apply preset profiles
- Backup/restore settings

## Commands

```bash
# Install development environment
pip install -e ".[dev]"

# Run CLI directly
python -m claude_cli_helper.cli <command>

# Or after installation
claude-helper <command>

# Run tests
pytest

# Run single test file
pytest tests/test_models.py

# Run single test function
pytest tests/test_models.py::test_mcp_server_defaults

# Linting
ruff check .
ruff check . --fix

# Type checking
mypy src
```

## Architecture

```
src/claude_cli_helper/
├── cli.py              # Entry point, register command groups
├── config.py           # Path functions for Claude Desktop and Claude Code
├── models.py           # Pydantic models: MCPServer, MCPConfig, ClaudeSettings, etc.
├── settings_manager.py # Core logic for read/write JSON files, backup/restore
├── commands/           # Click command groups
│   ├── settings.py     # settings show/list/get/set
│   ├── mcp.py          # mcp list/add/remove
│   ├── backup.py       # backup create/list/restore/delete
│   ├── profile.py      # profile list/show/apply
│   └── setup.py        # Interactive setup wizard
└── templates/
    └── profiles.py     # Built-in profiles (developer, power-user, etc.)
```

## Key Patterns

- **Click** for CLI with command groups (settings, mcp, backup, profile, setup)
- **Pydantic** for data validation and serialization
- **Rich** for console output with colors and tables
- **Questionary** for interactive prompts (with Click fallback)
- **utf-8-sig encoding** to handle BOM in JSON files (Windows PowerShell creates files with BOM)

## Settings File Locations

Tool manages these config files:

| Type | Path |
|------|------|
| **Claude Code CLI** | `~/.claude/settings.json` (all platforms) |
| **Claude Desktop** | `%APPDATA%/Claude/` (Win), `~/Library/Application Support/Claude/` (Mac) |
| **MCP Config** | `claude_desktop_config.json` in Claude Desktop directory |
| **Backups** | `~/.claude/backups/` |

## Adding New Profiles

Add new profile in `src/claude_cli_helper/templates/profiles.py`:

```python
NEW_PROFILE = SettingsProfile(
    name="profile-name",
    description="Description in English",
    claude_code_settings=ClaudeCodeSettings(...),
    mcp_config=MCPConfig(...),
)

# Add to BUILTIN_PROFILES dict
BUILTIN_PROFILES["profile-name"] = NEW_PROFILE
```
