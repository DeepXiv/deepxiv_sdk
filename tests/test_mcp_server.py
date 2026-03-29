"""
Unit tests for the MCP Server tools.
"""
import pytest
from unittest import mock
import json


class TestMCPSearchPapers:
    """Test search_papers MCP tool."""

    @mock.patch("deepxiv_sdk.mcp_server._reader")
    def test_search_papers_success(self, mock_reader):
        """Test successful search."""
        from deepxiv_sdk.mcp_server import search_papers

        mock_reader.search.return_value = {
            "total": 100,
            "results": [
                {
                    "arxiv_id": "2409.05591",
                    "title": "Test Paper",
                    "abstract": "Test abstract" * 20,
                    "categories": ["cs.AI"],
                    "citation": 50,
                    "score": 0.95,
                }
            ],
        }

        result = search_papers("test query")
        assert isinstance(result, str)
        assert "Test Paper" in result
        assert "2409.05591" in result

    @mock.patch("deepxiv_sdk.mcp_server._reader")
    def test_search_papers_no_results(self, mock_reader):
        """Test search with no results."""
        from deepxiv_sdk.mcp_server import search_papers

        mock_reader.search.return_value = {"total": 0, "results": []}

        result = search_papers("nonexistent query")
        assert isinstance(result, str)
        assert "No papers found" in result or "not found" in result.lower()

    @mock.patch("deepxiv_sdk.mcp_server._reader")
    def test_search_papers_error_handling(self, mock_reader):
        """Test error handling in search."""
        from deepxiv_sdk.mcp_server import search_papers
        from deepxiv_sdk import AuthenticationError

        mock_reader.search.side_effect = AuthenticationError("Invalid token")

        result = search_papers("test")
        assert "Authentication" in result or "token" in result.lower()

    def test_search_papers_empty_query(self):
        """Test search with empty query."""
        from deepxiv_sdk.mcp_server import search_papers

        result = search_papers("")
        assert "empty" in result.lower() or "cannot" in result.lower()


class TestMCPPaperBrief:
    """Test get_paper_brief MCP tool."""

    @mock.patch("deepxiv_sdk.mcp_server._reader")
    def test_get_paper_brief_success(self, mock_reader):
        """Test getting paper brief."""
        from deepxiv_sdk.mcp_server import get_paper_brief

        mock_reader.brief.return_value = {
            "arxiv_id": "2409.05591",
            "title": "Test Paper",
            "tldr": "This is a test paper about...",
            "keywords": ["test", "paper", "ai"],
            "citations": 100,
            "publish_at": "2024-01-01",
            "src_url": "https://arxiv.org/pdf/2409.05591.pdf",
        }

        result = get_paper_brief("2409.05591")
        assert isinstance(result, str)
        assert "Test Paper" in result
        assert "2409.05591" in result

    @mock.patch("deepxiv_sdk.mcp_server._reader")
    def test_get_paper_brief_not_found(self, mock_reader):
        """Test brief when paper not found."""
        from deepxiv_sdk.mcp_server import get_paper_brief

        mock_reader.brief.return_value = None

        result = get_paper_brief("invalid_id")
        assert "not found" in result.lower()

    def test_get_paper_brief_empty_id(self):
        """Test brief with empty paper ID."""
        from deepxiv_sdk.mcp_server import get_paper_brief

        result = get_paper_brief("")
        assert "empty" in result.lower() or "cannot" in result.lower()


class TestMCPPaperMetadata:
    """Test get_paper_metadata MCP tool."""

    @mock.patch("deepxiv_sdk.mcp_server._reader")
    def test_get_paper_metadata_success(self, mock_reader):
        """Test getting paper metadata."""
        from deepxiv_sdk.mcp_server import get_paper_metadata

        mock_reader.head.return_value = {
            "arxiv_id": "2409.05591",
            "title": "Test Paper",
            "abstract": "This is a test abstract",
            "authors": [
                {"name": "John Doe", "orgs": ["MIT"]},
                {"name": "Jane Smith", "orgs": ["Stanford"]},
            ],
            "categories": ["cs.AI", "cs.CL"],
            "publish_at": "2024-01-01",
            "token_count": 10000,
            "sections": {
                "Introduction": {
                    "tldr": "Intro TLDR",
                    "token_count": 1000,
                    "idx": 1,
                }
            },
        }

        result = get_paper_metadata("2409.05591")
        assert isinstance(result, str)
        assert "Test Paper" in result
        assert "John Doe" in result

    @mock.patch("deepxiv_sdk.mcp_server._reader")
    def test_get_paper_metadata_not_found(self, mock_reader):
        """Test metadata when paper not found."""
        from deepxiv_sdk.mcp_server import get_paper_metadata

        mock_reader.head.return_value = None

        result = get_paper_metadata("invalid_id")
        assert "not found" in result.lower()


