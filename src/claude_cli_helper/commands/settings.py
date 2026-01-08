"""Commands quản lý settings."""

import click
from rich.console import Console
from rich.table import Table

from ..settings_manager import SettingsManager

console = Console()
manager = SettingsManager()


@click.group()
def settings() -> None:
    """Quản lý Claude settings."""
    pass


@settings.command()
def show() -> None:
    """Hiển thị settings hiện tại."""
    table = Table(title="Claude Settings Paths")
    table.add_column("Type", style="cyan")
    table.add_column("Path", style="green")
    table.add_column("Exists", style="yellow")

    table.add_row(
        "Claude Desktop",
        str(manager.settings_path),
        "✓" if manager.settings_path.exists() else "✗",
    )
    table.add_row(
        "MCP Config",
        str(manager.mcp_path),
        "✓" if manager.mcp_path.exists() else "✗",
    )
    table.add_row(
        "Claude Code",
        str(manager.claude_code_path),
        "✓" if manager.claude_code_path.exists() else "✗",
    )

    console.print(table)


@settings.command()
@click.argument("key")
@click.argument("value")
def set(key: str, value: str) -> None:
    """Đặt một setting value."""
    settings_obj = manager.read_claude_code_settings()

    # Parse value
    parsed_value: str | bool
    if value.lower() in ("true", "false"):
        parsed_value = value.lower() == "true"
    else:
        parsed_value = value

    setattr(settings_obj, key, parsed_value)
    manager.write_claude_code_settings(settings_obj)

    console.print(f"[green]Đã đặt {key} = {parsed_value}[/green]")


@settings.command()
@click.argument("key")
def get(key: str) -> None:
    """Lấy một setting value."""
    settings_obj = manager.read_claude_code_settings()

    if hasattr(settings_obj, key):
        value = getattr(settings_obj, key)
        console.print(f"[cyan]{key}[/cyan] = [green]{value}[/green]")
    else:
        console.print(f"[red]Setting '{key}' không tồn tại[/red]")
