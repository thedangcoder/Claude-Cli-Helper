# Claude CLI Helper

[English](README.md)

CLI tool để thiết lập và quản lý Claude Code settings nhanh hơn.

## Tính năng

- **Interactive Setup**: Wizard hướng dẫn cấu hình Claude Code
- **Quản lý Settings**: Đọc/ghi Claude Desktop và Claude Code settings
- **Validation Settings**: Kiểm tra và tự động sửa các vấn đề cấu hình
- **Export/Import**: Chia sẻ settings với team (hỗ trợ JSON/YAML)
- **So sánh Settings**: So sánh settings với profiles, backups hoặc files
- **Environment Variables**: Quản lý API URLs, tokens và các biến môi trường khác
- **MCP Marketplace**: Duyệt và cài đặt MCP servers từ 10+ templates
- **MCP Servers**: Thêm, xóa, liệt kê MCP server configurations
- **Profiles**: Apply preset settings và tạo custom profiles
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

# Kiểm tra settings
claude-helper settings validate
claude-helper settings validate --fix  # Tự động sửa lỗi

# Export settings
claude-helper settings export settings.json
claude-helper settings export settings.yaml --format yaml
claude-helper settings export backup.json --include-mcp

# Import settings
claude-helper settings import settings.json
claude-helper settings import settings.json --merge  # Merge với settings hiện tại
claude-helper settings import settings.json --dry-run  # Xem trước thay đổi

# So sánh settings
claude-helper settings diff --profile developer
claude-helper settings diff --backup my-backup
claude-helper settings diff --file settings.json

# Quản lý environment variables
claude-helper env set ANTHROPIC_BASE_URL https://api.custom.com
claude-helper env set ANTHROPIC_AUTH_TOKEN your-token-here
claude-helper env get ANTHROPIC_BASE_URL
claude-helper env list
claude-helper env delete ANTHROPIC_BASE_URL

# Duyệt MCP marketplace
claude-helper mcp browse
claude-helper mcp browse --category Database

# Tìm kiếm MCP templates
claude-helper mcp search "github"

# Cài đặt MCP server từ template
claude-helper mcp install filesystem
claude-helper mcp install github --name my-github
claude-helper mcp install postgres --interactive

# Liệt kê MCP servers
claude-helper mcp list

# Thêm MCP server thủ công
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

# Lưu current settings thành profile mới
claude-helper profile save my-profile -d "My custom profile"

# Xóa custom profile
claude-helper profile delete my-profile
```

## MCP Templates có sẵn

Duyệt và cài đặt MCP servers từ marketplace:

| Template | Danh mục | Mô tả |
|----------|----------|-------|
| `filesystem` | File Access | Truy cập filesystem local với permissions |
| `github` | Development | Tương tác với GitHub repositories và issues |
| `postgres` | Database | Query PostgreSQL databases |
| `sqlite` | Database | Query SQLite databases |
| `slack` | Communication | Gửi tin nhắn và tương tác với Slack |
| `google-drive` | Cloud Storage | Truy cập Google Drive files và folders |
| `brave-search` | Search | Tìm kiếm web dùng Brave Search API |
| `puppeteer` | Automation | Tự động hóa browser với Puppeteer |
| `memory` | Utility | Persistent memory cho Claude conversations |
| `fetch` | Web | Fetch và xử lý web content |

Dùng `claude-helper mcp browse` để xem chi tiết tất cả templates.

## Profiles có sẵn

| Profile | Mô tả |
|---------|-------|
| `developer` | Auto approve đọc files |
| `power-user` | Auto approve read và write |
| `filesystem-mcp` | Cấu hình MCP filesystem server |
| `github-mcp` | Cấu hình MCP GitHub server |
| `minimal` | Reset về settings mặc định |

## Các Use Case thường gặp

### Chia sẻ Settings với Team

```bash
# Export settings của bạn
claude-helper settings export team-settings.json --include-mcp

# Team members import và merge
claude-helper settings import team-settings.json --merge
```

### Cài đặt MCP Server nhanh

```bash
# Duyệt templates có sẵn
claude-helper mcp browse

# Cài đặt với cấu hình interactive
claude-helper mcp install github --interactive

# Hoặc cài nhiều cùng lúc
claude-helper mcp install filesystem
claude-helper mcp install memory
claude-helper mcp install fetch
```

### Kiểm tra và Sửa lỗi

```bash
# Check các vấn đề thường gặp
claude-helper settings validate

# Tự động sửa lỗi
claude-helper settings validate --fix
```

### So sánh Configurations

```bash
# Xem thay đổi so với profile mặc định
claude-helper settings diff --profile developer

# So sánh với backup trước khi restore
claude-helper settings diff --backup production-backup
```

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
