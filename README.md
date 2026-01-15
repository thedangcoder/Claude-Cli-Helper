# Claude CLI Helper

[Tiếng Việt](README.vi.md)

CLI tool to setup and manage Claude Code settings faster.

## Features

- **Interactive Setup**: Wizard to configure Claude Code with guided prompts
- **Settings Management**: Read/write Claude Desktop and Claude Code settings
- **Settings Validation**: Check and auto-fix common configuration issues
- **Export/Import**: Share settings with your team (JSON/YAML support)
- **Settings Diff**: Compare settings with profiles, backups, or files
- **Environment Variables**: Manage API URLs, tokens, and other environment variables
- **MCP Marketplace**: Browse and install MCP servers from 10+ templates
- **MCP Servers**: Add, remove, list MCP server configurations
- **Profiles**: Apply preset settings profiles and create custom ones
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

# Validate settings
claude-helper settings validate
claude-helper settings validate --fix  # Auto-fix common issues

# Export settings
claude-helper settings export settings.json
claude-helper settings export settings.yaml --format yaml
claude-helper settings export backup.json --include-mcp

# Import settings
claude-helper settings import settings.json
claude-helper settings import settings.json --merge  # Merge with existing
claude-helper settings import settings.json --dry-run  # Preview changes

# Compare settings
claude-helper settings diff --profile developer
claude-helper settings diff --backup my-backup
claude-helper settings diff --file settings.json

# Manage environment variables
claude-helper env set ANTHROPIC_BASE_URL https://api.custom.com
claude-helper env set ANTHROPIC_AUTH_TOKEN your-token-here
claude-helper env get ANTHROPIC_BASE_URL
claude-helper env list
claude-helper env delete ANTHROPIC_BASE_URL

# Browse MCP marketplace
claude-helper mcp browse
claude-helper mcp browse --category Database

# Search MCP templates
claude-helper mcp search "github"

# Install MCP server from template
claude-helper mcp install filesystem
claude-helper mcp install github --name my-github
claude-helper mcp install postgres --interactive

# List MCP servers
claude-helper mcp list

# Add MCP server manually
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

# Save current settings as a new profile
claude-helper profile save my-profile -d "My custom profile"

# Delete custom profile
claude-helper profile delete my-profile
```

## Available MCP Templates

Browse and install MCP servers from our marketplace:

| Template | Category | Description |
|----------|----------|-------------|
| `filesystem` | File Access | Access local filesystem with permissions |
| `github` | Development | Interact with GitHub repositories and issues |
| `postgres` | Database | Query PostgreSQL databases |
| `sqlite` | Database | Query SQLite databases |
| `slack` | Communication | Send messages and interact with Slack |
| `google-drive` | Cloud Storage | Access Google Drive files and folders |
| `brave-search` | Search | Web search using Brave Search API |
| `puppeteer` | Automation | Browser automation with Puppeteer |
| `memory` | Utility | Persistent memory for Claude conversations |
| `fetch` | Web | Fetch and process web content |

Use `claude-helper mcp browse` to see all templates with detailed information.

## Available Profiles

| Profile | Description |
|---------|-------------|
| `developer` | Auto approve read files |
| `power-user` | Auto approve read and write |
| `filesystem-mcp` | MCP filesystem server config |
| `github-mcp` | MCP GitHub server config |
| `minimal` | Reset to default settings |

## Common Use Cases

### Share Settings with Your Team

```bash
# Export your settings
claude-helper settings export team-settings.json --include-mcp

# Team members import with merge
claude-helper settings import team-settings.json --merge
```

### Quick MCP Server Setup

```bash
# Browse available templates
claude-helper mcp browse

# Install with interactive configuration
claude-helper mcp install github --interactive

# Or install multiple at once
claude-helper mcp install filesystem
claude-helper mcp install memory
claude-helper mcp install fetch
```

### Validate and Fix Issues

```bash
# Check for common issues
claude-helper settings validate

# Auto-fix problems
claude-helper settings validate --fix
```

### Compare Configurations

```bash
# See what changed from default profile
claude-helper settings diff --profile developer

# Compare with a backup before restoring
claude-helper settings diff --backup production-backup
```

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
