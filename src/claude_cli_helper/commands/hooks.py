"""Commands to manage Claude Code hooks/notifications."""

import platform
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from ..models import HookMatcher, HooksConfig
from ..settings_manager import SettingsManager

console = Console()
manager = SettingsManager()

# Windows Media sounds directory
WINDOWS_MEDIA_DIR = Path("C:/Windows/Media")

# Predefined notification commands for different platforms
# Windows commands use -NoProfile -ExecutionPolicy Bypass to avoid profile loading and script policy errors
NOTIFICATION_PRESETS = {
    "windows": {
        "beep": 'powershell -NoProfile -ExecutionPolicy Bypass -Command "[console]::beep(1000,500)"',
        "toast": (
            'powershell -NoProfile -ExecutionPolicy Bypass -Command "'
            "Add-Type -AssemblyName System.Windows.Forms; "
            "[System.Windows.Forms.MessageBox]::Show('Claude Code task completed!', 'Notification')"
            '"'
        ),
        "sound": (
            'powershell -NoProfile -ExecutionPolicy Bypass -Command "'
            "(New-Object Media.SoundPlayer 'C:\\Windows\\Media\\notify.wav').PlaySync()"
            '"'
        ),
    },
    "darwin": {  # macOS
        "beep": "afplay /System/Library/Sounds/Glass.aiff",
        "toast": 'osascript -e \'display notification "Claude Code task completed!" with title "Notification"\'',
        "sound": "afplay /System/Library/Sounds/Ping.aiff",
    },
    "linux": {
        "beep": "paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null || echo -e '\\a'",
        "toast": 'notify-send "Claude Code" "Task completed!"',
        "sound": "paplay /usr/share/sounds/freedesktop/stereo/message.oga 2>/dev/null || echo -e '\\a'",
    },
}

# Common tools that can be matched
COMMON_TOOLS = ["Task", "Bash", "Read", "Write", "Edit", "Grep", "Glob", "WebFetch", "WebSearch"]


def _get_platform() -> str:
    """Get current platform identifier."""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "darwin"
    return "linux"


def _get_preset_command(preset_name: str) -> str | None:
    """Get preset command for current platform."""
    plat = _get_platform()
    presets = NOTIFICATION_PRESETS.get(plat, {})
    return presets.get(preset_name)


def _get_windows_sounds() -> list[str]:
    """Get list of available Windows sound files."""
    if not WINDOWS_MEDIA_DIR.exists():
        return []
    return sorted([f.name for f in WINDOWS_MEDIA_DIR.glob("*.wav")])


def _build_sound_command(sound_file: str, volume: int = 100) -> str:
    """Build PowerShell command to play a sound file with volume control.

    Args:
        sound_file: Name of the sound file in Windows Media directory
        volume: Volume level from 0 to 100 (default: 100)
    """
    import base64

    sound_path = WINDOWS_MEDIA_DIR / sound_file
    vol = volume / 100  # Convert to 0.0-1.0 scale

    # PowerShell script using MediaPlayer for volume control
    # Volume must be set before Play() and after media is loaded
    ps_script = f"""
Add-Type -AssemblyName PresentationCore
$p = New-Object System.Windows.Media.MediaPlayer
$p.Volume = {vol}
$p.Open([uri]"{sound_path}")
while (-not $p.HasAudio) {{ Start-Sleep -Milliseconds 50 }}
$p.Play()
Start-Sleep -Milliseconds 2000
"""
    # Encode script as base64 to avoid escaping issues
    encoded = base64.b64encode(ps_script.encode("utf-16-le")).decode("ascii")
    return f"powershell -NoProfile -ExecutionPolicy Bypass -EncodedCommand {encoded}"


