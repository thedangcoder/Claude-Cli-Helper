"""Tests for MCP templates."""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from claude_cli_helper.commands.mcp import browse, install, search
from claude_cli_helper.models import MCPConfig, MCPServer
from claude_cli_helper.templates.mcp_templates import (
    MCP_TEMPLATES,
    TEMPLATE_INFO,
    get_template,
    search_templates,
)


@pytest.fixture
def runner():
    """Create CLI runner."""
    return CliRunner()


@pytest.fixture
def mock_manager():
    """Create mock settings manager."""
    with patch("claude_cli_helper.commands.mcp.manager") as mock:
        yield mock


def test_get_template_valid():
    """Test get_template với template hợp lệ."""
    template, info = get_template("filesystem")

    assert template is not None
    assert info is not None
    assert template.command == "npx"
    assert info["category"] == "File Access"


def test_get_template_invalid():
    """Test get_template với template không tồn tại."""
    result = get_template("nonexistent")
    assert result is None


def test_search_templates_by_name():
    """Test search templates theo tên."""
    results = search_templates("github")

    assert "github" in results
    assert len(results) >= 1


def test_search_templates_by_description():
    """Test search templates theo description."""
    results = search_templates("database")

    assert "postgres" in results or "sqlite" in results


def test_search_templates_no_results():
    """Test search với query không match."""
    results = search_templates("xyz123nonexistent")
    assert len(results) == 0


def test_mcp_browse_all(runner):
    """Test browse tất cả templates."""
    result = runner.invoke(browse)

    assert result.exit_code == 0
    assert "Available MCP Server Templates" in result.output
    assert "filesystem" in result.output
    assert "github" in result.output


def test_mcp_browse_by_category(runner):
    """Test browse theo category."""
    result = runner.invoke(browse, ["--category", "Database"])

    assert result.exit_code == 0
    assert "postgres" in result.output or "sqlite" in result.output


def test_mcp_search(runner):
    """Test search command."""
    result = runner.invoke(search, ["database"])

    assert result.exit_code == 0
    assert "Search results for 'database'" in result.output


def test_mcp_search_no_results(runner):
    """Test search với không có kết quả."""
    result = runner.invoke(search, ["xyz123nonexistent"])

    assert result.exit_code == 0
    assert "No templates found" in result.output


def test_mcp_install_valid(runner, mock_manager):
    """Test install template hợp lệ."""
    # Setup
    mock_manager.read_mcp_config.return_value = MCPConfig()

    # Execute
    result = runner.invoke(install, ["filesystem"])

    # Assert
    assert result.exit_code == 0
    assert "Installing MCP Server: filesystem" in result.output
    assert "installed successfully" in result.output
    mock_manager.write_mcp_config.assert_called_once()


def test_mcp_install_invalid_template(runner, mock_manager):
    """Test install template không tồn tại."""
    mock_manager.read_mcp_config.return_value = MCPConfig()

    result = runner.invoke(install, ["nonexistent"])

    assert result.exit_code == 0
    assert "Template 'nonexistent' not found" in result.output


def test_mcp_install_custom_name(runner, mock_manager):
    """Test install với custom name."""
    # Setup
    mock_manager.read_mcp_config.return_value = MCPConfig()

    # Execute
    result = runner.invoke(install, ["filesystem", "--name", "my-fs"])

    # Assert
    assert result.exit_code == 0
    assert "my-fs" in result.output or "installed successfully" in result.output


def test_mcp_install_overwrite(runner, mock_manager):
    """Test install khi server đã tồn tại."""
    # Setup
    existing_config = MCPConfig(
        mcpServers={"filesystem": MCPServer(command="existing")}
    )
    mock_manager.read_mcp_config.return_value = existing_config

    # Execute (with auto-confirm no)
    result = runner.invoke(install, ["filesystem"], input="n\n")

    # Assert
    assert result.exit_code == 0
    assert "already exists" in result.output


def test_template_has_required_fields():
    """Test tất cả templates có required fields."""
    for name, template in MCP_TEMPLATES.items():
        assert template.command
        assert isinstance(template.args, list)
        assert isinstance(template.env, dict)

        # Check template info exists
        assert name in TEMPLATE_INFO
        info = TEMPLATE_INFO[name]
        assert "description" in info
        assert "category" in info


def test_template_info_consistency():
    """Test template info consistency."""
    # All templates should have info
    assert set(MCP_TEMPLATES.keys()) == set(TEMPLATE_INFO.keys())


def test_templates_are_valid_mcp_servers():
    """Test tất cả templates là valid MCPServer instances."""
    for name, template in MCP_TEMPLATES.items():
        assert isinstance(template, MCPServer)
        # Validate can be serialized
        data = template.model_dump()
        assert "command" in data
        assert "args" in data
        assert "env" in data
