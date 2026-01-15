"""Tests for settings export/import commands."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from claude_cli_helper.commands.settings import export, import_settings
from claude_cli_helper.models import ClaudeCodeSettings, MCPConfig, MCPServer


@pytest.fixture
def runner():
    """Create CLI runner."""
    return CliRunner()


@pytest.fixture
def mock_manager():
    """Create mock settings manager."""
    with patch("claude_cli_helper.commands.settings.manager") as mock:
        yield mock


@pytest.fixture
def sample_settings():
    """Create sample settings."""
    return ClaudeCodeSettings(
        autoApproveRead=True,
        model="sonnet",
        env={"ANTHROPIC_BASE_URL": "https://api.example.com"},
    )


@pytest.fixture
def sample_mcp_config():
    """Create sample MCP config."""
    return MCPConfig(
        mcpServers={"filesystem": MCPServer(command="npx", args=["-y", "server"])}
    )


def test_export_json(runner, mock_manager, sample_settings, tmp_path):
    """Test export settings to JSON."""
    # Setup
    mock_manager.read_claude_code_settings.return_value = sample_settings
    output_file = tmp_path / "export.json"

    # Execute
    result = runner.invoke(export, [str(output_file)])

    # Assert
    assert result.exit_code == 0
    assert "OK Settings exported" in result.output
    assert output_file.exists()

    # Verify content
    data = json.loads(output_file.read_text())
    assert "claude_code" in data
    assert data["claude_code"]["autoApproveRead"] is True
    assert data["claude_code"]["model"] == "sonnet"


def test_export_with_mcp(runner, mock_manager, sample_settings, sample_mcp_config, tmp_path):
    """Test export với MCP config."""
    # Setup
    mock_manager.read_claude_code_settings.return_value = sample_settings
    mock_manager.read_mcp_config.return_value = sample_mcp_config
    output_file = tmp_path / "export.json"

    # Execute
    result = runner.invoke(export, [str(output_file), "--include-mcp"])

    # Assert
    assert result.exit_code == 0
    assert "Included: Claude Code settings + MCP config" in result.output

    # Verify content
    data = json.loads(output_file.read_text())
    assert "claude_code" in data
    assert "mcp" in data
    assert "filesystem" in data["mcp"]["mcpServers"]


def test_export_yaml(runner, mock_manager, sample_settings, tmp_path):
    """Test export to YAML format."""
    # Setup
    mock_manager.read_claude_code_settings.return_value = sample_settings
    output_file = tmp_path / "export.yaml"

    # Execute with pytest.skipif if yaml not installed
    try:
        import yaml
        result = runner.invoke(export, [str(output_file), "--format", "yaml"])
        assert result.exit_code == 0
        assert output_file.exists()
    except ImportError:
        pytest.skip("PyYAML not installed")


def test_import_json(runner, mock_manager, tmp_path):
    """Test import settings from JSON."""
    # Setup
    import_data = {
        "claude_code": {
            "autoApproveRead": True,
            "model": "opus",
        }
    }
    input_file = tmp_path / "import.json"
    input_file.write_text(json.dumps(import_data))
    mock_manager.read_claude_code_settings.return_value = ClaudeCodeSettings()

    # Execute
    result = runner.invoke(import_settings, [str(input_file)])

    # Assert
    assert result.exit_code == 0
    assert "OK Claude Code settings imported" in result.output
    mock_manager.write_claude_code_settings.assert_called_once()


def test_import_merge(runner, mock_manager, tmp_path):
    """Test import với merge mode."""
    # Setup
    current_settings = ClaudeCodeSettings(autoApproveWrite=True, model="haiku")
    import_data = {
        "claude_code": {
            "autoApproveRead": True,
            "model": "opus",
        }
    }
    input_file = tmp_path / "import.json"
    input_file.write_text(json.dumps(import_data))
    mock_manager.read_claude_code_settings.return_value = current_settings

    # Execute
    result = runner.invoke(import_settings, [str(input_file), "--merge"])

    # Assert
    assert result.exit_code == 0
    assert "Settings merged successfully" in result.output

    # Verify merge
    call_args = mock_manager.write_claude_code_settings.call_args[0][0]
    assert call_args.autoApproveRead is True  # From import
    assert call_args.autoApproveWrite is True  # From current
    assert call_args.model == "opus"  # From import (overwrite)


def test_import_dry_run(runner, mock_manager, tmp_path):
    """Test import với dry-run mode."""
    # Setup
    import_data = {
        "claude_code": {
            "autoApproveRead": True,
        }
    }
    input_file = tmp_path / "import.json"
    input_file.write_text(json.dumps(import_data))
    mock_manager.read_claude_code_settings.return_value = ClaudeCodeSettings()

    # Execute
    result = runner.invoke(import_settings, [str(input_file), "--dry-run"])

    # Assert
    assert result.exit_code == 0
    assert "Dry run" in result.output
    assert "Run without --dry-run to apply changes" in result.output
    mock_manager.write_claude_code_settings.assert_not_called()


def test_import_with_mcp(runner, mock_manager, tmp_path):
    """Test import với MCP config."""
    # Setup
    import_data = {
        "claude_code": {"autoApproveRead": True},
        "mcp": {
            "mcpServers": {
                "github": {
                    "command": "npx",
                    "args": ["-y", "server"],
                    "env": {},
                }
            }
        },
    }
    input_file = tmp_path / "import.json"
    input_file.write_text(json.dumps(import_data))
    mock_manager.read_claude_code_settings.return_value = ClaudeCodeSettings()
    mock_manager.read_mcp_config.return_value = MCPConfig()

    # Execute
    result = runner.invoke(import_settings, [str(input_file)])

    # Assert
    assert result.exit_code == 0
    assert "OK Claude Code settings imported" in result.output
    assert "OK MCP config imported" in result.output
    mock_manager.write_mcp_config.assert_called_once()


def test_import_invalid_file(runner):
    """Test import với file không tồn tại."""
    result = runner.invoke(import_settings, ["nonexistent.json"])
    assert result.exit_code != 0


def test_import_invalid_json(runner, tmp_path):
    """Test import với invalid JSON."""
    input_file = tmp_path / "invalid.json"
    input_file.write_text("{invalid json}")

    result = runner.invoke(import_settings, [str(input_file)])
    assert result.exit_code != 0
