"""Interactive setup wizard for Claude Code settings."""

import sys

import click
from rich.console import Console

from ..models import HookCommand, HookMatcher, HooksConfig
from ..settings_manager import SettingsManager
from .hooks import NOTIFICATION_PRESETS, _get_platform

console = Console()
manager = SettingsManager()


def _is_interactive() -> bool:
    """Check if running in interactive terminal."""
    return sys.stdin.isatty() and sys.stdout.isatty()


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


def _setup_interactive() -> None:
    """Run interactive setup using questionary."""
    import questionary
    from questionary import Style

    custom_style = Style([
        ("qmark", "fg:cyan bold"),
        ("question", "bold"),
        ("answer", "fg:green"),
        ("pointer", "fg:cyan bold"),
        ("highlighted", "fg:cyan bold"),
        ("selected", "fg:green"),
    ])

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

    # Notification hooks
    console.print()
    has_hooks = current.hooks and current.hooks.PostToolUse
    setup_hooks = questionary.confirm(
        "Configure notification when tasks complete?",
        default=not has_hooks,
        style=custom_style,
    ).ask()

    if setup_hooks is None:
        console.print("[yellow]Setup cancelled.[/yellow]")
        return

    notification_command: str | None = None
    if setup_hooks:
        plat = _get_platform()
        presets = NOTIFICATION_PRESETS.get(plat, {})

        notification_choice = questionary.select(
            "Select notification type:",
            choices=[
                questionary.Choice("Beep sound", value="beep"),
                questionary.Choice("Toast/Popup notification", value="toast"),
                questionary.Choice("System sound", value="sound"),
                questionary.Choice("No notification", value="none"),
            ],
            style=custom_style,
        ).ask()

        if notification_choice is None:
            console.print("[yellow]Setup cancelled.[/yellow]")
            return

        if notification_choice != "none":
            notification_command = presets.get(notification_choice)

    # Apply settings
    console.print()
    current.autoApproveRead = "read" in auto_approve_choices
    current.autoApproveWrite = "write" in auto_approve_choices
    current.autoApproveBash = "bash" in auto_approve_choices
    current.autoApproveAll = "all" in auto_approve_choices
    setattr(current, "model", model)

    if env_vars:
        setattr(current, "env", env_vars)

    # Apply notification hooks
    if notification_command:
        if not current.hooks:
            current.hooks = HooksConfig()
        # Clear existing Task hooks and add new one
        current.hooks.PostToolUse = [
            h for h in current.hooks.PostToolUse if h.matcher != "Task"
        ]
        hook_cmd = HookCommand(type="command", command=notification_command)
        hook_matcher = HookMatcher(matcher="Task", hooks=[hook_cmd])
        current.hooks.PostToolUse.append(hook_matcher)

    # Confirm
    console.print("[bold]Summary:[/bold]")
    console.print(f"  Model: [green]{model}[/green]")
    console.print(f"  Auto-approve read: [green]{current.autoApproveRead}[/green]")
    console.print(f"  Auto-approve write: [green]{current.autoApproveWrite}[/green]")
    console.print(f"  Auto-approve bash: [green]{current.autoApproveBash}[/green]")
    console.print(f"  Auto-approve all: [green]{current.autoApproveAll}[/green]")
    if env_vars:
        console.print(f"  Environment variables: [green]{len(env_vars)} configured[/green]")
    if notification_command:
        console.print("  Notification: [green]enabled[/green]")

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


