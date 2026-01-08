"""Commands for backup/restore."""

import click
from rich.console import Console
from rich.table import Table

from ..settings_manager import SettingsManager

console = Console()
manager = SettingsManager()


@click.group()
def backup() -> None:
    """Manage backup and restore settings."""
    pass


@backup.command()
@click.option("--name", "-n", help="Backup name (default: timestamp)")
def create(name: str | None) -> None:
    """Create a backup of current settings."""
    try:
        backup_path = manager.create_backup(name)
        console.print(f"[green]Created backup at: {backup_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error creating backup: {e}[/red]")


@backup.command()
def list() -> None:
    """List existing backups."""
    backups = manager.list_backups()

    if not backups:
        console.print("[yellow]No backups found[/yellow]")
        return

    table = Table(title="Backups")
    table.add_column("Name", style="cyan")

    for b in sorted(backups):
        table.add_row(b)

    console.print(table)


@backup.command()
@click.argument("name")
@click.confirmation_option(prompt="Are you sure you want to restore this backup?")
def restore(name: str) -> None:
    """Restore settings from a backup."""
    try:
        manager.restore_backup(name)
        console.print(f"[green]Restored backup '{name}'[/green]")
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
    except Exception as e:
        console.print(f"[red]Error restoring: {e}[/red]")


@backup.command()
@click.argument("name")
@click.confirmation_option(prompt="Are you sure you want to delete this backup?")
def delete(name: str) -> None:
    """Delete a backup."""
    try:
        manager.delete_backup(name)
        console.print(f"[green]Deleted backup '{name}'[/green]")
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
    except Exception as e:
        console.print(f"[red]Error deleting: {e}[/red]")
