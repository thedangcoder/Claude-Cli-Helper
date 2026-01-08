"""Tests for models."""

from claude_cli_helper.models import ClaudeCodeSettings, MCPConfig, MCPServer


def test_mcp_server_defaults():
    """Test MCPServer với giá trị mặc định."""
    server = MCPServer(command="npx")
    assert server.command == "npx"
    assert server.args == []
    assert server.env == {}


def test_mcp_server_with_args():
    """Test MCPServer với arguments."""
    server = MCPServer(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem"],
        env={"HOME": "/home/user"},
    )
    assert server.command == "npx"
    assert len(server.args) == 2
    assert server.env["HOME"] == "/home/user"


def test_mcp_config():
    """Test MCPConfig."""
    config = MCPConfig(
        mcpServers={
            "filesystem": MCPServer(command="npx", args=["-y", "server"]),
        }
    )
    assert "filesystem" in config.mcpServers
    assert config.mcpServers["filesystem"].command == "npx"


def test_claude_code_settings_defaults():
    """Test ClaudeCodeSettings với giá trị mặc định."""
    settings = ClaudeCodeSettings()
    assert settings.autoApproveAll is False
    assert settings.autoApproveRead is False
    assert settings.autoApproveWrite is False
    assert settings.autoApproveBash is False


def test_claude_code_settings_custom():
    """Test ClaudeCodeSettings với giá trị custom."""
    settings = ClaudeCodeSettings(
        autoApproveRead=True,
        autoApproveWrite=True,
    )
    assert settings.autoApproveRead is True
    assert settings.autoApproveWrite is True
    assert settings.autoApproveBash is False
