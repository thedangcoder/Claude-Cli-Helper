"""Commands to manage MCP servers."""

import click
from rich.console import Console
from rich.table import Table

from ..models import MCPServer
from ..settings_manager import SettingsManager

console = Console()
manager = SettingsManager()


@click.group()
def mcp() -> None:
    """Manage MCP servers configuration."""
    pass


@mcp.command()
def list() -> None:
    """List configured MCP servers."""
    config = manager.read_mcp_config()

    if not config.mcpServers:
        console.print("[yellow]No MCP servers configured[/yellow]")
        return

    table = Table(title="MCP Servers")
    table.add_column("Name", style="cyan")
    table.add_column("Command", style="green")
    table.add_column("Args", style="yellow")

    for name, server in config.mcpServers.items():
        table.add_row(name, server.command, " ".join(server.args))

    console.print(table)


@mcp.command()
@click.argument("name")
@click.argument("command")
@click.option("--args", "-a", multiple=True, help="Arguments for server")
@click.option("--env", "-e", multiple=True, help="Environment variables (KEY=VALUE)")
def add(name: str, command: str, args: tuple[str, ...], env: tuple[str, ...]) -> None:
    """Add an MCP server."""
    config = manager.read_mcp_config()

    # Parse env vars
    env_dict: dict[str, str] = {}
    for e in env:
        if "=" in e:
            k, v = e.split("=", 1)
            env_dict[k] = v

    server = MCPServer(command=command, args=list(args), env=env_dict)
    config.mcpServers[name] = server

    manager.write_mcp_config(config)
    console.print(f"[green]Added MCP server '{name}'[/green]")


@mcp.command()
@click.argument("name")
def remove(name: str) -> None:
    """Remove an MCP server."""
    config = manager.read_mcp_config()

    if name not in config.mcpServers:
        console.print(f"[red]MCP server '{name}' does not exist[/red]")
        return

    del config.mcpServers[name]
    manager.write_mcp_config(config)

    console.print(f"[green]Removed MCP server '{name}'[/green]")
