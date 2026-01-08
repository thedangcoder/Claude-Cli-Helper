# Claude CLI Helper

CLI tool to setup and manage Claude Code settings faster.

CLI tool để thiết lập và quản lý Claude Code settings nhanh hơn.

## Features / Tính năng

- **Settings Management**: Read/write Claude Desktop and Claude Code settings
- **MCP Servers**: Add, remove, list MCP server configurations
- **Profiles**: Apply preset settings profiles
- **Backup/Restore**: Backup and restore settings

---

- **Quản lý Settings**: Đọc/ghi Claude Desktop và Claude Code settings
- **MCP Servers**: Thêm, xóa, liệt kê MCP server configurations
- **Profiles**: Apply các preset settings có sẵn
- **Backup/Restore**: Sao lưu và khôi phục settings

## Installation / Cài đặt

```bash
# Install from source / Cài đặt từ source
pip install -e .

# Or with dev dependencies / Hoặc với dev dependencies
pip install -e ".[dev]"
```

## Usage / Sử dụng

```bash
# Show info / Xem thông tin
claude-helper info

# Show settings paths / Xem settings paths
claude-helper settings show

# Set a setting / Đặt một setting
claude-helper settings set autoApproveRead true

# List MCP servers / Liệt kê MCP servers
claude-helper mcp list

# Add MCP server / Thêm MCP server
claude-helper mcp add filesystem npx -a "-y" -a "@modelcontextprotocol/server-filesystem"

# Create backup / Tạo backup
claude-helper backup create --name my-backup

# List profiles / Liệt kê profiles
claude-helper profile list

# Apply profile / Apply profile
claude-helper profile apply developer
```

## Available Profiles / Profiles có sẵn

| Profile | Description | Mô tả |
|---------|-------------|-------|
| `developer` | Auto approve read files | Auto approve đọc files |
| `power-user` | Auto approve read and write | Auto approve read và write |
| `filesystem-mcp` | MCP filesystem server config | Cấu hình MCP filesystem server |
| `github-mcp` | MCP GitHub server config | Cấu hình MCP GitHub server |
| `minimal` | Reset to default settings | Reset về settings mặc định |

## Development / Phát triển

```bash
# Run tests / Chạy tests
pytest

# Run linting / Chạy linting
ruff check .

# Type checking / Kiểm tra type
mypy src
```

## License / Giấy phép

MIT
