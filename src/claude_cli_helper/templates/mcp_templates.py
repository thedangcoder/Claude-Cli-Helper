"""MCP Server Templates and Marketplace."""

from ..models import MCPServer

# Popular MCP Server Templates
MCP_TEMPLATES = {
    "filesystem": MCPServer(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/path/to/directory"],
    ),
    "github": MCPServer(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": "your-token-here"},
    ),
    "postgres": MCPServer(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"],
    ),
    "sqlite": MCPServer(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-sqlite", "/path/to/database.db"],
    ),
    "slack": MCPServer(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-slack"],
        env={
            "SLACK_BOT_TOKEN": "xoxb-your-token",
            "SLACK_TEAM_ID": "T1234567890",
        },
    ),
    "google-drive": MCPServer(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-gdrive"],
        env={"GDRIVE_CLIENT_ID": "your-client-id", "GDRIVE_CLIENT_SECRET": "your-secret"},
    ),
    "brave-search": MCPServer(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-brave-search"],
        env={"BRAVE_API_KEY": "your-api-key"},
    ),
    "puppeteer": MCPServer(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-puppeteer"],
    ),
    "memory": MCPServer(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-memory"],
    ),
    "fetch": MCPServer(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-fetch"],
    ),
}

# Template metadata
TEMPLATE_INFO = {
    "filesystem": {
        "description": "Access local filesystem with permissions",
        "category": "File Access",
        "requires_config": True,
        "config_help": "Replace /path/to/directory with actual directory path",
    },
    "github": {
        "description": "Interact with GitHub repositories and issues",
        "category": "Development",
        "requires_config": True,
        "config_help": "Set GITHUB_PERSONAL_ACCESS_TOKEN in env",
    },
    "postgres": {
        "description": "Query PostgreSQL databases",
        "category": "Database",
        "requires_config": True,
        "config_help": "Replace connection string with your database URL",
    },
    "sqlite": {
        "description": "Query SQLite databases",
        "category": "Database",
        "requires_config": True,
        "config_help": "Replace /path/to/database.db with your database path",
    },
    "slack": {
        "description": "Send messages and interact with Slack",
        "category": "Communication",
        "requires_config": True,
        "config_help": "Set SLACK_BOT_TOKEN and SLACK_TEAM_ID in env",
    },
    "google-drive": {
        "description": "Access Google Drive files and folders",
        "category": "Cloud Storage",
        "requires_config": True,
        "config_help": "Set GDRIVE_CLIENT_ID and GDRIVE_CLIENT_SECRET",
    },
    "brave-search": {
        "description": "Web search using Brave Search API",
        "category": "Search",
        "requires_config": True,
        "config_help": "Set BRAVE_API_KEY in env",
    },
    "puppeteer": {
        "description": "Browser automation with Puppeteer",
        "category": "Automation",
        "requires_config": False,
        "config_help": None,
    },
    "memory": {
        "description": "Persistent memory for Claude conversations",
        "category": "Utility",
        "requires_config": False,
        "config_help": None,
    },
    "fetch": {
        "description": "Fetch and process web content",
        "category": "Web",
        "requires_config": False,
        "config_help": None,
    },
}


def get_template(name: str) -> tuple[MCPServer, dict] | None:
    """Get template and its info by name."""
    if name not in MCP_TEMPLATES:
        return None
    return MCP_TEMPLATES[name], TEMPLATE_INFO.get(name, {})


def search_templates(query: str) -> list[str]:
    """Search templates by name or description."""
    query_lower = query.lower()
    results = []

    for name, info in TEMPLATE_INFO.items():
        if query_lower in name.lower() or query_lower in info.get("description", "").lower():
            results.append(name)

    return results
