"""Tests for settings validation command."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from claude_cli_helper.commands.settings import validate
from claude_cli_helper.models import ClaudeCodeSettings, MCPConfig


@pytest.fixture
def runner():
    """Create CLI runner."""
    return CliRunner()


@pytest.fixture
def mock_manager():
    """Create mock settings manager."""
    with patch("claude_cli_helper.commands.settings.manager") as mock:
        yield mock


def test_validate_valid_settings(runner, mock_manager):
    """Test validation với settings hợp lệ."""
    # Setup
    mock_manager.claude_code_path.exists.return_value = True
    mock_manager.mcp_path.exists.return_value = True
    mock_manager.read_claude_code_settings.return_value = ClaudeCodeSettings()
    mock_manager.read_mcp_config.return_value = MCPConfig()

    # Execute
    result = runner.invoke(validate)

    # Assert
    assert result.exit_code == 0
    assert "OK Valid settings file" in result.output
    assert "OK Valid MCP config" in result.output
    assert "All settings are valid!" in result.output


def test_validate_missing_settings_file(runner, mock_manager):
    """Test validation khi thiếu settings file."""
    # Setup
    mock_manager.claude_code_path.exists.return_value = False
    mock_manager.mcp_path.exists.return_value = True

    # Execute
    result = runner.invoke(validate)

    # Assert
    assert result.exit_code == 0
    assert "! Settings file doesn't exist" in result.output
    assert "1 issue(s) found" in result.output


def test_validate_fix_missing_settings(runner, mock_manager):
    """Test auto-fix cho missing settings file."""
    # Setup
    mock_manager.claude_code_path.exists.return_value = False
    mock_manager.claude_code_path.parent.mkdir = MagicMock()
    mock_manager.mcp_path.exists.return_value = True
    mock_manager.read_claude_code_settings.return_value = ClaudeCodeSettings()

    # Execute
    result = runner.invoke(validate, ["--fix"])

    # Assert
    assert result.exit_code == 0
    assert "OK Created default settings file" in result.output
    mock_manager.write_claude_code_settings.assert_called_once()


def test_validate_empty_env_var(runner, mock_manager):
    """Test validation với empty environment variable."""
    # Setup
    settings = ClaudeCodeSettings(env={"ANTHROPIC_BASE_URL": ""})
    mock_manager.claude_code_path.exists.return_value = True
    mock_manager.mcp_path.exists.return_value = True
    mock_manager.read_claude_code_settings.return_value = settings
    mock_manager.read_mcp_config.return_value = MCPConfig()

    # Execute
    result = runner.invoke(validate)

    # Assert
    assert result.exit_code == 0
    assert "! ANTHROPIC_BASE_URL is empty" in result.output


def test_validate_fix_empty_env_var(runner, mock_manager):
    """Test auto-fix cho empty env var."""
    # Setup
    settings = ClaudeCodeSettings(env={"ANTHROPIC_BASE_URL": ""})
    mock_manager.claude_code_path.exists.return_value = True
    mock_manager.mcp_path.exists.return_value = True
    mock_manager.read_claude_code_settings.return_value = settings
    mock_manager.read_mcp_config.return_value = MCPConfig()

    # Execute
    result = runner.invoke(validate, ["--fix"])

    # Assert
    assert result.exit_code == 0
    assert "OK Removed empty ANTHROPIC_BASE_URL" in result.output
    assert "ANTHROPIC_BASE_URL" not in settings.env


def test_validate_json_decode_error(runner, mock_manager):
    """Test validation với JSON syntax error."""
    # Setup
    mock_manager.claude_code_path.exists.return_value = True
    mock_manager.read_claude_code_settings.side_effect = json.JSONDecodeError(
        "Invalid JSON", "", 0
    )
    mock_manager.mcp_path.exists.return_value = True
    mock_manager.read_mcp_config.return_value = MCPConfig()

    # Execute
    result = runner.invoke(validate)

    # Assert
    assert result.exit_code == 0
    assert "X Invalid JSON" in result.output
    assert "1 issue(s) found" in result.output


def test_validate_duplicate_mcp_servers(runner, mock_manager):
    """Test validation với duplicate MCP server names."""
    # Setup
    from claude_cli_helper.models import MCPServer

    mcp_config = MCPConfig(
        mcpServers={
            "server1": MCPServer(command="npx"),
            "server2": MCPServer(command="npx"),
        }
    )
    mock_manager.claude_code_path.exists.return_value = True
    mock_manager.mcp_path.exists.return_value = True
    mock_manager.read_claude_code_settings.return_value = ClaudeCodeSettings()
    mock_manager.read_mcp_config.return_value = mcp_config

    # Execute
    result = runner.invoke(validate)

    # Assert
    assert result.exit_code == 0
    assert "OK Valid MCP config" in result.output
