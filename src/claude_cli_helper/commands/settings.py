"""Commands to manage settings."""

import json
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from ..settings_manager import SettingsManager

console = Console()
manager = SettingsManager()


@click.group()
def settings() -> None:
    """Manage Claude settings."""
    pass


@settings.command()
def show() -> None:
    """Show current settings paths."""
    table = Table(title="Claude Settings Paths")
    table.add_column("Type", style="cyan")
    table.add_column("Path", style="green")
    table.add_column("Exists", style="yellow")

    table.add_row(
        "Claude Desktop",
        str(manager.settings_path),
        "Y" if manager.settings_path.exists() else "N",
    )
    table.add_row(
        "MCP Config",
        str(manager.mcp_path),
        "Y" if manager.mcp_path.exists() else "N",
    )
    table.add_row(
        "Claude Code",
        str(manager.claude_code_path),
        "Y" if manager.claude_code_path.exists() else "N",
    )

    console.print(table)


@settings.command()
@click.argument("key")
@click.argument("value")
def set(key: str, value: str) -> None:
    """Set a setting value."""
    settings_obj = manager.read_claude_code_settings()

    # Parse value
    parsed_value = value.lower() == "true" if value.lower() in ("true", "false") else value

    setattr(settings_obj, key, parsed_value)
    manager.write_claude_code_settings(settings_obj)

    console.print(f"[green]Set {key} = {parsed_value}[/green]")


def _format_value(value: object) -> str:
    """Format value for display."""
    if type(value) is bool:
        return str(value).lower()
    if type(value) in (dict, list):
        return json.dumps(value, indent=2, ensure_ascii=False)
    return str(value)


@settings.command()
@click.argument("key")
def get(key: str) -> None:
    """Get a setting value."""
    settings_obj = manager.read_claude_code_settings()

    if hasattr(settings_obj, key):
        value = getattr(settings_obj, key)
        formatted = _format_value(value)
        if type(value) in (dict, list) and value:
            console.print(f"[cyan]{key}[/cyan] =")
            print(formatted)
        else:
            console.print(f"[cyan]{key}[/cyan] = [green]{formatted}[/green]")
    else:
        console.print(f"[red]Setting '{key}' does not exist[/red]")


@settings.command()
def list() -> None:
    """List all current settings."""
    settings_obj = manager.read_claude_code_settings()

    console.print("[bold]Claude Code Settings[/bold]\n")

    for key, value in settings_obj.model_dump().items():
        if value is not None and value != [] and value != {}:
            formatted = _format_value(value)
            if type(value) in (dict, list):
                console.print(f"[cyan]{key}[/cyan] =")
                print(formatted)
            else:
                console.print(f"[cyan]{key}[/cyan] = [green]{formatted}[/green]")


@settings.command()
@click.option("--fix", is_flag=True, help="Automatically fix common issues")
def validate(fix: bool) -> None:
    """Validate settings files and check for issues."""
    from pydantic import ValidationError

    console.print("[bold]Validating Claude Settings...[/bold]\n")

    issues_found = 0
    issues_fixed = 0

    # Check Claude Code settings
    console.print("[cyan]Checking Claude Code settings...[/cyan]")
    if not manager.claude_code_path.exists():
        console.print("  [yellow]![/yellow] Settings file doesn't exist")
        if fix:
            manager.claude_code_path.parent.mkdir(parents=True, exist_ok=True)
            manager.write_claude_code_settings(manager.read_claude_code_settings())
            console.print("  [green]OK[/green] Created default settings file")
            issues_fixed += 1
        else:
            issues_found += 1
    else:
        try:
            settings_obj = manager.read_claude_code_settings()
            console.print("  [green]OK[/green] Valid settings file")

            # Check for common issues
            if hasattr(settings_obj, 'env') and settings_obj.env:
                env = settings_obj.env
                if 'ANTHROPIC_BASE_URL' in env and not env['ANTHROPIC_BASE_URL']:
                    console.print("  [yellow]![/yellow] ANTHROPIC_BASE_URL is empty")
                    if fix:
                        del env['ANTHROPIC_BASE_URL']
                        manager.write_claude_code_settings(settings_obj)
                        console.print("  [green]OK[/green] Removed empty ANTHROPIC_BASE_URL")
                        issues_fixed += 1
                    else:
                        issues_found += 1

        except ValidationError as e:
            console.print(f"  [red]X[/red] Validation error: {e}")
            issues_found += 1
        except json.JSONDecodeError as e:
            console.print(f"  [red]X[/red] Invalid JSON: {e}")
            if fix:
                console.print("  [yellow]![/yellow] Cannot auto-fix JSON syntax errors")
            issues_found += 1

    # Check MCP config
    console.print("\n[cyan]Checking MCP configuration...[/cyan]")
    if not manager.mcp_path.exists():
        console.print("  [yellow]![/yellow] MCP config doesn't exist")
        if fix:
            manager.mcp_path.parent.mkdir(parents=True, exist_ok=True)
            manager.write_mcp_config(manager.read_mcp_config())
            console.print("  [green]OK[/green] Created default MCP config")
            issues_fixed += 1
        else:
            issues_found += 1
    else:
        try:
            mcp_config = manager.read_mcp_config()
            console.print("  [green]OK[/green] Valid MCP config")

            # Check for duplicate server names
            if mcp_config.mcpServers:
                server_names = list(mcp_config.mcpServers.keys())
                if len(server_names) != len(set(server_names)):
                    console.print("  [yellow]![/yellow] Duplicate server names found")
                    issues_found += 1

        except ValidationError as e:
            console.print(f"  [red]X[/red] Validation error: {e}")
            issues_found += 1
        except json.JSONDecodeError as e:
            console.print(f"  [red]X[/red] Invalid JSON: {e}")
            if fix:
                console.print("  [yellow]![/yellow] Cannot auto-fix JSON syntax errors")
            issues_found += 1

    # Summary
    console.print("\n[bold]Summary:[/bold]")
    if issues_found == 0 and issues_fixed == 0:
        console.print("[green]OK All settings are valid![/green]")
    else:
        if issues_fixed > 0:
            console.print(f"[green]OK Fixed {issues_fixed} issue(s)[/green]")
        if issues_found > 0:
            console.print(f"[yellow]! {issues_found} issue(s) found[/yellow]")
            if not fix:
                console.print("\n[dim]Run with --fix to automatically fix common issues[/dim]")