class TestMCPPaperSection:
    """Test get_paper_section MCP tool."""

    @mock.patch("deepxiv_sdk.mcp_server._reader")
    def test_get_paper_section_success(self, mock_reader):
        """Test getting paper section."""
        from deepxiv_sdk.mcp_server import get_paper_section

        mock_reader.section.return_value = (
            "# Introduction\n\nThis is the introduction section..."
        )

        result = get_paper_section("2409.05591", "Introduction")
        assert isinstance(result, str)
        assert "Introduction" in result

    @mock.patch("deepxiv_sdk.mcp_server._reader")
    def test_get_paper_section_not_found(self, mock_reader):
        """Test section not found."""
        from deepxiv_sdk.mcp_server import get_paper_section

        mock_reader.section.side_effect = ValueError(
            "Section 'Invalid' not found in paper"
        )

        result = get_paper_section("2409.05591", "Invalid")
        assert "not found" in result.lower()

    def test_get_paper_section_empty_id(self):
        """Test section with empty paper ID."""
        from deepxiv_sdk.mcp_server import get_paper_section

        result = get_paper_section("", "Introduction")
        assert "empty" in result.lower() or "cannot" in result.lower()


class TestMCPFullPaper:
    """Test get_full_paper MCP tool."""

    @mock.patch("deepxiv_sdk.mcp_server._reader")
    def test_get_full_paper_success(self, mock_reader):
        """Test getting full paper."""
        from deepxiv_sdk.mcp_server import get_full_paper

        mock_reader.raw.return_value = "# Full Paper\n\nThis is the full content..."

        result = get_full_paper("2409.05591")
        assert isinstance(result, str)
        assert "Full Paper" in result

    @mock.patch("deepxiv_sdk.mcp_server._reader")
    def test_get_full_paper_not_found(self, mock_reader):
        """Test full paper not found."""
        from deepxiv_sdk.mcp_server import get_full_paper

        mock_reader.raw.return_value = None

        result = get_full_paper("invalid_id")
        assert "Failed" in result or "not found" in result.lower()


class TestMCPPreview:
    """Test get_paper_preview MCP tool."""

    @mock.patch("deepxiv_sdk.mcp_server._reader")
    def test_get_paper_preview_success(self, mock_reader):
        """Test getting paper preview."""
        from deepxiv_sdk.mcp_server import get_paper_preview

        mock_reader.preview.return_value = {
            "content": "Preview content " * 100,
            "is_truncated": True,
            "total_characters": 50000,
        }

        result = get_paper_preview("2409.05591")
        assert isinstance(result, str)
        assert "Preview content" in result

    @mock.patch("deepxiv_sdk.mcp_server._reader")
    def test_get_paper_preview_not_found(self, mock_reader):
        """Test preview not found."""
        from deepxiv_sdk.mcp_server import get_paper_preview

        mock_reader.preview.return_value = None

        result = get_paper_preview("invalid_id")
        assert "Failed" in result or "not found" in result.lower()


class TestMCPPMCMetadata:
    """Test get_pmc_metadata MCP tool."""

    @mock.patch("deepxiv_sdk.mcp_server._reader")
    def test_get_pmc_metadata_success(self, mock_reader):
        """Test getting PMC metadata."""
        from deepxiv_sdk.mcp_server import get_pmc_metadata

        mock_reader.pmc_head.return_value = {
            "pmc_id": "PMC544940",
            "title": "Sample PMC Paper",
            "abstract": "Sample abstract",
            "authors": [{"name": "Author Name"}],
            "doi": "10.1234/example.12345",
            "publish_at": "2023-01-01",
        }

        result = get_pmc_metadata("PMC544940")
        assert isinstance(result, str)
        assert "PMC544940" in result
        assert "Sample PMC Paper" in result

    @mock.patch("deepxiv_sdk.mcp_server._reader")
    def test_get_pmc_metadata_not_found(self, mock_reader):
        """Test PMC metadata not found."""
        from deepxiv_sdk.mcp_server import get_pmc_metadata

        mock_reader.pmc_head.return_value = None

        result = get_pmc_metadata("invalid_id")
        assert "not found" in result.lower()


class TestMCPPMCFull:
    """Test get_pmc_full MCP tool."""

    @mock.patch("deepxiv_sdk.mcp_server._reader")
    def test_get_pmc_full_success(self, mock_reader):
        """Test getting full PMC paper."""
        from deepxiv_sdk.mcp_server import get_pmc_full

        mock_reader.pmc_full.return_value = {
            "pmc_id": "PMC544940",
            "content": "Full PMC content",
        }

        result = get_pmc_full("PMC544940")
        assert isinstance(result, str)
        json_obj = json.loads(result)
        assert "pmc_id" in json_obj

    @mock.patch("deepxiv_sdk.mcp_server._reader")
    def test_get_pmc_full_not_found(self, mock_reader):
        """Test full PMC not found."""
        from deepxiv_sdk.mcp_server import get_pmc_full

        mock_reader.pmc_full.return_value = None

        result = get_pmc_full("invalid_id")
        assert "Failed" in result or "not found" in result.lower()
