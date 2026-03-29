"""
Pytest configuration and shared fixtures for deepxiv-sdk tests.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


@pytest.fixture
def sample_paper_head():
    """Sample paper head response."""
    return {
        "arxiv_id": "2409.05591",
        "title": "MemGPT: Towards LLMs as Operating Systems",
        "abstract": "This paper introduces MemGPT, a system...",
        "authors": [
            {"name": "Charles Patel", "orgs": ["UC Berkeley"]},
            {"name": "Anush Trivedi", "orgs": ["CMU"]},
        ],
        "categories": ["cs.AI", "cs.CL"],
        "publish_at": "2023-10-01",
        "token_count": 25000,
        "sections": {
            "1. Introduction": {
                "tldr": "We propose MemGPT...",
                "token_count": 2000,
                "idx": 1,
            },
            "2. Related Work": {
                "tldr": "Related work includes...",
                "token_count": 1500,
                "idx": 2,
            },
            "3. Methods": {
                "tldr": "Our method uses...",
                "token_count": 5000,
                "idx": 3,
            },
        },
    }


@pytest.fixture
def sample_paper_brief():
    """Sample paper brief response."""
    return {
        "arxiv_id": "2409.05591",
        "title": "MemGPT: Towards LLMs as Operating Systems",
        "tldr": "MemGPT is a system that enables LLMs to manage their own context memory...",
        "keywords": ["llm", "memory", "context", "operating system"],
        "citations": 150,
        "publish_at": "2023-10-01",
        "src_url": "https://arxiv.org/pdf/2409.05591.pdf",
    }


@pytest.fixture
def sample_search_results():
    """Sample search results response."""
    return {
        "total": 1250,
        "took": 45,
        "results": [
            {
                "arxiv_id": "2409.05591",
                "title": "MemGPT: Towards LLMs as Operating Systems",
                "abstract": "This paper introduces MemGPT...",
                "categories": ["cs.AI", "cs.CL"],
                "citation": 150,
                "score": 0.95,
            },
            {
                "arxiv_id": "2504.21776",
                "title": "Agent Memory Benchmark",
                "abstract": "We propose a benchmark...",
                "categories": ["cs.AI"],
                "citation": 45,
                "score": 0.87,
            },
        ],
    }


@pytest.fixture
def sample_pmc_head():
    """Sample PMC paper head response."""
    return {
        "pmc_id": "PMC544940",
        "title": "Sample Biomedical Paper",
        "abstract": "This is a sample biomedical paper...",
        "authors": [
            {"name": "Jane Smith"},
            {"name": "John Doe"},
        ],
        "categories": ["Medicine", "Biology"],
        "publish_at": "2023-05-15",
        "doi": "10.1234/example.12345",
    }


@pytest.fixture
def mock_reader(sample_paper_head, sample_paper_brief, sample_search_results):
    """Create a mock Reader with predefined responses."""
    from deepxiv_sdk import Reader

    reader = Reader(token="test_token")

    # Mock the _make_request method
    def mock_make_request(url, params=None, retry_count=0):
        if params and params.get("type") == "head":
            return sample_paper_head
        elif params and params.get("type") == "brief":
            return sample_paper_brief
        elif params and params.get("type") == "retrieve":
            return sample_search_results
        elif params and params.get("type") == "raw":
            return {"raw": "# Full Paper Content\n\nThis is the full content..."}
        elif params and params.get("type") == "preview":
            return {
                "content": "Paper preview..." * 100,
                "is_truncated": True,
                "total_characters": 50000,
            }
        elif params and params.get("type") == "section":
            return {"content": "# Introduction\n\nThis is the introduction section..."}
        return {}

    with patch.object(reader, "_make_request", side_effect=mock_make_request):
        yield reader


@pytest.fixture
def mock_reader_with_errors():
    """Create a mock Reader that raises errors."""
    from deepxiv_sdk import Reader, AuthenticationError, RateLimitError

    reader = Reader(token="invalid_token")

    def mock_make_request(url, params=None, retry_count=0):
        if "invalid" in str(url):
            raise AuthenticationError("Invalid token")
        if "rate_limit" in str(url):
            raise RateLimitError("Daily limit reached")
        return {}

    with patch.object(reader, "_make_request", side_effect=mock_make_request):
        yield reader


@pytest.fixture
def tmp_env_file(tmp_path):
    """Create a temporary .env file."""
    env_file = tmp_path / ".env"
    env_file.write_text("DEEPXIV_TOKEN=test_token_value\n")
    return env_file
