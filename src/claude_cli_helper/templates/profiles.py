"""Built-in profiles for Claude settings."""

from ..models import ClaudeCodeSettings, MCPConfig, MCPServer, SettingsProfile

# Profile for developers with auto-approve read files
DEVELOPER_PROFILE = SettingsProfile(
    name="developer",
    description="Developer profile - auto approve read files",
    claude_code_settings=ClaudeCodeSettings(
        autoApproveRead=True,
        autoApproveWrite=False,
        autoApproveBash=False,
    ),
)

# Profile for power users with more auto-approve
POWER_USER_PROFILE = SettingsProfile(
    name="power-user",
    description="Power user profile - auto approve read and write",
    claude_code_settings=ClaudeCodeSettings(
        autoApproveRead=True,
        autoApproveWrite=True,
        autoApproveBash=False,
    ),
)

# Profile with MCP filesystem server
FILESYSTEM_MCP_PROFILE = SettingsProfile(
    name="filesystem-mcp",
    description="Profile with MCP filesystem server",
    mcp_config=MCPConfig(
        mcpServers={
            "filesystem": MCPServer(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"],
            )
        }
    ),
)

# Profile with MCP GitHub server
GITHUB_MCP_PROFILE = SettingsProfile(
    name="github-mcp",
    description="Profile with MCP GitHub server",
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

# Minimal profile - reset to defaults
MINIMAL_PROFILE = SettingsProfile(
    name="minimal",
    description="Minimal profile - reset all settings to defaults",
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
    """Get profile by name."""
    return BUILTIN_PROFILES.get(name)
