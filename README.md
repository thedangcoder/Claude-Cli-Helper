# Claude CLI Helper

CLI tool để thiết lập và quản lý Claude Code settings nhanh hơn.

## Tính năng

- **Quản lý Settings**: Đọc/ghi Claude Desktop và Claude Code settings
- **MCP Servers**: Thêm, xóa, liệt kê MCP server configurations
- **Profiles**: Apply các preset settings có sẵn
- **Backup/Restore**: Sao lưu và khôi phục settings

## Cài đặt

```bash
# Cài đặt từ source
pip install -e .

# Hoặc với dev dependencies
pip install -e ".[dev]"
```

## Sử dụng

```bash
# Xem thông tin
claude-helper info

# Xem settings paths
claude-helper settings show

# Đặt một setting
claude-helper settings set autoApproveRead true

# Liệt kê MCP servers
claude-helper mcp list

# Thêm MCP server
claude-helper mcp add filesystem npx -a "-y" -a "@modelcontextprotocol/server-filesystem"

# Tạo backup
claude-helper backup create --name my-backup

# Liệt kê profiles
claude-helper profile list

# Apply profile
claude-helper profile apply developer
```

## Profiles có sẵn

| Profile | Mô tả |
|---------|-------|
| `developer` | Auto approve đọc files |
| `power-user` | Auto approve read và write |
| `filesystem-mcp` | Cấu hình MCP filesystem server |
| `github-mcp` | Cấu hình MCP GitHub server |
| `minimal` | Reset về settings mặc định |

## Development

```bash
# Chạy tests
pytest

# Chạy linting
ruff check .

# Type checking
mypy src
```

## License

MIT
