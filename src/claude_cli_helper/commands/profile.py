"""Commands to manage profiles."""

import click
from rich.console import Console
from rich.table import Table

from ..settings_manager import ProfileManager, SettingsManager
from ..templates import BUILTIN_PROFILES, get_profile

console = Console()
manager = SettingsManager()
profile_manager = ProfileManager()


def get_all_profiles() -> dict[str, tuple[type | None, str]]:
    """Get all profiles (builtin + custom).

    Returns dict with profile name -> (type, description)
    where type is 'builtin' or 'custom'.
    """
    profiles = {}

    # Builtin profiles
    for name, p in BUILTIN_PROFILES.items():
        profiles[name] = ("builtin", p.description)

    # Custom profiles
    for p in profile_manager.list_custom_profiles():
        profiles[p.name] = ("custom", p.description or "")

    return profiles


@click.group()
def profile() -> None:
    """Manage and apply settings profiles."""
    pass


@profile.command()
def list() -> None:
    """List available profiles (builtin and custom)."""
    profiles = get_all_profiles()

    table = Table(title="Available Profiles")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="yellow")
    table.add_column("Description", style="green")

    for name, (p_type, description) in profiles.items():
        table.add_row(name, p_type, description)

    console.print(table)


@profile.command()
@click.argument("name")
def show(name: str) -> None:
    """Show profile details."""
    # Check builtin first
    p = get_profile(name)

    # If not builtin, check custom
    if not p:
        p = profile_manager.load_profile(name)

    if not p:
        console.print(f"[red]Profile '{name}' does not exist[/red]")
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

    if p.claude_settings:
        console.print("\n[bold]Claude Desktop Settings:[/bold]")
        for key, value in p.claude_settings.model_dump(exclude_none=True).items():
            console.print(f"  {key}: {value}")


@profile.command()
@click.argument("name")
@click.option("--backup/--no-backup", default=True, help="Create backup before applying")
def apply(name: str, backup: bool) -> None:
    """Apply a profile (merges with existing settings)."""
    # Check builtin first
    p = get_profile(name)

    # If not builtin, check custom
    if not p:
        p = profile_manager.load_profile(name)

    if not p:
        console.print(f"[red]Profile '{name}' does not exist[/red]")
        return

    if backup:
        backup_path = manager.create_backup(f"before_{name}")
        console.print(f"[dim]Created backup: {backup_path}[/dim]")

    if p.claude_code_settings:
        # Merge with existing settings instead of replacing
        current = manager.read_claude_code_settings()
        current_data = current.model_dump()
        profile_data = p.claude_code_settings.model_dump(exclude_none=True)

        # Only update keys that are explicitly set in profile
        for key, value in profile_data.items():
            if value is not None and value != [] and value != {}:
                current_data[key] = value

        manager._write_json(manager.claude_code_path, current_data)
        console.print("[green]+ Applied Claude Code settings[/green]")

    if p.mcp_config:
        manager.write_mcp_config(p.mcp_config)
        console.print("[green]+ Applied MCP config[/green]")

    if p.claude_settings:
        manager.write_settings(p.claude_settings)
        console.print("[green]+ Applied Claude Desktop settings[/green]")

    console.print(f"\n[bold green]Successfully applied profile '{name}'![/bold green]")


@profile.command()
@click.argument("name")
@click.option("--description", "-d", default="", help="Profile description")
@click.option("--include-claude-code/--no-include-claude-code", default=True, help="Include Claude Code settings")
@click.option("--include-mcp/--no-include-mcp", default=True, help="Include MCP configuration")
@click.option("--include-claude-desktop/--no-include-claude-desktop", default=False, help="Include Claude Desktop settings")
def save(
    name: str,
    description: str,
    include_claude_code: bool,
    include_mcp: bool,
    include_claude_desktop: bool,
) -> None:
    """Save current settings as a new profile."""
    # Check if profile already exists
    if name in BUILTIN_PROFILES or profile_manager.load_profile(name):
        console.print(f"[red]Profile '{name}' already exists. Use a different name.[/red]")
        return

    profile = profile_manager.save_profile(
        name=name,
        description=description,
        include_claude_code=include_claude_code,
        include_mcp=include_mcp,
        include_claude_desktop=include_claude_desktop,
    )

    console.print(f"[bold green]Profile '{name}' saved successfully![/bold green]")
    console.print(f"[dim]Includes: Claude Code={include_claude_code}, MCP={include_mcp}, Claude Desktop={include_claude_desktop}[/dim]")


@profile.command()
@click.argument("name")
@click.confirmation_option(prompt="Are you sure you want to delete this profile?")
def delete(name: str) -> None:
    """Delete a custom profile."""
    # Cannot delete builtin profiles
    if name in BUILTIN_PROFILES:
        console.print(f"[red]Cannot delete builtin profile '{name}'.[/red]")
        return

    if profile_manager.delete_profile(name):
        console.print(f"[bold green]Profile '{name}' deleted successfully![/bold green]")
    else:
        console.print(f"[red]Profile '{name}' does not exist.[/red]")
