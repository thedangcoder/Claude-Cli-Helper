"""Main CLI entry point."""

import click
from rich.console import Console

from . import __version__
from .commands.backup import backup
from .commands.mcp import mcp
from .commands.profile import profile
from .commands.settings import settings

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="claude-helper")
def main() -> None:
    """Claude CLI Helper - Thiết lập Claude settings nhanh hơn.

    Tool giúp quản lý settings, MCP servers, và profiles cho Claude Desktop
    và Claude Code CLI.
    """
    pass


# Register command groups
main.add_command(settings)
main.add_command(mcp)
main.add_command(backup)
main.add_command(profile)


@main.command()
def info() -> None:
    """Hiển thị thông tin về Claude CLI Helper."""
    console.print(f"[bold cyan]Claude CLI Helper[/bold cyan] v{__version__}")
    console.print("\nTool giúp quản lý Claude settings một cách nhanh chóng.")
    console.print("\n[bold]Commands:[/bold]")
    console.print("  settings  - Quản lý Claude settings")
    console.print("  mcp       - Quản lý MCP servers")
    console.print("  backup    - Backup/Restore settings")
    console.print("  profile   - Apply settings profiles có sẵn")


if __name__ == "__main__":
    main()
