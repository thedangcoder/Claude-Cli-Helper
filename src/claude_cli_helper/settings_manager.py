"""Manager để đọc/ghi Claude settings."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import (
    get_backup_dir,
    get_claude_code_settings_path,
    get_mcp_settings_path,
    get_profiles_dir,
    get_settings_path,
)
from .models import ClaudeCodeSettings, ClaudeSettings, MCPConfig, SettingsProfile


class SettingsManager:
    """Quản lý đọc/ghi các file settings của Claude."""

    def __init__(self) -> None:
        self.settings_path = get_settings_path()
        self.mcp_path = get_mcp_settings_path()
        self.claude_code_path = get_claude_code_settings_path()
        self.backup_dir = get_backup_dir()
        self.profiles_dir = get_profiles_dir()

    def _read_json(self, path: Path) -> dict[str, Any]:
        """Read JSON file, return empty dict if file doesn't exist."""
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}

    def _write_json(self, path: Path, data: dict[str, Any]) -> None:
        """Ghi dict ra file JSON với format đẹp."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # Claude Desktop settings
    def read_settings(self) -> ClaudeSettings:
        """Đọc Claude Desktop settings."""
        data = self._read_json(self.settings_path)
        return ClaudeSettings(**data)

    def write_settings(self, settings: ClaudeSettings) -> None:
        """Ghi Claude Desktop settings."""
        self._write_json(self.settings_path, settings.model_dump(exclude_none=True))

    # MCP configuration
    def read_mcp_config(self) -> MCPConfig:
        """Đọc MCP servers configuration."""
        data = self._read_json(self.mcp_path)
        return MCPConfig(**data)

    def write_mcp_config(self, config: MCPConfig) -> None:
        """Ghi MCP servers configuration."""
        self._write_json(self.mcp_path, config.model_dump(exclude_none=True))

    # Claude Code CLI settings
    def read_claude_code_settings(self) -> ClaudeCodeSettings:
        """Đọc Claude Code CLI settings."""
        data = self._read_json(self.claude_code_path)
        return ClaudeCodeSettings(**data)

    def write_claude_code_settings(self, settings: ClaudeCodeSettings) -> None:
        """Ghi Claude Code CLI settings."""
        self._write_json(self.claude_code_path, settings.model_dump(exclude_none=True))

    # Backup/Restore
    def create_backup(self, name: str | None = None) -> Path:
        """Tạo backup tất cả settings hiện tại."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = name or f"backup_{timestamp}"
        backup_path = self.backup_dir / backup_name

        backup_path.mkdir(parents=True, exist_ok=True)

        for src_path, filename in [
            (self.settings_path, "settings.json"),
            (self.mcp_path, "claude_desktop_config.json"),
            (self.claude_code_path, "claude_code_settings.json"),
        ]:
            if src_path.exists():
                shutil.copy2(src_path, backup_path / filename)

        return backup_path

    def restore_backup(self, backup_name: str) -> None:
        """Khôi phục settings từ backup."""
        backup_path = self.backup_dir / backup_name

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup '{backup_name}' không tồn tại")

        for src_filename, dest_path in [
            ("settings.json", self.settings_path),
            ("claude_desktop_config.json", self.mcp_path),
            ("claude_code_settings.json", self.claude_code_path),
        ]:
            src = backup_path / src_filename
            if src.exists():
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest_path)

    def list_backups(self) -> list[str]:
        """List all backups."""
        if not self.backup_dir.exists():
            return []
        return [d.name for d in self.backup_dir.iterdir() if d.is_dir()]

    def delete_backup(self, backup_name: str) -> None:
        """Delete a backup."""
        backup_path = self.backup_dir / backup_name

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup '{backup_name}' does not exist")

        shutil.rmtree(backup_path)


class ProfileManager:
    """Quản lý custom profiles."""

    def __init__(self) -> None:
        self.profiles_dir = get_profiles_dir()
        self.settings = SettingsManager()

    def _get_profile_path(self, name: str) -> Path:
        """Get path to profile file."""
        return self.profiles_dir / f"{name}.json"

    def save_profile(
        self,
        name: str,
        description: str = "",
        include_claude_code: bool = True,
        include_mcp: bool = True,
        include_claude_desktop: bool = False,
    ) -> SettingsProfile:
        """Lưu current settings như một profile mới."""
        profile = SettingsProfile(name=name, description=description)

        if include_claude_code:
            profile.claude_code_settings = self.settings.read_claude_code_settings()

        if include_mcp:
            profile.mcp_config = self.settings.read_mcp_config()

        if include_claude_desktop:
            profile.claude_settings = self.settings.read_settings()

        # Lưu profile ra file
        profile_path = self._get_profile_path(name)
        profile_path.parent.mkdir(parents=True, exist_ok=True)
        with open(profile_path, "w", encoding="utf-8") as f:
            f.write(profile.model_dump_json(indent=2, exclude_none=True))

        return profile

    def load_profile(self, name: str) -> SettingsProfile | None:
        """Tải profile từ file."""
        profile_path = self._get_profile_path(name)

        if not profile_path.exists():
            return None

        with open(profile_path, "r", encoding="utf-8") as f:
            return SettingsProfile.model_validate_json(f.read())

    def delete_profile(self, name: str) -> bool:
        """Xóa profile."""
        profile_path = self._get_profile_path(name)

        if not profile_path.exists():
            return False

        profile_path.unlink()
        return True

    def list_custom_profiles(self) -> list[SettingsProfile]:
        """List tất cả custom profiles."""
        if not self.profiles_dir.exists():
            return []

        profiles = []
        for profile_file in self.profiles_dir.glob("*.json"):
            with open(profile_file, "r", encoding="utf-8") as f:
                profiles.append(SettingsProfile.model_validate_json(f.read()))

        return profiles
