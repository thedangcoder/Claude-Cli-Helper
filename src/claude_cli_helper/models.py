"""Pydantic models cho Claude settings."""

from typing import Any

from pydantic import BaseModel, Field


class MCPServer(BaseModel):
    """Model cho một MCP server configuration."""

    command: str
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)


class MCPConfig(BaseModel):
    """Model cho toàn bộ MCP configuration."""

    mcpServers: dict[str, MCPServer] = Field(default_factory=dict)


class ClaudeSettings(BaseModel):
    """Model cho Claude settings.json."""

    # Các settings phổ biến
    theme: str = "system"
    fontSize: int = 14
    autoUpdate: bool = True

    # Custom settings
    extra: dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "allow"


class ClaudeCodeSettings(BaseModel):
    """Model cho Claude Code CLI settings."""

    # Permission settings
    allowedTools: list[str] = Field(default_factory=list)
    deniedTools: list[str] = Field(default_factory=list)

    # Behavior settings
    autoApproveAll: bool = False
    autoApproveRead: bool = False
    autoApproveWrite: bool = False
    autoApproveBash: bool = False

    # MCP settings
    mcpServers: dict[str, MCPServer] = Field(default_factory=dict)

    class Config:
        extra = "allow"


class SettingsProfile(BaseModel):
    """Model cho một profile settings có thể apply nhanh."""

    name: str
    description: str = ""
    claude_settings: ClaudeSettings | None = None
    claude_code_settings: ClaudeCodeSettings | None = None
    mcp_config: MCPConfig | None = None
