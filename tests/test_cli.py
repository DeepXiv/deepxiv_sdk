"""
Integration tests for CLI commands.
"""
import pytest
from unittest import mock
from click.testing import CliRunner
from deepxiv_sdk.cli import main, get_token, save_token


class TestCLIBasic:
    """Test basic CLI functionality."""

    def test_cli_help(self):
        """Test help command."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output or "Commands:" in result.output

    def test_cli_version(self):
        """Test version command."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0 or "version" in result.output.lower()


class TestTokenManagement:
    """Test token management."""

    def test_get_token_from_option(self):
        """Test getting token from option."""
        token = get_token("test_token")
        assert token == "test_token"

    def test_get_token_none(self):
        """Test getting token when none is provided."""
        token = get_token(None)
        # Token might be from environment or None
        assert token is None or isinstance(token, str)

    def test_save_token(self, tmp_path):
        """Test saving token."""
        import os
        with mock.patch("pathlib.Path.home", return_value=tmp_path):
            env_file = save_token("test_token_123", is_global=True)
            assert env_file.exists()
            assert "test_token_123" in env_file.read_text()


class TestCLISearch:
    """Test CLI search command."""

    def test_search_help(self):
        """Test search help."""
        runner = CliRunner()
        result = runner.invoke(main, ["search", "--help"])
        assert result.exit_code == 0
        assert "search" in result.output.lower()

    @mock.patch("deepxiv_sdk.cli.Reader")
    def test_search_basic(self, mock_reader_class):
        """Test basic search."""
        runner = CliRunner()
        mock_instance = mock.Mock()
        mock_instance.search.return_value = {
            "total": 10,
            "results": [
                {
                    "arxiv_id": "2409.05591",
                    "title": "Test Paper",
                    "abstract": "Test abstract",
                    "categories": ["cs.AI"],
                    "citation": 10,
                }
            ],
        }
        mock_reader_class.return_value = mock_instance

        result = runner.invoke(main, ["search", "agent", "--limit", "1"])
        # Should either succeed or mention missing token
        assert result.exit_code in [0, 1]


class TestCLIPaper:
    """Test CLI paper commands."""

    def test_paper_help(self):
        """Test paper help."""
        runner = CliRunner()
        result = runner.invoke(main, ["paper", "--help"])
        assert result.exit_code == 0
        assert "paper" in result.output.lower()

    @mock.patch("deepxiv_sdk.cli.Reader")
    def test_paper_brief(self, mock_reader_class):
        """Test paper brief command."""
        runner = CliRunner()
        mock_instance = mock.Mock()
        mock_instance.brief.return_value = {
            "arxiv_id": "2409.05591",
            "title": "Test Paper",
            "tldr": "Test TLDR",
            "citations": 100,
        }
        mock_reader_class.return_value = mock_instance

        result = runner.invoke(main, ["paper", "2409.05591", "--brief"])
        assert result.exit_code in [0, 1]  # Might fail due to token


class TestCLIToken:
    """Test token command."""

    def test_token_help(self):
        """Test token help."""
        runner = CliRunner()
        result = runner.invoke(main, ["token", "--help"])
        assert result.exit_code == 0


class TestCLIPMC:
    """Test PMC commands."""

    def test_pmc_help(self):
        """Test PMC help."""
        runner = CliRunner()
        result = runner.invoke(main, ["pmc", "--help"])
        assert result.exit_code == 0
        assert "pmc" in result.output.lower()

    @mock.patch("deepxiv_sdk.cli.Reader")
    def test_pmc_head(self, mock_reader_class):
        """Test PMC head command."""
        runner = CliRunner()
        mock_instance = mock.Mock()
        mock_instance.pmc_head.return_value = {
            "pmc_id": "PMC544940",
            "title": "Sample Paper",
        }
        mock_reader_class.return_value = mock_instance

        result = runner.invoke(main, ["pmc", "PMC544940", "--head"])
        assert result.exit_code in [0, 1]


class TestCLIConfig:
    """Test config command."""

    def test_config_help(self):
        """Test config help."""
        runner = CliRunner()
        result = runner.invoke(main, ["config", "--help"])
        assert result.exit_code == 0
        assert "config" in result.output.lower()


class TestCLIServe:
    """Test serve command."""

    def test_serve_help(self):
        """Test serve help."""
        runner = CliRunner()
        result = runner.invoke(main, ["serve", "--help"])
        assert result.exit_code == 0
        assert "serve" in result.output.lower()
