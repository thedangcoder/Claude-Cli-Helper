"""Doctor command to diagnose Claude CLI Helper issues."""

import json
import platform
import shutil
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..config import (
    get_backup_dir,
    get_claude_code_settings_path,
    get_claude_desktop_config_dir,
    get_mcp_settings_path,
)
from ..settings_manager import SettingsManager

console = Console()
manager = SettingsManager()


def _check_mark(ok: bool) -> str:
    """Return checkmark or X based on status."""
    return "[green]OK[/green]" if ok else "[red]FAIL[/red]"


def _warn_mark() -> str:
    """Return warning mark."""
    return "[yellow]WARN[/yellow]"


def _check_file_exists(path: Path) -> tuple[bool, str]:
    """Check if file exists and return status."""
    if path.exists():
        return True, f"{_check_mark(True)} File exists"
    return False, f"{_check_mark(False)} File not found"


def _check_json_valid(path: Path) -> tuple[bool, str]:
    """Check if JSON file is valid."""
    if not path.exists():
        return False, f"{_check_mark(False)} File not found"
    try:
        with open(path, encoding="utf-8-sig") as f:
            json.load(f)
        return True, f"{_check_mark(True)} Valid JSON"
    except json.JSONDecodeError as e:
        return False, f"{_check_mark(False)} Invalid JSON: {e.msg}"
    except Exception as e:
        return False, f"{_check_mark(False)} Error reading: {e}"


