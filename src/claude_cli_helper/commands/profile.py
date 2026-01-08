"""Commands quản lý profiles."""

import click
from rich.console import Console
from rich.table import Table

from ..settings_manager import SettingsManager
from ..templates import BUILTIN_PROFILES, get_profile

console = Console()
manager = SettingsManager()


@click.group()
def profile() -> None:
    """Quản lý và apply settings profiles."""
    pass


@profile.command()
def list() -> None:
    """Liệt kê các profiles có sẵn."""
    table = Table(title="Available Profiles")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="green")

    for name, p in BUILTIN_PROFILES.items():
        table.add_row(name, p.description)

    console.print(table)


@profile.command()
@click.argument("name")
def show(name: str) -> None:
    """Hiển thị chi tiết một profile."""
    p = get_profile(name)

    if not p:
        console.print(f"[red]Profile '{name}' không tồn tại[/red]")
        return

    console.print(f"[bold cyan]{p.name}[/bold cyan]")
    console.print(f"[dim]{p.description}[/dim]\n")

    if p.claude_code_settings:
        console.print("[bold]Claude Code Settings:[/bold]")
        for key, value in p.claude_code_settings.model_dump(exclude_none=True).items():
            console.print(f"  {key}: {value}")

    if p.mcp_config and p.mcp_config.mcpServers:
        console.print("\n[bold]MCP Servers:[/bold]")
        for server_name, server in p.mcp_config.mcpServers.items():
            console.print(f"  {server_name}: {server.command} {' '.join(server.args)}")


@profile.command()
@click.argument("name")
@click.option("--backup/--no-backup", default=True, help="Tạo backup trước khi apply")
def apply(name: str, backup: bool) -> None:
    """Apply một profile."""
    p = get_profile(name)

    if not p:
        console.print(f"[red]Profile '{name}' không tồn tại[/red]")
        return

    if backup:
        backup_path = manager.create_backup(f"before_{name}")
        console.print(f"[dim]Đã tạo backup: {backup_path}[/dim]")

    if p.claude_code_settings:
        manager.write_claude_code_settings(p.claude_code_settings)
        console.print("[green]✓ Đã apply Claude Code settings[/green]")

    if p.mcp_config:
        manager.write_mcp_config(p.mcp_config)
        console.print("[green]✓ Đã apply MCP config[/green]")

    if p.claude_settings:
        manager.write_settings(p.claude_settings)
        console.print("[green]✓ Đã apply Claude Desktop settings[/green]")

    console.print(f"\n[bold green]Đã apply profile '{name}' thành công![/bold green]")