def _setup_fallback() -> None:
    """Run fallback setup using click prompts."""
    current = manager.read_claude_code_settings()

    # Auto-approve settings
    console.print("[bold]Auto-approve Settings[/bold]")
    console.print("Choose which actions Claude can perform without asking.\n")

    auto_read = click.confirm(
        "  Auto-approve read files?",
        default=current.autoApproveRead,
    )
    auto_write = click.confirm(
        "  Auto-approve write files?",
        default=current.autoApproveWrite,
    )
    auto_bash = click.confirm(
        "  Auto-approve bash commands?",
        default=current.autoApproveBash,
    )
    auto_all = click.confirm(
        "  Auto-approve ALL actions?",
        default=current.autoApproveAll,
    )

    # Model selection
    console.print()
    current_model = getattr(current, "model", None) or "sonnet"
    console.print("[bold]Model Selection[/bold]")
    console.print("  1. sonnet (balanced)")
    console.print("  2. opus (most capable)")
    console.print("  3. haiku (fastest)")
    model_map = {"1": "sonnet", "2": "opus", "3": "haiku", "sonnet": "sonnet", "opus": "opus", "haiku": "haiku"}
    model_input = click.prompt(
        "  Select model (1/2/3 or name)",
        default=current_model,
    )
    model = model_map.get(model_input, current_model)

    # Environment variables
    console.print()
    setup_env = click.confirm(
        "Configure environment variables (API URL, tokens)?",
        default=False,
    )

    env_vars: dict[str, str] = dict(getattr(current, "env", {}) or {})

    if setup_env:
        console.print()
        console.print("[dim]Leave empty to keep current value or skip.[/dim]\n")

        current_url = env_vars.get("ANTHROPIC_BASE_URL", "")
        base_url = click.prompt(
            "  ANTHROPIC_BASE_URL",
            default=current_url,
            show_default=bool(current_url),
        )
        if base_url:
            env_vars["ANTHROPIC_BASE_URL"] = base_url

        current_token = env_vars.get("ANTHROPIC_AUTH_TOKEN", "")
        masked_token = current_token[:10] + "..." if len(current_token) > 10 else ""
        auth_token = click.prompt(
            f"  ANTHROPIC_AUTH_TOKEN [{masked_token}]",
            default="",
            show_default=False,
        )
        if auth_token:
            env_vars["ANTHROPIC_AUTH_TOKEN"] = auth_token

    # Notification hooks
    console.print()
    has_hooks = current.hooks and current.hooks.PostToolUse
    setup_hooks = click.confirm(
        "Configure notification when tasks complete?",
        default=not has_hooks,
    )

    notification_command: str | None = None
    if setup_hooks:
        plat = _get_platform()
        presets = NOTIFICATION_PRESETS.get(plat, {})

        console.print("\n[bold]Notification Type[/bold]")
        console.print("  1. Beep sound")
        console.print("  2. Toast/Popup notification")
        console.print("  3. System sound")
        console.print("  4. No notification")

        notif_choice = click.prompt(
            "  Select notification type (1-4)",
            type=click.IntRange(1, 4),
            default=1,
        )

        notif_map = {1: "beep", 2: "toast", 3: "sound"}
        if notif_choice in notif_map:
            notification_command = presets.get(notif_map[notif_choice])

    # Apply settings
    current.autoApproveRead = auto_read
    current.autoApproveWrite = auto_write
    current.autoApproveBash = auto_bash
    current.autoApproveAll = auto_all
    setattr(current, "model", model)

    if env_vars:
        setattr(current, "env", env_vars)

    # Apply notification hooks
    if notification_command:
        if not current.hooks:
            current.hooks = HooksConfig()
        # Clear existing Task hooks and add new one
        current.hooks.PostToolUse = [
            h for h in current.hooks.PostToolUse if h.matcher != "Task"
        ]
        hook_cmd = HookCommand(type="command", command=notification_command)
        hook_matcher = HookMatcher(matcher="Task", hooks=[hook_cmd])
        current.hooks.PostToolUse.append(hook_matcher)

    # Confirm
    console.print()
    console.print("[bold]Summary:[/bold]")
    console.print(f"  Model: [green]{model}[/green]")
    console.print(f"  Auto-approve read: [green]{auto_read}[/green]")
    console.print(f"  Auto-approve write: [green]{auto_write}[/green]")
    console.print(f"  Auto-approve bash: [green]{auto_bash}[/green]")
    console.print(f"  Auto-approve all: [green]{auto_all}[/green]")
    if env_vars:
        console.print(f"  Environment variables: [green]{len(env_vars)} configured[/green]")
    if notification_command:
        console.print("  Notification: [green]enabled[/green]")

    console.print()
    if click.confirm("Save these settings?", default=True):
        manager.write_claude_code_settings(current)
        console.print("\n[green]Settings saved successfully![/green]")
    else:
        console.print("\n[yellow]Settings not saved.[/yellow]")


@click.command()
def setup() -> None:
    """Interactive setup wizard for Claude Code settings."""
    console.print("\n[bold cyan]Claude Code Setup Wizard[/bold cyan]\n")

    # Show current settings
    _show_current_settings()

    # Try interactive mode, fallback to click prompts
    if _is_interactive():
        try:
            _setup_interactive()
        except Exception:
            console.print("[dim]Falling back to simple prompts...[/dim]\n")
            _setup_fallback()
    else:
        _setup_fallback()
