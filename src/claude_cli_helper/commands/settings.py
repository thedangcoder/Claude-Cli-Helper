"""Commands to manage settings."""

import json

import click
from rich.console import Console
from rich.table import Table

from ..settings_manager import SettingsManager

console = Console()
manager = SettingsManager()


@click.group()
def settings() -> None:
    """Manage Claude settings."""
    pass


@settings.command()
def show() -> None:
    """Show current settings paths."""
    table = Table(title="Claude Settings Paths")
    table.add_column("Type", style="cyan")
    table.add_column("Path", style="green")
    table.add_column("Exists", style="yellow")

    table.add_row(
        "Claude Desktop",
        str(manager.settings_path),
        "Y" if manager.settings_path.exists() else "N",
    )
    table.add_row(
        "MCP Config",
        str(manager.mcp_path),
        "Y" if manager.mcp_path.exists() else "N",
    )
    table.add_row(
        "Claude Code",
        str(manager.claude_code_path),
        "Y" if manager.claude_code_path.exists() else "N",
    )

    console.print(table)


@settings.command()
@click.argument("key")
@click.argument("value")
def set(key: str, value: str) -> None:
    """Set a setting value."""
    settings_obj = manager.read_claude_code_settings()

    # Parse value
    parsed_value: str | bool
    if value.lower() in ("true", "false"):
        parsed_value = value.lower() == "true"
    else:
        parsed_value = value

    setattr(settings_obj, key, parsed_value)
    manager.write_claude_code_settings(settings_obj)

    console.print(f"[green]Set {key} = {parsed_value}[/green]")


def _format_value(value: object) -> str:
    """Format value for display."""
    if type(value) is bool:
        return str(value).lower()
    if type(value) in (dict, list):
        return json.dumps(value, indent=2, ensure_ascii=False)
    return str(value)


@settings.command()
@click.argument("key")
def get(key: str) -> None:
    """Get a setting value."""
    settings_obj = manager.read_claude_code_settings()

    if hasattr(settings_obj, key):
        value = getattr(settings_obj, key)
        formatted = _format_value(value)
        if type(value) in (dict, list) and value:
            console.print(f"[cyan]{key}[/cyan] =")
            print(formatted)
        else:
            console.print(f"[cyan]{key}[/cyan] = [green]{formatted}[/green]")
    else:
        console.print(f"[red]Setting '{key}' does not exist[/red]")


@settings.command()
def list() -> None:
    """List all current settings."""
    settings_obj = manager.read_claude_code_settings()

    console.print("[bold]Claude Code Settings[/bold]\n")

    for key, value in settings_obj.model_dump().items():
        if value is not None and value != [] and value != {}:
            formatted = _format_value(value)
            if type(value) in (dict, list):
                console.print(f"[cyan]{key}[/cyan] =")
                print(formatted)
            else:
                console.print(f"[cyan]{key}[/cyan] = [green]{formatted}[/green]")
