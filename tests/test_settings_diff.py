"""Tests for settings diff command."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from claude_cli_helper.commands.settings import diff
from claude_cli_helper.models import ClaudeCodeSettings
from claude_cli_helper.templates.profiles import BUILTIN_PROFILES, SettingsProfile


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
def current_settings():
    """Create current settings."""
    return ClaudeCodeSettings(
        autoApproveRead=True,
        autoApproveWrite=False,
        model="sonnet",
    )


def test_diff_with_profile(runner, mock_manager, current_settings):
    """Test diff với profile."""
    # Setup
    mock_manager.read_claude_code_settings.return_value = current_settings

    # Execute
    with patch.dict(
        "claude_cli_helper.templates.profiles.BUILTIN_PROFILES",
        {
            "test-profile": SettingsProfile(
                name="test-profile",
                description="Test",
                claude_code_settings=ClaudeCodeSettings(
                    autoApproveRead=True,
                    autoApproveWrite=True,
                    model="opus",
                ),
            )
        },
    ):
        result = runner.invoke(diff, ["--profile", "test-profile"])

    # Assert
    assert result.exit_code == 0
    assert "Comparing current settings with profile 'test-profile'" in result.output


def test_diff_with_backup(runner, mock_manager, current_settings, tmp_path):
    """Test diff với backup."""
    # Setup
    mock_manager.read_claude_code_settings.return_value = current_settings
    mock_manager.backup_dir = tmp_path

    backup_data = {
        "claude_code": {
            "autoApproveRead": False,
            "model": "haiku",
        }
    }
    backup_file = tmp_path / "test-backup.json"
    backup_file.write_text(json.dumps(backup_data))

    # Execute
    result = runner.invoke(diff, ["--backup", "test-backup"])

    # Assert
    assert result.exit_code == 0
    assert "Comparing current settings with backup 'test-backup'" in result.output


def test_diff_with_file(runner, mock_manager, current_settings, tmp_path):
    """Test diff với file."""
    # Setup
    mock_manager.read_claude_code_settings.return_value = current_settings

    compare_data = {
        "claude_code": {
            "autoApproveRead": False,
            "autoApproveWrite": True,
            "model": "opus",
        }
    }
    compare_file = tmp_path / "compare.json"
    compare_file.write_text(json.dumps(compare_data))

    # Execute
    result = runner.invoke(diff, ["--file", str(compare_file)])

    # Assert
    assert result.exit_code == 0
    assert f"Comparing current settings with file 'compare.json'" in result.output


def test_diff_no_differences(runner, mock_manager):
    """Test diff khi không có sự khác biệt."""
    # Setup
    settings = ClaudeCodeSettings(autoApproveRead=True, model="sonnet")
    mock_manager.read_claude_code_settings.return_value = settings

    with patch.dict(
        "claude_cli_helper.templates.profiles.BUILTIN_PROFILES",
        {
            "same": SettingsProfile(
                name="same",
                description="Same",
                claude_code_settings=settings,
            )
        },
    ):
        result = runner.invoke(diff, ["--profile", "same"])

    # Assert
    assert result.exit_code == 0
    assert "No differences found!" in result.output


def test_diff_show_added(runner, mock_manager, tmp_path):
    """Test diff hiển thị added fields."""
    # Setup
    mock_manager.read_claude_code_settings.return_value = ClaudeCodeSettings(
        autoApproveRead=True
    )

    compare_data = {
        "claude_code": {
            "autoApproveRead": True,
            "autoApproveWrite": True,
            "model": "opus",
        }
    }
    compare_file = tmp_path / "compare.json"
    compare_file.write_text(json.dumps(compare_data))

    # Execute
    result = runner.invoke(diff, ["--file", str(compare_file)])

    # Assert
    assert result.exit_code == 0
    assert "Added in comparison:" in result.output


def test_diff_show_removed(runner, mock_manager, tmp_path):
    """Test diff hiển thị removed fields."""
    # Setup
    mock_manager.read_claude_code_settings.return_value = ClaudeCodeSettings(
        autoApproveRead=True,
        autoApproveWrite=True,
        model="sonnet",
    )

    compare_data = {"claude_code": {"autoApproveRead": True}}
    compare_file = tmp_path / "compare.json"
    compare_file.write_text(json.dumps(compare_data))

    # Execute
    result = runner.invoke(diff, ["--file", str(compare_file)])

    # Assert
    assert result.exit_code == 0
    assert "Removed in comparison:" in result.output


def test_diff_show_changed(runner, mock_manager, tmp_path):
    """Test diff hiển thị changed fields."""
    # Setup
    mock_manager.read_claude_code_settings.return_value = ClaudeCodeSettings(
        autoApproveRead=True, model="sonnet"
    )

    compare_data = {"claude_code": {"autoApproveRead": False, "model": "opus"}}
    compare_file = tmp_path / "compare.json"
    compare_file.write_text(json.dumps(compare_data))

    # Execute
    result = runner.invoke(diff, ["--file", str(compare_file)])

    # Assert
    assert result.exit_code == 0
    assert "Changed:" in result.output
    assert "Current:" in result.output
    assert "Compare:" in result.output


def test_diff_missing_source(runner, mock_manager):
    """Test diff khi không chỉ định source."""
    mock_manager.read_claude_code_settings.return_value = ClaudeCodeSettings()

    result = runner.invoke(diff)

    assert result.exit_code == 0
    assert "Please specify --profile, --backup, or --file" in result.output


def test_diff_backup_not_found(runner, mock_manager, tmp_path):
    """Test diff với backup không tồn tại."""
    mock_manager.read_claude_code_settings.return_value = ClaudeCodeSettings()
    mock_manager.backup_dir = tmp_path

    result = runner.invoke(diff, ["--backup", "nonexistent"])

    assert result.exit_code == 0
    assert "Backup 'nonexistent' not found" in result.output