def _select_windows_sound_interactive(custom_style: object) -> str | None:
    """Interactive Windows sound selection with volume control."""
    import subprocess

    import questionary

    sound_files = _get_windows_sounds()
    if not sound_files:
        console.print("[red]No sound files found.[/red]")
        return None

    choices = [questionary.Choice(sound, value=sound) for sound in sound_files]

    selected = questionary.select(
        "Select a sound file:",
        choices=choices,
        style=custom_style,
    ).ask()

    if not selected:
        return None

    # Ask for volume
    volume_choices = [
        questionary.Choice("100% (Full)", value=100),
        questionary.Choice("75%", value=75),
        questionary.Choice("50%", value=50),
        questionary.Choice("25%", value=25),
        questionary.Choice("10% (Quiet)", value=10),
    ]

    volume = questionary.select(
        "Select volume level:",
        choices=volume_choices,
        style=custom_style,
    ).ask()

    if volume is None:
        return None

    # Preview the sound
    command = _build_sound_command(selected, volume)
    console.print(f"[dim]Playing: {selected} at {volume}% volume[/dim]")
    subprocess.run(command, shell=True, check=True)

    return command


@click.group()
def hooks() -> None:
    """Manage Claude Code hooks and notifications.

    Hooks allow you to run custom commands when Claude Code completes tasks.
    Use this to get notifications (sound, popup, toast) when long-running
    operations finish.
    """
    pass


@hooks.command()
def list() -> None:
    """List all configured hooks."""
    settings = manager.read_claude_code_settings()

    if not settings.hooks:
        console.print("[dim]No hooks configured.[/dim]")
        console.print("\nUse [cyan]claude-helper hooks add[/cyan] to add a notification hook.")
        return

    # postToolUse hooks
    if settings.hooks.postToolUse:
        table = Table(title="Post-Tool Hooks (run after tool completes)")
        table.add_column("#", style="dim", width=3)
        table.add_column("Matcher", style="cyan")
        table.add_column("Command", style="green")

        for i, hook in enumerate(settings.hooks.postToolUse):
            table.add_row(str(i), hook.matcher, hook.command)

        console.print(table)
    else:
        console.print("[dim]No post-tool hooks configured.[/dim]")

    console.print()

    # preToolUse hooks
    if settings.hooks.preToolUse:
        table = Table(title="Pre-Tool Hooks (run before tool executes)")
        table.add_column("#", style="dim", width=3)
        table.add_column("Matcher", style="cyan")
        table.add_column("Command", style="green")

        for i, hook in enumerate(settings.hooks.preToolUse):
            table.add_row(str(i), hook.matcher, hook.command)

        console.print(table)


@hooks.command()
@click.option(
    "--matcher", "-m",
    default="Task",
    help="Tool name to match (e.g., Task, Bash). Default: Task",
)
@click.option(
    "--command", "-c",
    help="Custom command to run. If not provided, will prompt for preset.",
)
@click.option(
    "--type", "-t", "hook_type",
    type=click.Choice(["post", "pre"]),
    default="post",
    help="Hook type: post (after tool) or pre (before tool). Default: post",
)
def add(matcher: str, command: str | None, hook_type: str) -> None:
    """Add a notification hook.

    Examples:

    \b
    # Add notification when Task completes (interactive)
    claude-helper hooks add

    \b
    # Add beep when any Bash command finishes
    claude-helper hooks add -m Bash -c "echo -e '\\a'"

    \b
    # Add toast notification for Task completion
    claude-helper hooks add -m Task --command "notify-send 'Done!'"
    """
    settings = manager.read_claude_code_settings()

    # Initialize hooks if not exists
    if not settings.hooks:
        settings.hooks = HooksConfig()

    # If no command provided, show presets
    if not command:
        command = _select_preset_interactive()
        if not command:
            console.print("[yellow]Cancelled.[/yellow]")
            return

    # Create hook matcher
    hook = HookMatcher(matcher=matcher, command=command)

    # Add to appropriate list
    if hook_type == "post":
        settings.hooks.postToolUse.append(hook)
    else:
        settings.hooks.preToolUse.append(hook)

    manager.write_claude_code_settings(settings)

    console.print(f"[green]Added {hook_type}-tool hook:[/green]")
    console.print(f"  Matcher: [cyan]{matcher}[/cyan]")
    console.print(f"  Command: [dim]{command}[/dim]")


