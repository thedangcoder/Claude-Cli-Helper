"""Commands to manage environment variables."""

import click
from rich.console import Console
from rich.table import Table

from ..settings_manager import SettingsManager

console = Console()
manager = SettingsManager()


@click.group()
def env() -> None:
    """Manage environment variables."""
    pass


@env.command()
@click.argument("key")
@click.argument("value")
def set(key: str, value: str) -> None:
    """Set an environment variable.

    Examples:
        claude-helper env set ANTHROPIC_BASE_URL https://api.custom.com
        claude-helper env set ANTHROPIC_AUTH_TOKEN your-token
    """
    settings_obj = manager.read_claude_code_settings()

    # Get current env dict or create new one
    env_vars: dict[str, str] = dict(getattr(settings_obj, "env", {}) or {})

    # Set the new value
    env_vars[key] = value

    # Update settings
    setattr(settings_obj, "env", env_vars)
    manager.write_claude_code_settings(settings_obj)

    # Mask sensitive values in output
    display_value = value
    if any(sensitive in key.upper() for sensitive in ["TOKEN", "SECRET", "KEY", "PASSWORD"]):
        display_value = value[:10] + "..." if len(value) > 10 else "***"

    console.print(f"[green]Set {key} = {display_value}[/green]")


@env.command()
@click.argument("key")
def get(key: str) -> None:
    """Get an environment variable value.

    Examples:
        claude-helper env get ANTHROPIC_BASE_URL
    """
    settings_obj = manager.read_claude_code_settings()
    env_vars: dict[str, str] = getattr(settings_obj, "env", {}) or {}

    if key in env_vars:
        value = env_vars[key]
        # Mask sensitive values
        if any(sensitive in key.upper() for sensitive in ["TOKEN", "SECRET", "KEY", "PASSWORD"]):
            display_value = value[:10] + "..." if len(value) > 10 else "***"
        else:
            display_value = value

        console.print(f"[cyan]{key}[/cyan] = [green]{display_value}[/green]")
    else:
        console.print(f"[red]Environment variable '{key}' not found[/red]")


@env.command()
def list() -> None:
    """List all environment variables.

    Examples:
        claude-helper env list
    """
    settings_obj = manager.read_claude_code_settings()
    env_vars: dict[str, str] = getattr(settings_obj, "env", {}) or {}

    if not env_vars:
        console.print("[dim]No environment variables configured.[/dim]")
        return

    table = Table(title="Environment Variables")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")

    for key, value in sorted(env_vars.items()):
        # Mask sensitive values
        if any(sensitive in key.upper() for sensitive in ["TOKEN", "SECRET", "KEY", "PASSWORD"]):
            display_value = value[:10] + "..." if len(value) > 10 else "***"
        else:
            display_value = value

        table.add_row(key, display_value)

    console.print(table)


@env.command()
@click.argument("key")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
def delete(key: str, yes: bool) -> None:
    """Delete an environment variable.

    Examples:
        claude-helper env delete ANTHROPIC_BASE_URL
        claude-helper env delete ANTHROPIC_AUTH_TOKEN --yes
    """
    settings_obj = manager.read_claude_code_settings()
    env_vars: dict[str, str] = dict(getattr(settings_obj, "env", {}) or {})

    if key not in env_vars:
        console.print(f"[red]Environment variable '{key}' not found[/red]")
        return

    # Confirm deletion
    if not yes:
        if not click.confirm(f"Delete environment variable '{key}'?"):
            console.print("[yellow]Cancelled.[/yellow]")
            return

    # Delete the key
    del env_vars[key]

    # Update settings
    setattr(settings_obj, "env", env_vars)
    manager.write_claude_code_settings(settings_obj)

    console.print(f"[green]Deleted environment variable '{key}'[/green]")
