# Claude CLI Helper

[English](README.md)

CLI tool để thiết lập và quản lý Claude Code settings nhanh hơn.

## Tính năng

- **Interactive Setup**: Wizard hướng dẫn cấu hình Claude Code
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

## Bắt đầu nhanh

```bash
# Chạy wizard setup
claude-helper setup
```

## Sử dụng

```bash
# Xem thông tin
claude-helper info

# Interactive setup (khuyên dùng lần đầu)
claude-helper setup

# Xem settings paths
claude-helper settings show

# Liệt kê settings hiện tại
claude-helper settings list

# Đặt một setting
claude-helper settings set autoApproveRead true

# Lấy một setting
claude-helper settings get model

# Liệt kê MCP servers
claude-helper mcp list

# Thêm MCP server
claude-helper mcp add filesystem npx -a "-y" -a "@modelcontextprotocol/server-filesystem"

# Xóa MCP server
claude-helper mcp remove filesystem

# Tạo backup
claude-helper backup create --name my-backup

# Liệt kê backups
claude-helper backup list

# Khôi phục backup
claude-helper backup restore my-backup

# Xóa backup
claude-helper backup delete my-backup

# Liệt kê profiles
claude-helper profile list

# Xem chi tiết profile
claude-helper profile show developer

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

## Phát triển

```bash
# Chạy tests
pytest

# Chạy linting
ruff check .

# Kiểm tra type
mypy src
```

## Giấy phép

MIT
