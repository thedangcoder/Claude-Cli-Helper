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


@mcp.command()
@click.option("--category", "-c", help="Filter by category")
def browse(category: str | None) -> None:
    """Browse available MCP server templates."""
    from ..templates.mcp_templates import TEMPLATE_INFO

    console.print("[bold]Available MCP Server Templates[/bold]\n")

    # Group by category
    categories: dict[str, list[tuple[str, dict]]] = {}
    for name, info in TEMPLATE_INFO.items():
        cat = info.get("category", "Other")
        if category and cat.lower() != category.lower():
            continue
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((name, info))

    for cat, templates in sorted(categories.items()):
        console.print(f"[bold cyan]{cat}[/bold cyan]")
        for name, info in templates:
            desc = info.get("description", "")
            requires = " [yellow](requires config)[/yellow]" if info.get("requires_config") else ""
            console.print(f"  [green]{name}[/green]{requires}")
            console.print(f"    {desc}")
        console.print()

    console.print(f"[dim]Total: {len(TEMPLATE_INFO)} templates available[/dim]")
    console.print("[dim]Use 'claude-helper mcp install <name>' to install a template[/dim]")


@mcp.command()
@click.argument("query")
def search(query: str) -> None:
    """Search for MCP server templates."""
    from ..templates.mcp_templates import TEMPLATE_INFO, search_templates

    results = search_templates(query)

    if not results:
        console.print(f"[yellow]No templates found matching '{query}'[/yellow]")
        return

    console.print(f"[bold]Search results for '{query}':[/bold]\n")

    for name in results:
        info = TEMPLATE_INFO[name]
        desc = info.get("description", "")
        cat = info.get("category", "Other")
        requires = " [yellow](requires config)[/yellow]" if info.get("requires_config") else ""

        console.print(f"[green]{name}[/green] [{cat}]{requires}")
        console.print(f"  {desc}")
        console.print()

    console.print(f"[dim]Found {len(results)} template(s)[/dim]")


@mcp.command()
@click.argument("template_name")
@click.option("--name", "-n", help="Custom name for the server (default: template name)")
@click.option("--interactive", "-i", is_flag=True, help="Interactive configuration")
def install(template_name: str, name: str | None, interactive: bool) -> None:
    """Install an MCP server from a template."""
    from ..templates.mcp_templates import get_template

    result = get_template(template_name)
    if not result:
        console.print(f"[red]Template '{template_name}' not found[/red]")
        console.print("\n[dim]Use 'claude-helper mcp browse' to see available templates[/dim]")
        return

    template, info = result
    server_name = name or template_name

    # Check if already exists
    config = manager.read_mcp_config()
    if server_name in config.mcpServers:
        if not click.confirm(f"Server '{server_name}' already exists. Overwrite?"):
            console.print("[yellow]Installation cancelled[/yellow]")
            return

    # Show template info
    console.print(f"[bold]Installing MCP Server: {template_name}[/bold]")
    console.print(f"Description: {info.get('description', 'N/A')}")

    if info.get("requires_config"):
        console.print(f"\n[yellow]! Configuration required:[/yellow]")
        console.print(f"  {info.get('config_help', 'See documentation')}")

        if interactive:
            # Interactive configuration
            import questionary

            console.print("\n[bold]Interactive Configuration:[/bold]")

            # Customize args
            if template.args:
                console.print(f"\nDefault args: {template.args}")
                custom_args = questionary.text(
                    "Custom args (comma-separated, or Enter to keep default):",
                    default="",
                ).ask()
                if custom_args:
                    template.args = [arg.strip() for arg in custom_args.split(",")]

            # Customize env
            if template.env:
                console.print(f"\nEnvironment variables needed:")
                new_env = {}
                for key, default_val in template.env.items():
                    val = questionary.text(
                        f"{key}:",
                        default=default_val,
                    ).ask()
                    if val:
                        new_env[key] = val
                template.env = new_env

        else:
            console.print("\n[dim]Tip: Use --interactive for guided configuration[/dim]")

    # Install
    config.mcpServers[server_name] = template
    manager.write_mcp_config(config)

    console.print(f"\n[green]OK MCP server '{server_name}' installed successfully![/green]")

    if info.get("requires_config") and not interactive:
        console.print("\n[yellow]! Don't forget to configure the server![/yellow]")
        console.print(f"  Edit: {manager.mcp_path}")
        console.print(f"  {info.get('config_help', '')}")
