"""Main CLI entry point."""

import click
from rich.console import Console

from . import __version__
from .commands.backup import backup
from .commands.config import config
from .commands.doctor import doctor
from .commands.env import env
from .commands.hooks import hooks
from .commands.mcp import mcp
from .commands.profile import profile
from .commands.settings import settings
from .commands.setup import setup

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="claude-helper")
def main() -> None:
    """Claude CLI Helper - Setup Claude settings faster.

    Tool to manage settings, MCP servers, and profiles for Claude Desktop
    and Claude Code CLI.
    """
    pass


# Register command groups
main.add_command(setup)
main.add_command(settings)
main.add_command(mcp)
main.add_command(backup)
main.add_command(profile)
main.add_command(hooks)
main.add_command(doctor)
main.add_command(config)
main.add_command(env)


@main.command()
def info() -> None:
    """Display information about Claude CLI Helper."""
    console.print(f"[bold cyan]Claude CLI Helper[/bold cyan] v{__version__}")
    console.print("\nTool to manage Claude settings quickly.")
    console.print("\n[bold]Commands:[/bold]")
    console.print("  setup     - Interactive setup wizard")
    console.print("  settings  - Manage Claude settings")
    console.print("  mcp       - Manage MCP servers")
    console.print("  backup    - Backup/Restore settings")
    console.print("  profile   - Apply preset settings profiles")
    console.print("  hooks     - Manage notification hooks")
    console.print("  doctor    - Diagnose configuration issues")
    console.print("  config    - Manage CLAUDE.md file")
    console.print("  env       - Manage environment variables")


if __name__ == "__main__":
    main()
