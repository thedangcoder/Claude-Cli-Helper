# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude CLI Helper là một Python CLI tool để quản lý settings của Claude Desktop và Claude Code CLI. Tool hỗ trợ:
- Đọc/ghi settings.json
- Cấu hình MCP servers
- Apply preset profiles
- Backup/restore settings

## Commands

```bash
# Cài đặt development environment
pip install -e ".[dev]"

# Chạy CLI trực tiếp
python -m claude_cli_helper.cli <command>

# Hoặc sau khi cài đặt
claude-helper <command>

# Chạy tests
pytest

# Chạy single test file
pytest tests/test_models.py

# Chạy single test function
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
├── config.py           # OS-specific paths (Windows/macOS/Linux)
├── models.py           # Pydantic models: MCPServer, MCPConfig, ClaudeSettings, etc.
├── settings_manager.py # Core logic đọc/ghi JSON files, backup/restore
├── commands/           # Click command groups
│   ├── settings.py     # settings show/get/set
│   ├── mcp.py          # mcp list/add/remove
│   ├── backup.py       # backup create/list/restore
│   └── profile.py      # profile list/show/apply
└── templates/
    └── profiles.py     # Built-in profiles (developer, power-user, etc.)
```

## Key Patterns

- **Click** cho CLI với command groups (settings, mcp, backup, profile)
- **Pydantic** cho data validation và serialization
- **Rich** cho console output với colors và tables
- **Cross-platform paths** trong `config.py` - detect OS và trả về đúng path cho Claude settings

## Settings File Locations

Tool quản lý 3 file chính (paths tự động detect theo OS):
1. **Claude Desktop settings**: `settings.json`
2. **MCP config**: `claude_desktop_config.json`
3. **Claude Code CLI**: `~/.config/claude-code/settings.json` (Linux) hoặc tương đương

## Adding New Profiles

Thêm profile mới trong `src/claude_cli_helper/templates/profiles.py`:

```python
NEW_PROFILE = SettingsProfile(
    name="profile-name",
    description="Description",
    claude_code_settings=ClaudeCodeSettings(...),
    mcp_config=MCPConfig(...),
)

# Thêm vào BUILTIN_PROFILES dict
BUILTIN_PROFILES["profile-name"] = NEW_PROFILE
```