def _is_interactive() -> bool:
    """Check if running in interactive terminal."""
    return sys.stdin.isatty() and sys.stdout.isatty()


def _select_preset_interactive() -> str | None:
    """Interactive preset selection."""
    plat = _get_platform()
    presets = NOTIFICATION_PRESETS.get(plat, {})

    if not _is_interactive():
        # Fallback to click prompts
        return _select_preset_fallback(presets)

    try:
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

        choices = [
            questionary.Choice("Beep sound", value="beep"),
            questionary.Choice("Toast/Popup notification", value="toast"),
            questionary.Choice("System sound (default)", value="sound"),
        ]

        # Add Windows sound browser option
        if _get_platform() == "windows":
            choices.append(questionary.Choice("Browse Windows sounds...", value="browse_sounds"))

        choices.append(questionary.Choice("Custom command...", value="custom"))

        result = questionary.select(
            "Select notification type:",
            choices=choices,
            style=custom_style,
        ).ask()

        if result is None:
            return None

        if result == "custom":
            custom_cmd: str | None = questionary.text(
                "Enter custom command:",
                style=custom_style,
            ).ask()
            return custom_cmd

        if result == "browse_sounds":
            return _select_windows_sound_interactive(custom_style)

        return presets.get(result) if result else None

    except Exception:
        return _select_preset_fallback(presets)


def _select_preset_fallback(presets: dict[str, str]) -> str | None:
    """Fallback preset selection using click."""
    console.print("\n[bold]Select notification type:[/bold]")
    console.print("  1. Beep sound")
    console.print("  2. Toast/Popup notification")
    console.print("  3. System sound")
    console.print("  4. Custom command")

    choice = click.prompt("Choice", type=click.IntRange(1, 4), default=1)

    if choice == 4:
        custom: str = click.prompt("Enter custom command")
        return custom

    preset_map = {1: "beep", 2: "toast", 3: "sound"}
    preset_name = preset_map.get(choice)
    return presets.get(preset_name) if preset_name else None


@hooks.command()
@click.argument("index", type=int)
@click.option(
    "--type", "-t", "hook_type",
    type=click.Choice(["post", "pre"]),
    default="post",
    help="Hook type to remove from. Default: post",
)
def remove(index: int, hook_type: str) -> None:
    """Remove a hook by its index.

    Use 'hooks list' to see hook indices.

    Example:
        claude-helper hooks remove 0
    """
    settings = manager.read_claude_code_settings()

    if not settings.hooks:
        console.print("[red]No hooks configured.[/red]")
        return

    hook_list = settings.hooks.postToolUse if hook_type == "post" else settings.hooks.preToolUse

    if index < 0 or index >= len(hook_list):
        console.print(f"[red]Invalid index. Valid range: 0-{len(hook_list) - 1}[/red]")
        return

    removed = hook_list.pop(index)
    manager.write_claude_code_settings(settings)

    console.print("[green]Removed hook:[/green]")
    console.print(f"  Matcher: [cyan]{removed.matcher}[/cyan]")
    console.print(f"  Command: [dim]{removed.command}[/dim]")


@hooks.command()
def clear() -> None:
    """Remove all hooks."""
    settings = manager.read_claude_code_settings()

    if not settings.hooks or (not settings.hooks.postToolUse and not settings.hooks.preToolUse):
        console.print("[dim]No hooks to clear.[/dim]")
        return

    if not click.confirm("Remove all hooks?", default=False):
        console.print("[yellow]Cancelled.[/yellow]")
        return

    settings.hooks = HooksConfig()
    manager.write_claude_code_settings(settings)

    console.print("[green]All hooks cleared.[/green]")


@hooks.command()
def presets() -> None:
    """Show available notification presets for your platform."""
    plat = _get_platform()
    presets_dict = NOTIFICATION_PRESETS.get(plat, {})

    platform_name = {"windows": "Windows", "darwin": "macOS", "linux": "Linux"}.get(plat, plat)

    console.print(f"[bold]Available presets for {platform_name}:[/bold]\n")

    table = Table()
    table.add_column("Preset", style="cyan")
    table.add_column("Command", style="dim")

    for name, cmd in presets_dict.items():
        table.add_row(name, cmd)

    console.print(table)

    console.print("\n[dim]Use 'claude-helper hooks add' to add a preset interactively.[/dim]")


