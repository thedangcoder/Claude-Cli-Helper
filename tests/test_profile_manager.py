"""Tests for ProfileManager."""

from pathlib import Path
from unittest.mock import patch

from claude_cli_helper.models import ClaudeCodeSettings, MCPConfig, MCPServer, SettingsProfile
from claude_cli_helper.settings_manager import ProfileManager


def test_profile_manager_save_and_load(tmp_path: Path) -> None:
    """Test saving and loading a custom profile."""
    with patch("claude_cli_helper.settings_manager.get_profiles_dir", return_value=tmp_path):
        manager = ProfileManager()

        # Save a profile
        profile = manager.save_profile(
            name="test-profile",
            description="Test profile description",
            include_claude_code=True,
            include_mcp=True,
            include_claude_desktop=False,
        )

        assert profile.name == "test-profile"
        assert profile.description == "Test profile description"

        # Load the profile
        loaded = manager.load_profile("test-profile")
        assert loaded is not None
        assert loaded.name == "test-profile"
        assert loaded.description == "Test profile description"


def test_profile_manager_load_nonexistent(tmp_path: Path) -> None:
    """Test loading a nonexistent profile returns None."""
    with patch("claude_cli_helper.settings_manager.get_profiles_dir", return_value=tmp_path):
        manager = ProfileManager()

        loaded = manager.load_profile("nonexistent")
        assert loaded is None


def test_profile_manager_delete(tmp_path: Path) -> None:
    """Test deleting a profile."""
    with patch("claude_cli_helper.settings_manager.get_profiles_dir", return_value=tmp_path):
        manager = ProfileManager()

        # Save a profile
        manager.save_profile(name="delete-test")

        # Verify it exists
        assert manager.load_profile("delete-test") is not None

        # Delete it
        assert manager.delete_profile("delete-test") is True

        # Verify it's gone
        assert manager.load_profile("delete-test") is None


def test_profile_manager_delete_nonexistent(tmp_path: Path) -> None:
    """Test deleting a nonexistent profile returns False."""
    with patch("claude_cli_helper.settings_manager.get_profiles_dir", return_value=tmp_path):
        manager = ProfileManager()

        assert manager.delete_profile("nonexistent") is False


def test_profile_manager_list_custom(tmp_path: Path) -> None:
    """Test listing custom profiles."""
    with patch("claude_cli_helper.settings_manager.get_profiles_dir", return_value=tmp_path):
        manager = ProfileManager()

        # Initially empty
        profiles = manager.list_custom_profiles()
        assert len(profiles) == 0

        # Save some profiles
        manager.save_profile(name="profile-1", description="First profile")
        manager.save_profile(name="profile-2", description="Second profile")

        # List them
        profiles = manager.list_custom_profiles()
        assert len(profiles) == 2

        profile_names = {p.name for p in profiles}
        assert "profile-1" in profile_names
        assert "profile-2" in profile_names


def test_profile_manager_get_profile_path(tmp_path: Path) -> None:
    """Test _get_profile_path returns correct path."""
    with patch("claude_cli_helper.settings_manager.get_profiles_dir", return_value=tmp_path):
        manager = ProfileManager()

        path = manager._get_profile_path("test-profile")
        assert path == tmp_path / "test-profile.json"


def test_profile_manager_save_excludes_none_values(tmp_path: Path) -> None:
    """Test that None values are excluded when saving profile."""
    with patch("claude_cli_helper.settings_manager.get_profiles_dir", return_value=tmp_path):
        manager = ProfileManager()

        manager.save_profile(name="minimal", include_claude_desktop=False)

        # Load and verify Claude Desktop settings is None
        profile = manager.load_profile("minimal")
        assert profile is not None
        assert profile.claude_settings is None