@settings.command()
@click.argument("output_file", type=click.Path())
@click.option("--format", "-f", type=click.Choice(["json", "yaml"]), default="json", help="Output format")
@click.option("--include-mcp", is_flag=True, help="Include MCP config in export")
def export(output_file: str, format: str, include_mcp: bool) -> None:
    """Export settings to a file."""
    output_path = Path(output_file)

    # Read settings
    settings_obj = manager.read_claude_code_settings()
    data = {"claude_code": settings_obj.model_dump(exclude_none=True)}

    if include_mcp:
        mcp_config = manager.read_mcp_config()
        data["mcp"] = mcp_config.model_dump(exclude_none=True)

    # Export based on format
    if format == "json":
        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    elif format == "yaml":
        try:
            import yaml
            output_path.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True), encoding="utf-8")
        except ImportError:
            console.print("[red]PyYAML not installed. Install with: pip install pyyaml[/red]")
            return

    console.print(f"[green]OK Settings exported to {output_path}[/green]")
    if include_mcp:
        console.print("[dim]  Included: Claude Code settings + MCP config[/dim]")
    else:
        console.print("[dim]  Included: Claude Code settings only[/dim]")


@settings.command("import")
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--merge", is_flag=True, help="Merge with existing settings instead of replacing")
@click.option("--dry-run", is_flag=True, help="Show what would be imported without applying")
def import_settings(input_file: str, merge: bool, dry_run: bool) -> None:
    """Import settings from a file."""
    input_path = Path(input_file)

    # Detect format
    content = input_path.read_text(encoding="utf-8")
    if input_path.suffix in [".yaml", ".yml"]:
        try:
            import yaml
            data = yaml.safe_load(content)
        except ImportError:
            console.print("[red]PyYAML not installed. Install with: pip install pyyaml[/red]")
            return
    else:
        data = json.loads(content)

    # Import Claude Code settings
    if "claude_code" in data:
        from ..models import ClaudeCodeSettings

        if merge:
            current = manager.read_claude_code_settings()
            current_dict = current.model_dump()
            # Merge imported data with current
            for key, value in data["claude_code"].items():
                if value is not None:
                    current_dict[key] = value
            new_settings = ClaudeCodeSettings(**current_dict)
        else:
            new_settings = ClaudeCodeSettings(**data["claude_code"])

        if dry_run:
            console.print("[bold]Dry run - Claude Code Settings to import:[/bold]\n")
            console.print(json.dumps(new_settings.model_dump(exclude_none=True), indent=2))
        else:
            manager.write_claude_code_settings(new_settings)
            console.print("[green]OK Claude Code settings imported[/green]")

    # Import MCP config
    if "mcp" in data:
        from ..models import MCPConfig

        if merge:
            current_mcp = manager.read_mcp_config()
            current_mcp_dict = current_mcp.model_dump()
            # Merge MCP servers
            if "mcpServers" in data["mcp"]:
                if current_mcp_dict.get("mcpServers"):
                    current_mcp_dict["mcpServers"].update(data["mcp"]["mcpServers"])
                else:
                    current_mcp_dict["mcpServers"] = data["mcp"]["mcpServers"]
            new_mcp = MCPConfig(**current_mcp_dict)
        else:
            new_mcp = MCPConfig(**data["mcp"])

        if dry_run:
            console.print("\n[bold]Dry run - MCP Config to import:[/bold]\n")
            console.print(json.dumps(new_mcp.model_dump(exclude_none=True), indent=2))
        else:
            manager.write_mcp_config(new_mcp)
            console.print("[green]OK MCP config imported[/green]")

    if dry_run:
        console.print("\n[dim]Run without --dry-run to apply changes[/dim]")
    else:
        mode = "merged" if merge else "replaced"
        console.print(f"\n[green]OK Settings {mode} successfully![/green]")


