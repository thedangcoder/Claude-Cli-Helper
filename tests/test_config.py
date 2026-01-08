"""Tests for config paths."""

import platform
from pathlib import Path
from unittest.mock import patch

from claude_cli_helper.config import (
    get_backup_dir,
    get_claude_code_settings_path,
    get_claude_config_dir,
    get_mcp_settings_path,
    get_settings_path,
)


def test_get_claude_config_dir_windows():
    """Test config dir trên Windows."""
    with patch.object(platform, "system", return_value="Windows"):
        with patch.dict("os.environ", {"APPDATA": "C:\\Users\\Test\\AppData\\Roaming"}):
            path = get_claude_config_dir()
            assert path == Path("C:\\Users\\Test\\AppData\\Roaming\\Claude")


def test_get_claude_config_dir_macos():
    """Test config dir trên macOS."""
    with patch.object(platform, "system", return_value="Darwin"):
        with patch("pathlib.Path.home", return_value=Path("/Users/test")):
            path = get_claude_config_dir()
            assert path == Path("/Users/test/Library/Application Support/Claude")


def test_get_claude_config_dir_linux():
    """Test config dir trên Linux."""
    with patch.object(platform, "system", return_value="Linux"):
        with patch.dict("os.environ", {"XDG_CONFIG_HOME": ""}, clear=False):
            with patch("pathlib.Path.home", return_value=Path("/home/test")):
                path = get_claude_config_dir()
                assert path == Path("/home/test/.config/Claude")


def test_get_settings_path():
    """Test settings.json path."""
    with patch.object(platform, "system", return_value="Windows"):
        with patch.dict("os.environ", {"APPDATA": "C:\\Users\\Test\\AppData\\Roaming"}):
            path = get_settings_path()
            assert path.name == "settings.json"
            assert "Claude" in str(path)


def test_get_mcp_settings_path():
    """Test MCP settings path."""
    with patch.object(platform, "system", return_value="Windows"):
        with patch.dict("os.environ", {"APPDATA": "C:\\Users\\Test\\AppData\\Roaming"}):
            path = get_mcp_settings_path()
            assert path.name == "claude_desktop_config.json"


def test_get_backup_dir():
    """Test backup directory path."""
    with patch.object(platform, "system", return_value="Windows"):
        with patch.dict("os.environ", {"APPDATA": "C:\\Users\\Test\\AppData\\Roaming"}):
            path = get_backup_dir()
            assert path.name == "backups"


def test_get_claude_code_settings_path():
    """Test Claude Code CLI settings path."""
    with patch.object(platform, "system", return_value="Windows"):
        with patch.dict("os.environ", {"APPDATA": "C:\\Users\\Test\\AppData\\Roaming"}):
            path = get_claude_code_settings_path()
            assert path.name == "settings.json"
            assert "claude-code" in str(path)