def _check_directory_writable(path: Path) -> tuple[bool, str]:
    """Check if directory is writable."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        test_file = path / ".write_test"
        test_file.write_text("test")
        test_file.unlink()
        return True, f"{_check_mark(True)} Writable"
    except Exception as e:
        return False, f"{_check_mark(False)} Not writable: {e}"


def _check_mcp_servers() -> list[tuple[str, bool, str]]:
    """Check MCP server configurations."""
    results = []

    try:
        settings = manager.read_claude_code_settings()
        mcp_servers = settings.mcpServers

        if not mcp_servers:
            return [("MCP Servers", True, f"{_warn_mark()} No MCP servers configured")]

        for name, server in mcp_servers.items():
            cmd = server.command
            # Check if command exists
            cmd_path = shutil.which(cmd)
            if cmd_path:
                results.append((f"MCP: {name}", True, f"{_check_mark(True)} Command '{cmd}' found"))
            else:
                results.append((f"MCP: {name}", False, f"{_check_mark(False)} Command '{cmd}' not found"))
    except Exception as e:
        results.append(("MCP Servers", False, f"{_check_mark(False)} Error reading: {e}"))

    return results


def _check_hooks() -> list[tuple[str, bool, str]]:
    """Check hooks configuration."""
    results = []

    try:
        settings = manager.read_claude_code_settings()
        hooks = settings.hooks

        if not hooks or not hooks.Stop:
            return [("Hooks", True, f"{_warn_mark()} No hooks configured")]

        for i, stop_hook in enumerate(hooks.Stop):
            for hook_cmd in stop_hook.hooks:
                cmd = hook_cmd.command
                # Just check if command is non-empty
                if cmd:
                    results.append((f"Hook #{i}", True, f"{_check_mark(True)} Command configured"))
                else:
                    results.append((f"Hook #{i}", False, f"{_check_mark(False)} Empty command"))
    except Exception as e:
        results.append(("Hooks", False, f"{_check_mark(False)} Error reading: {e}"))

    return results


def _check_claude_cli() -> tuple[bool, str]:
    """Check if Claude CLI is installed."""
    claude_path = shutil.which("claude")
    if claude_path:
        return True, f"{_check_mark(True)} Claude CLI found at {claude_path}"
    return False, f"{_warn_mark()} Claude CLI not found in PATH"


def _get_system_info() -> dict[str, str]:
    """Get system information."""
    return {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "Python": platform.python_version(),
        "Architecture": platform.machine(),
    }


@click.command()
@click.option("--fix", is_flag=True, help="Attempt to fix issues automatically")
@click.option("--verbose", "-v", is_flag=True, help="Show more details")
def doctor(fix: bool, verbose: bool) -> None:
    """Diagnose and fix Claude CLI Helper issues.

    This command checks:
    - Settings file paths and validity
    - JSON syntax in configuration files
    - MCP server availability
    - Hooks configuration
    - Backup directory status

    Examples:

    \b
    # Basic health check
    claude-helper doctor

    \b
    # Show detailed information
    claude-helper doctor --verbose

    \b
    # Attempt to fix issues
    claude-helper doctor --fix
    """
    console.print(Panel.fit(
        "[bold cyan]Claude CLI Helper Doctor[/bold cyan]\n"
        "Checking your Claude configuration...",
        border_style="cyan",
    ))
    console.print()

    issues_found = 0
    issues_fixed = 0

    # System info (verbose only)
    if verbose:
        console.print("[bold]System Information[/bold]")
        sys_info = _get_system_info()
        for key, value in sys_info.items():
            console.print(f"  {key}: [dim]{value}[/dim]")
        console.print()

    # Check Claude CLI
    console.print("[bold]Claude CLI[/bold]")
    cli_ok, cli_msg = _check_claude_cli()
    console.print(f"  {cli_msg}")
    if not cli_ok:
        issues_found += 1
    console.print()

    # Check settings files
    console.print("[bold]Configuration Files[/bold]")

    files_to_check = [
        ("Claude Code Settings", get_claude_code_settings_path()),
        ("MCP Config", get_mcp_settings_path()),
        ("Claude Desktop Dir", get_claude_desktop_config_dir()),
    ]

    table = Table(show_header=True, header_style="bold")
    table.add_column("File")
    table.add_column("Path")
    table.add_column("Status")

    for name, path in files_to_check:
        if path.is_dir() or name.endswith("Dir"):
            exists = path.exists()
            status = f"{_check_mark(exists)} {'Exists' if exists else 'Not found'}"
            if not exists and fix:
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    status = f"{_check_mark(True)} Created"
                    issues_fixed += 1
                except Exception:
                    pass
            if not exists:
                issues_found += 1
        else:
            # Check file exists and JSON valid
            exists, _ = _check_file_exists(path)
            if exists:
                valid, status = _check_json_valid(path)
                if not valid:
                    issues_found += 1
            else:
                status = f"{_warn_mark()} Not created yet"

        path_str = str(path)
        if len(path_str) > 50 and not verbose:
            path_str = "..." + path_str[-47:]
        table.add_row(name, path_str, status)

    console.print(table)
    console.print()

    # Check backup directory
    console.print("[bold]Backup Directory[/bold]")
    backup_dir = get_backup_dir()
    writable, writable_msg = _check_directory_writable(backup_dir)
    console.print(f"  Path: [dim]{backup_dir}[/dim]")
    console.print(f"  {writable_msg}")

    # Count backups
    if backup_dir.exists():
        backups = manager.list_backups()
        console.print(f"  {_check_mark(True)} {len(backups)} backup(s) available")
    console.print()

    # Check MCP servers
    console.print("[bold]MCP Servers[/bold]")
    mcp_results = _check_mcp_servers()
    for _name, ok, msg in mcp_results:
        console.print(f"  {msg}")
        if not ok:
            issues_found += 1
    console.print()

    # Check hooks
    console.print("[bold]Hooks[/bold]")
    hook_results = _check_hooks()
    for _name, ok, msg in hook_results:
        console.print(f"  {msg}")
        if not ok:
            issues_found += 1
    console.print()

    # Summary
    console.print("[bold]Summary[/bold]")
    if issues_found == 0:
        console.print(Panel.fit(
            f"{_check_mark(True)} All checks passed! Your configuration looks healthy.",
            border_style="green",
        ))
    else:
        status_msg = f"{_check_mark(False)} Found {issues_found} issue(s)"
        if issues_fixed > 0:
            status_msg += f", fixed {issues_fixed}"
        console.print(Panel.fit(
            status_msg + "\n\n"
            "Run [cyan]claude-helper doctor --fix[/cyan] to attempt automatic fixes.\n"
            "Run [cyan]claude-helper doctor --verbose[/cyan] for more details.",
            border_style="yellow",
        ))
