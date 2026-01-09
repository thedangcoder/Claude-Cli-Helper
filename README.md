# Claude CLI Helper

[Tiếng Việt](README.vi.md)

CLI tool to setup and manage Claude Code settings faster.

## Features

- **Interactive Setup**: Wizard to configure Claude Code with guided prompts
- **Settings Management**: Read/write Claude Desktop and Claude Code settings
- **Environment Variables**: Manage API URLs, tokens, and other environment variables
- **MCP Servers**: Add, remove, list MCP server configurations
- **Profiles**: Apply preset settings profiles
- **Backup/Restore**: Backup and restore settings

## Installation

```bash
# Install from source
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

## Quick Start

```bash
# Interactive setup wizard
claude-helper setup
```

## Usage

```bash
# Show info
claude-helper info

# Interactive setup (recommended for first time)
claude-helper setup

# Show settings paths
claude-helper settings show

# List current settings
claude-helper settings list

# Set a setting
claude-helper settings set autoApproveRead true

# Get a setting
claude-helper settings get model

# Manage environment variables
claude-helper env set ANTHROPIC_BASE_URL https://api.custom.com
claude-helper env set ANTHROPIC_AUTH_TOKEN your-token-here
claude-helper env get ANTHROPIC_BASE_URL
claude-helper env list
claude-helper env delete ANTHROPIC_BASE_URL

# List MCP servers
claude-helper mcp list

# Add MCP server
claude-helper mcp add filesystem npx -a "-y" -a "@modelcontextprotocol/server-filesystem"

# Remove MCP server
claude-helper mcp remove filesystem

# Create backup
claude-helper backup create --name my-backup

# List backups
claude-helper backup list

# Restore backup
claude-helper backup restore my-backup

# Delete backup
claude-helper backup delete my-backup

# List profiles
claude-helper profile list

# Show profile details
claude-helper profile show developer

# Apply profile
claude-helper profile apply developer
```

## Available Profiles

| Profile | Description |
|---------|-------------|
| `developer` | Auto approve read files |
| `power-user` | Auto approve read and write |
| `filesystem-mcp` | MCP filesystem server config |
| `github-mcp` | MCP GitHub server config |
| `minimal` | Reset to default settings |

## Development

```bash
# Run tests
pytest

# Run linting
ruff check .

# Type checking
mypy src
```

## License

MIT
