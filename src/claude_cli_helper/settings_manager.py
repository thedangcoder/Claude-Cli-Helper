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
    get_settings_path,
)
from .models import ClaudeCodeSettings, ClaudeSettings, MCPConfig


class SettingsManager:
    """Quản lý đọc/ghi các file settings của Claude."""

    def __init__(self) -> None:
        self.settings_path = get_settings_path()
        self.mcp_path = get_mcp_settings_path()
        self.claude_code_path = get_claude_code_settings_path()
        self.backup_dir = get_backup_dir()

    def _read_json(self, path: Path) -> dict[str, Any]:
        """Đọc file JSON, trả về dict rỗng nếu file không tồn tại."""
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

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
        """Liệt kê tất cả backups."""
        if not self.backup_dir.exists():
            return []
        return [d.name for d in self.backup_dir.iterdir() if d.is_dir()]
