"""Commands to manage CLAUDE.md configuration file."""

import os
import platform
import subprocess
from pathlib import Path

import click
from rich.console import Console
from rich.markdown import Markdown

console = Console()

CLAUDE_MD_FILENAME = "CLAUDE.md"

DEFAULT_TEMPLATE = """# CLAUDE.md

Project instructions for Claude Code.

## Rules

"""


def get_claude_md_path() -> Path:
    """Get CLAUDE.md path in current working directory."""
    return Path.cwd() / CLAUDE_MD_FILENAME


def get_default_editor() -> str:
    """Get default editor based on environment and platform."""
    # Check environment variables first
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL")
    if editor:
        return editor

    # Platform-specific defaults
    system = platform.system()
    if system == "Windows":
        return "notepad"
    elif system == "Darwin":
        return "nano"
    else:
        return "nano"


@click.group()
def config() -> None:
    """Manage CLAUDE.md configuration file."""
    pass


@config.command()
def show() -> None:
    """Show contents of CLAUDE.md in current directory."""
    path = get_claude_md_path()

    if not path.exists():
        console.print(f"[yellow]No {CLAUDE_MD_FILENAME} found in current directory.[/yellow]")
        console.print("\nRun [cyan]claude-helper config edit[/cyan] to create one.")
        return

    content = path.read_text(encoding="utf-8")
    md = Markdown(content)
    console.print(md)


@config.command()
def edit() -> None:
    """Open CLAUDE.md in editor."""
    path = get_claude_md_path()

    # Create file with template if it doesn't exist
    if not path.exists():
        path.write_text(DEFAULT_TEMPLATE, encoding="utf-8")
        console.print(f"[green]Created {CLAUDE_MD_FILENAME} with default template.[/green]")

    editor = get_default_editor()

    console.print(f"[dim]Opening with {editor}...[/dim]")

    try:
        subprocess.run([editor, str(path)], check=True)
    except FileNotFoundError:
        console.print(f"[red]Editor '{editor}' not found.[/red]")
        console.print(f"Set $EDITOR environment variable or edit manually: {path}")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Editor exited with error: {e}[/red]")


@config.command("add-rule")
@click.argument("rule")
def add_rule(rule: str) -> None:
    """Add a new rule to CLAUDE.md."""
    path = get_claude_md_path()

    if not path.exists():
        # Create new file with template and the rule
        content = DEFAULT_TEMPLATE + f"- {rule}\n"
        path.write_text(content, encoding="utf-8")
        console.print(f"[green]Created {CLAUDE_MD_FILENAME} with rule.[/green]")
        console.print(f"[cyan]+ {rule}[/cyan]")
        return

    content = path.read_text(encoding="utf-8")

    # Find ## Rules section and append rule
    lines = content.split("\n")
    rules_index = -1

    for i, line in enumerate(lines):
        if line.strip().lower() in ("## rules", "## rule"):
            rules_index = i
            break

    if rules_index >= 0:
        # Find the end of the rules section (next ## or end of file)
        insert_index = rules_index + 1

        # Skip empty lines after ## Rules
        while insert_index < len(lines) and lines[insert_index].strip() == "":
            insert_index += 1

        # Find where to insert (after existing rules, before next section)
        while insert_index < len(lines):
            line = lines[insert_index]
            if line.startswith("## "):
                break
            if line.strip() == "" and insert_index + 1 < len(lines) and lines[insert_index + 1].startswith("## "):
                break
            insert_index += 1

        # Insert the new rule
        lines.insert(insert_index, f"- {rule}")
    else:
        # No Rules section found, add one at the end
        if not content.endswith("\n"):
            content += "\n"
        content += f"\n## Rules\n\n- {rule}\n"
        path.write_text(content, encoding="utf-8")
        console.print("[green]Added Rules section with new rule.[/green]")
        console.print(f"[cyan]+ {rule}[/cyan]")
        return

    new_content = "\n".join(lines)
    path.write_text(new_content, encoding="utf-8")
    console.print(f"[green]Rule added to {CLAUDE_MD_FILENAME}.[/green]")
    console.print(f"[cyan]+ {rule}[/cyan]")
