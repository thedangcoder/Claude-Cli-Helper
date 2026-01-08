"""Built-in profiles cho Claude settings."""

from ..models import ClaudeCodeSettings, MCPConfig, MCPServer, SettingsProfile

# Profile cho developer với auto-approve read files
DEVELOPER_PROFILE = SettingsProfile(
    name="developer",
    description="Profile cho developer - auto approve đọc files",
    claude_code_settings=ClaudeCodeSettings(
        autoApproveRead=True,
        autoApproveWrite=False,
        autoApproveBash=False,
    ),
)

# Profile cho power user với nhiều auto-approve hơn
POWER_USER_PROFILE = SettingsProfile(
    name="power-user",
    description="Profile cho power user - auto approve read và write",
    claude_code_settings=ClaudeCodeSettings(
        autoApproveRead=True,
        autoApproveWrite=True,
        autoApproveBash=False,
    ),
)

# Profile với MCP filesystem server
FILESYSTEM_MCP_PROFILE = SettingsProfile(
    name="filesystem-mcp",
    description="Profile với MCP filesystem server",
    mcp_config=MCPConfig(
        mcpServers={
            "filesystem": MCPServer(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"],
            )
        }
    ),
)

# Profile với MCP GitHub server
GITHUB_MCP_PROFILE = SettingsProfile(
    name="github-mcp",
    description="Profile với MCP GitHub server",
    mcp_config=MCPConfig(
        mcpServers={
            "github": MCPServer(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-github"],
                env={"GITHUB_PERSONAL_ACCESS_TOKEN": "<your-token>"},
            )
        }
    ),
)

# Profile minimal - reset về mặc định
MINIMAL_PROFILE = SettingsProfile(
    name="minimal",
    description="Profile minimal - tất cả settings về mặc định",
    claude_code_settings=ClaudeCodeSettings(
        autoApproveAll=False,
        autoApproveRead=False,
        autoApproveWrite=False,
        autoApproveBash=False,
    ),
)

BUILTIN_PROFILES: dict[str, SettingsProfile] = {
    "developer": DEVELOPER_PROFILE,
    "power-user": POWER_USER_PROFILE,
    "filesystem-mcp": FILESYSTEM_MCP_PROFILE,
    "github-mcp": GITHUB_MCP_PROFILE,
    "minimal": MINIMAL_PROFILE,
}


def get_profile(name: str) -> SettingsProfile | None:
    """Lấy profile theo tên."""
    return BUILTIN_PROFILES.get(name)
