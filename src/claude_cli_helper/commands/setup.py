"""Interactive setup wizard for Claude Code settings."""

import click
import questionary
from questionary import Style
from rich.console import Console

from ..settings_manager import SettingsManager

console = Console()
manager = SettingsManager()

# Custom style for questionary
custom_style = Style([
    ("qmark", "fg:cyan bold"),
    ("question", "bold"),
    ("answer", "fg:green"),
    ("pointer", "fg:cyan bold"),
    ("highlighted", "fg:cyan bold"),
    ("selected", "fg:green"),
])


def _show_current_settings() -> None:
    """Display current settings."""
    current = manager.read_claude_code_settings()
    data = current.model_dump()

    # Filter out empty values
    has_settings = False
    for key, value in data.items():
        if value is not None and value != [] and value != {}:
            has_settings = True
            break

    if not has_settings:
        console.print("[dim]No settings configured yet.[/dim]\n")
        return

    console.print("[bold]Current Settings:[/bold]")

    # Model
    model = getattr(current, "model", None)
    if model:
        console.print(f"  Model: [cyan]{model}[/cyan]")

    # Auto-approve
    approves = []
    if current.autoApproveAll:
        approves.append("all")
    else:
        if current.autoApproveRead:
            approves.append("read")
        if current.autoApproveWrite:
            approves.append("write")
        if current.autoApproveBash:
            approves.append("bash")

    if approves:
        console.print(f"  Auto-approve: [cyan]{', '.join(approves)}[/cyan]")
    else:
        console.print("  Auto-approve: [dim]none[/dim]")

    # Environment
    env = getattr(current, "env", None)
    if env:
        console.print(f"  Environment variables: [cyan]{len(env)} configured[/cyan]")
        for key in env:
            if "TOKEN" in key or "SECRET" in key or "KEY" in key:
                console.print(f"    {key}: [dim]***[/dim]")
            else:
                console.print(f"    {key}: [dim]{env[key]}[/dim]")

    console.print()


@click.command()
def setup() -> None:
    """Interactive setup wizard for Claude Code settings."""
    console.print("\n[bold cyan]Claude Code Setup Wizard[/bold cyan]\n")

    # Show current settings
    _show_current_settings()

    # Load current settings
    current = manager.read_claude_code_settings()

    # Auto-approve settings
    console.print("[bold]Auto-approve Settings[/bold]")
    console.print("Choose which actions Claude can perform without asking.\n")

    auto_approve_choices = questionary.checkbox(
        "Select auto-approve options:",
        choices=[
            questionary.Choice(
                "Read files (autoApproveRead)",
                checked=current.autoApproveRead,
                value="read",
            ),
            questionary.Choice(
                "Write files (autoApproveWrite)",
                checked=current.autoApproveWrite,
                value="write",
            ),
            questionary.Choice(
                "Run bash commands (autoApproveBash)",
                checked=current.autoApproveBash,
                value="bash",
            ),
            questionary.Choice(
                "All actions (autoApproveAll)",
                checked=current.autoApproveAll,
                value="all",
            ),
        ],
        style=custom_style,
    ).ask()

    if auto_approve_choices is None:
        console.print("[yellow]Setup cancelled.[/yellow]")
        return

    # Model selection
    console.print()
    current_model = getattr(current, "model", None)
    model = questionary.select(
        "Select default model:",
        choices=[
            questionary.Choice("Sonnet (balanced)", value="sonnet"),
            questionary.Choice("Opus (most capable)", value="opus"),
            questionary.Choice("Haiku (fastest)", value="haiku"),
        ],
        default="sonnet" if current_model is None else current_model,
        style=custom_style,
    ).ask()

    if model is None:
        console.print("[yellow]Setup cancelled.[/yellow]")
        return

    # Environment variables
    console.print()
    setup_env = questionary.confirm(
        "Configure environment variables (API URL, tokens)?",
        default=False,
        style=custom_style,
    ).ask()

    if setup_env is None:
        console.print("[yellow]Setup cancelled.[/yellow]")
        return

    env_vars: dict[str, str] = dict(getattr(current, "env", {}) or {})

    if setup_env:
        console.print()
        console.print("[dim]Leave empty to keep current value or skip.[/dim]\n")

        current_url = env_vars.get("ANTHROPIC_BASE_URL", "")
        base_url = questionary.text(
            "ANTHROPIC_BASE_URL:",
            default=current_url,
            style=custom_style,
        ).ask()

        if base_url is None:
            console.print("[yellow]Setup cancelled.[/yellow]")
            return

        if base_url:
            env_vars["ANTHROPIC_BASE_URL"] = base_url
        elif "ANTHROPIC_BASE_URL" in env_vars and not base_url:
            # User cleared the value
            pass

        current_token = env_vars.get("ANTHROPIC_AUTH_TOKEN", "")
        masked_token = current_token[:10] + "..." if len(current_token) > 10 else current_token
        auth_token = questionary.text(
            f"ANTHROPIC_AUTH_TOKEN [{masked_token}]:",
            default="",
            style=custom_style,
        ).ask()

        if auth_token is None:
            console.print("[yellow]Setup cancelled.[/yellow]")
            return

        if auth_token:
            env_vars["ANTHROPIC_AUTH_TOKEN"] = auth_token

    # Apply settings
    console.print()
    current.autoApproveRead = "read" in auto_approve_choices
    current.autoApproveWrite = "write" in auto_approve_choices
    current.autoApproveBash = "bash" in auto_approve_choices
    current.autoApproveAll = "all" in auto_approve_choices
    setattr(current, "model", model)

    if env_vars:
        setattr(current, "env", env_vars)

    # Confirm
    console.print("[bold]Summary:[/bold]")
    console.print(f"  Model: [green]{model}[/green]")
    console.print(f"  Auto-approve read: [green]{current.autoApproveRead}[/green]")
    console.print(f"  Auto-approve write: [green]{current.autoApproveWrite}[/green]")
    console.print(f"  Auto-approve bash: [green]{current.autoApproveBash}[/green]")
    console.print(f"  Auto-approve all: [green]{current.autoApproveAll}[/green]")
    if env_vars:
        console.print(f"  Environment variables: [green]{len(env_vars)} configured[/green]")

    console.print()
    confirm = questionary.confirm(
        "Save these settings?",
        default=True,
        style=custom_style,
    ).ask()

    if confirm:
        manager.write_claude_code_settings(current)
        console.print("\n[green]Settings saved successfully![/green]")
    else:
        console.print("\n[yellow]Settings not saved.[/yellow]")
