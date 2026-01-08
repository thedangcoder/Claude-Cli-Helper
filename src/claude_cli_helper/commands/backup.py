"""Commands backup/restore."""

import click
from rich.console import Console
from rich.table import Table

from ..settings_manager import SettingsManager

console = Console()
manager = SettingsManager()


@click.group()
def backup() -> None:
    """Quản lý backup và restore settings."""
    pass


@backup.command()
@click.option("--name", "-n", help="Tên backup (mặc định: timestamp)")
def create(name: str | None) -> None:
    """Tạo backup settings hiện tại."""
    try:
        backup_path = manager.create_backup(name)
        console.print(f"[green]Đã tạo backup tại: {backup_path}[/green]")
    except Exception as e:
        console.print(f"[red]Lỗi tạo backup: {e}[/red]")


@backup.command()
def list() -> None:
    """Liệt kê các backup hiện có."""
    backups = manager.list_backups()

    if not backups:
        console.print("[yellow]Chưa có backup nào[/yellow]")
        return

    table = Table(title="Backups")
    table.add_column("Name", style="cyan")

    for b in sorted(backups):
        table.add_row(b)

    console.print(table)


@backup.command()
@click.argument("name")
@click.confirmation_option(prompt="Bạn có chắc muốn restore backup này?")
def restore(name: str) -> None:
    """Khôi phục settings từ backup."""
    try:
        manager.restore_backup(name)
        console.print(f"[green]Đã restore backup '{name}'[/green]")
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
    except Exception as e:
        console.print(f"[red]Lỗi restore: {e}[/red]")
