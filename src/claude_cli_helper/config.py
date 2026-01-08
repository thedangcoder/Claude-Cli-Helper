"""Configuration và paths cho Claude settings."""

import os
import platform
from pathlib import Path


def get_claude_config_dir() -> Path:
    """Lấy đường dẫn thư mục config của Claude theo OS."""
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


def get_settings_path() -> Path:
    """Lấy đường dẫn file settings.json của Claude."""
    return get_claude_config_dir() / "settings.json"


def get_mcp_settings_path() -> Path:
    """Lấy đường dẫn file claude_desktop_config.json cho MCP servers."""
    return get_claude_config_dir() / "claude_desktop_config.json"


def get_backup_dir() -> Path:
    """Lấy đường dẫn thư mục backup."""
    return get_claude_config_dir() / "backups"


# Claude Code specific paths
def get_claude_code_settings_path() -> Path:
    """Lấy đường dẫn settings của Claude Code CLI."""
    system = platform.system()

    if system == "Windows":
        base = os.environ.get("APPDATA", "")
        return Path(base) / "claude-code" / "settings.json"
    elif system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "claude-code" / "settings.json"
    else:
        xdg_config = os.environ.get("XDG_CONFIG_HOME", "")
        if xdg_config:
            return Path(xdg_config) / "claude-code" / "settings.json"
        return Path.home() / ".config" / "claude-code" / "settings.json"