@settings.command()
@click.option("--profile", "-p", help="Compare with a profile")
@click.option("--backup", "-b", help="Compare with a backup")
@click.option("--file", "-f", type=click.Path(exists=True), help="Compare with a file")
def diff(profile: str | None, backup: str | None, file: str | None) -> None:
    """Show differences between current settings and another source."""
    from rich.syntax import Syntax

    # Get current settings
    current = manager.read_claude_code_settings()
    current_dict = current.model_dump(exclude_none=True)

    # Get comparison target
    compare_dict = None
    source_name = ""

    if profile:
        from ..templates.profiles import BUILTIN_PROFILES
        from ..settings_manager import ProfileManager

        profile_manager = ProfileManager()

        if profile in BUILTIN_PROFILES:
            profile_obj = BUILTIN_PROFILES[profile]
            source_name = f"profile '{profile}'"
        else:
            profile_obj = profile_manager.load_profile(profile)
            source_name = f"custom profile '{profile}'"

        if profile_obj and profile_obj.claude_code_settings:
            compare_dict = profile_obj.claude_code_settings.model_dump(exclude_none=True)

    elif backup:
        backup_path = manager.backup_dir / f"{backup}.json"
        if not backup_path.exists():
            console.print(f"[red]Backup '{backup}' not found[/red]")
            return
        backup_data = json.loads(backup_path.read_text(encoding="utf-8"))
        compare_dict = backup_data.get("claude_code", {})
        source_name = f"backup '{backup}'"

    elif file:
        file_path = Path(file)
        content = file_path.read_text(encoding="utf-8")
        if file_path.suffix in [".yaml", ".yml"]:
            try:
                import yaml
                data = yaml.safe_load(content)
            except ImportError:
                console.print("[red]PyYAML not installed. Install with: pip install pyyaml[/red]")
                return
        else:
            data = json.loads(content)
        compare_dict = data.get("claude_code", data)
        source_name = f"file '{file_path.name}'"

    else:
        console.print("[red]Please specify --profile, --backup, or --file[/red]")
        return

    if compare_dict is None:
        console.print("[red]Could not load comparison source[/red]")
        return

    # Compare
    console.print(f"[bold]Comparing current settings with {source_name}[/bold]\n")

    added = []
    removed = []
    changed = []

    all_keys = set(current_dict.keys()) | set(compare_dict.keys())

    for key in sorted(all_keys):
        current_val = current_dict.get(key)
        compare_val = compare_dict.get(key)

        if current_val is None and compare_val is not None:
            added.append((key, compare_val))
        elif current_val is not None and compare_val is None:
            removed.append((key, current_val))
        elif current_val != compare_val:
            changed.append((key, current_val, compare_val))

    if not added and not removed and not changed:
        console.print("[green]OK No differences found![/green]")
        return

    if added:
        console.print("[bold green]Added in comparison:[/bold green]")
        for key, val in added:
            console.print(f"  [green]+[/green] {key}: {json.dumps(val)}")
        console.print()

    if removed:
        console.print("[bold red]Removed in comparison:[/bold red]")
        for key, val in removed:
            console.print(f"  [red]-[/red] {key}: {json.dumps(val)}")
        console.print()

    if changed:
        console.print("[bold yellow]Changed:[/bold yellow]")
        for key, current_val, compare_val in changed:
            console.print(f"  [yellow]~[/yellow] {key}:")
            console.print(f"    Current:  {json.dumps(current_val)}")
            console.print(f"    Compare:  {json.dumps(compare_val)}")
        console.print()

    # Summary
    total = len(added) + len(removed) + len(changed)
    console.print(f"[dim]Total differences: {total} ({len(added)} added, {len(removed)} removed, {len(changed)} changed)[/dim]")