@hooks.command()
def sounds() -> None:
    """List and select Windows system sounds (Windows only).

    Browse available sounds in C:\\Windows\\Media and add one as a hook.
    """
    if _get_platform() != "windows":
        console.print("[yellow]This command is only available on Windows.[/yellow]")
        return

    sound_files = _get_windows_sounds()
    if not sound_files:
        console.print("[red]No sound files found in C:\\Windows\\Media[/red]")
        return

    if not _is_interactive():
        # Non-interactive: just list sounds
        console.print("[bold]Available Windows sounds:[/bold]\n")
        for i, sound in enumerate(sound_files, 1):
            console.print(f"  {i:2}. {sound}")
        console.print("\n[dim]Use 'claude-helper hooks add -c \"<command>\"' to add manually.[/dim]")
        return

    try:
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

        # Let user select a sound
        choices = [questionary.Choice(sound, value=sound) for sound in sound_files]

        selected = questionary.select(
            "Select a sound file:",
            choices=choices,
            style=custom_style,
        ).ask()

        if not selected:
            console.print("[yellow]Cancelled.[/yellow]")
            return

        # Ask for volume
        volume_choices = [
            questionary.Choice("100% (Full)", value=100),
            questionary.Choice("75%", value=75),
            questionary.Choice("50%", value=50),
            questionary.Choice("25%", value=25),
            questionary.Choice("10% (Quiet)", value=10),
        ]

        volume = questionary.select(
            "Select volume level:",
            choices=volume_choices,
            style=custom_style,
        ).ask()

        if volume is None:
            console.print("[yellow]Cancelled.[/yellow]")
            return

        # Test the sound
        import subprocess

        command = _build_sound_command(selected, volume)
        console.print(f"\n[dim]Testing: {selected} at {volume}% volume[/dim]")
        subprocess.run(command, shell=True, check=True)

        # Ask to add as hook
        add_hook = questionary.confirm(
            "Add this sound as notification hook?",
            default=True,
            style=custom_style,
        ).ask()

        if add_hook:
            settings = manager.read_claude_code_settings()
            if not settings.hooks:
                settings.hooks = HooksConfig()

            hook = HookMatcher(matcher="Task", command=command)
            settings.hooks.postToolUse.append(hook)
            manager.write_claude_code_settings(settings)

            console.print(f"[green]Added hook with sound: {selected} at {volume}% volume[/green]")
        else:
            console.print("[yellow]Sound not added.[/yellow]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        # Fallback to simple list
        console.print("\n[bold]Available Windows sounds:[/bold]\n")
        for i, sound in enumerate(sound_files, 1):
            console.print(f"  {i:2}. {sound}")


@hooks.command()
@click.option(
    "--preset", "-p",
    type=click.Choice(["beep", "toast", "sound"]),
    help="Test a specific preset",
)
def test(preset: str | None) -> None:
    """Test notification command.

    Run this to verify your notification works before adding it as a hook.
    """
    import subprocess

    if preset:
        command = _get_preset_command(preset)
        if not command:
            console.print(f"[red]Preset '{preset}' not available for your platform.[/red]")
            return
    else:
        # Test first configured hook or default beep
        settings = manager.read_claude_code_settings()
        if settings.hooks and settings.hooks.postToolUse:
            command = settings.hooks.postToolUse[0].command
            console.print("[dim]Testing first configured hook...[/dim]")
        else:
            command = _get_preset_command("beep")
            console.print("[dim]Testing default beep...[/dim]")

    if not command:
        console.print("[red]No command to test.[/red]")
        return

    console.print(f"[dim]Running: {command}[/dim]")

    try:
        if platform.system().lower() == "windows":
            subprocess.run(command, shell=True, check=True)
        else:
            subprocess.run(command, shell=True, check=True)
        console.print("[green]Notification executed successfully![/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Command failed with exit code {e.returncode}[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
