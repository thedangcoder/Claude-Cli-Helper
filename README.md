# Claude CLI Helper

[Tiếng Việt](README.vi.md)

CLI tool to setup and manage Claude Code settings faster.

## Features

- **Settings Management**: Read/write Claude Desktop and Claude Code settings
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

## Usage

```bash
# Show info
claude-helper info

# Show settings paths
claude-helper settings show

# Set a setting
claude-helper settings set autoApproveRead true

# List MCP servers
claude-helper mcp list

# Add MCP server
claude-helper mcp add filesystem npx -a "-y" -a "@modelcontextprotocol/server-filesystem"

# Create backup
claude-helper backup create --name my-backup

# List profiles
claude-helper profile list

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
