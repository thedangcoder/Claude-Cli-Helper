"""Configuration and paths for Claude settings."""

import os
import platform
from pathlib import Path


def get_claude_desktop_config_dir() -> Path:
    """Get Claude Desktop config directory path based on OS."""
    system = platform.system()

    if system == "Windows":
        base = os.environ.get("APPDATA", "")
        return Path(base) / "Claude"
    elif system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude"
    else:  # Linux
        xdg_config = os.environ.get("XDG_CONFIG_HOME", "")
        if xdg_config:
            return Path(xdg_config) / "Claude"
        return Path.home() / ".config" / "Claude"


def get_claude_code_config_dir() -> Path:
    """Get Claude Code CLI config directory path (~/.claude on all platforms)."""
    return Path.home() / ".claude"


def get_claude_desktop_settings_path() -> Path:
    """Get Claude Desktop settings.json path."""
    return get_claude_desktop_config_dir() / "settings.json"


def get_mcp_settings_path() -> Path:
    """Get claude_desktop_config.json path for MCP servers (Claude Desktop)."""
    return get_claude_desktop_config_dir() / "claude_desktop_config.json"


def get_claude_code_settings_path() -> Path:
    """Get Claude Code CLI settings.json path (~/.claude/settings.json)."""
    return get_claude_code_config_dir() / "settings.json"


def get_backup_dir() -> Path:
    """Get backup directory path."""
    return get_claude_code_config_dir() / "backups"


# Aliases for backward compatibility
def get_claude_config_dir() -> Path:
    """Alias for get_claude_code_config_dir."""
    return get_claude_code_config_dir()


def get_settings_path() -> Path:
    """Alias for get_claude_code_settings_path."""
    return get_claude_code_settings_path()
