"""
Reader class for accessing the arXiv data service API.
Provides typed interface with robust error handling and logging.
"""
import logging
import requests
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

# Configure logger
logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base exception for API errors."""
    pass


class AuthenticationError(APIError):
    """Raised when authentication fails (401, invalid token)."""
    pass


class RateLimitError(APIError):
    """Raised when rate limit is exceeded (429)."""
    pass


class NotFoundError(APIError):
    """Raised when requested resource is not found (404)."""
    pass


class ServerError(APIError):
    """Raised when server returns 5xx error."""
    pass


class Reader:
    """Reader for accessing arXiv papers via the data service API.

    Provides comprehensive paper search, metadata retrieval, and content access
    with support for hybrid search (BM25 + Vector) and PMC biomedical literature.

    Attributes:
        token: API token for authentication (optional for free papers)
        base_url: Base URL of the data service
        timeout: Request timeout in seconds (default: 60)
        max_retries: Maximum number of retry attempts (default: 3)
        retry_delay: Initial retry delay in seconds (default: 1)
    """

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = "https://data.rag.ac.cn",
        timeout: int = 60,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        """
        Initialize the Reader.

        Args:
            token: API token for authentication (optional for free papers)
            base_url: Base URL of the data service (default: https://data.rag.ac.cn)
            timeout: Request timeout in seconds (default: 60)
            max_retries: Maximum number of retry attempts (default: 3)
            retry_delay: Initial retry delay in seconds (default: 1.0)
        """
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.arxiv_endpoint = f"{self.base_url}/arxiv/"
        self.pmc_endpoint = f"{self.base_url}/pmc/"
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        logger.debug(
            f"Reader initialized with base_url={self.base_url}, "
            f"token={'***' if token else 'None'}"
        )

    def _make_request(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> Optional[Dict[str, Any]]:
        """
        Make a request to the API with retry logic and comprehensive error handling.

        Args:
            url: URL to request
            params: Query parameters
            retry_count: Current retry attempt number (internal use)

        Returns:
            Response JSON or None if max retries exceeded

        Raises:
            AuthenticationError: Invalid or expired token (401)
            RateLimitError: Daily limit reached (429)
            NotFoundError: Resource not found (404)
            ServerError: Server error (5xx)
            APIError: Other API errors
        """
        headers: Dict[str, str] = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            logger.debug(f"Making request to {url} with params {params}")
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout,
            )

            # Handle HTTP errors with appropriate exceptions
            if response.status_code == 401:
                logger.error("Authentication failed: Invalid or expired token")
                raise AuthenticationError(
                    "Invalid or expired token. Run 'deepxiv config' to set a valid token."
                )
            elif response.status_code == 404:
                logger.warning(f"Resource not found: {url}")
                raise NotFoundError(f"Paper not found. Check your arXiv/PMC ID.")
            elif response.status_code == 429:
                logger.warning("Rate limit exceeded")
                raise RateLimitError(
                    "Daily limit reached. Email tommy@chien.io for higher limits."
                )
            elif response.status_code >= 500:
                logger.error(f"Server error {response.status_code}: {response.text}")
                raise ServerError(f"Server error {response.status_code}")

            response.raise_for_status()
            result = response.json()
            logger.debug(f"Successfully received response from {url}")
            return result

        except requests.exceptions.Timeout as e:
            if retry_count < self.max_retries:
                wait_time = self.retry_delay * (2 ** retry_count)
                logger.warning(
                    f"Request timeout (attempt {retry_count + 1}/{self.max_retries}), "
                    f"retrying in {wait_time}s..."
                )
                time.sleep(wait_time)
                return self._make_request(url, params, retry_count + 1)
            else:
                logger.error(f"Request timeout after {self.max_retries} retries")
                raise APIError(
                    f"Request timed out after {self.max_retries} retries. "
                    "Check your internet connection or try again later."
                )

        except requests.exceptions.ConnectionError as e:
            if retry_count < self.max_retries:
                wait_time = self.retry_delay * (2 ** retry_count)
                logger.warning(
                    f"Connection error (attempt {retry_count + 1}/{self.max_retries}), "
                    f"retrying in {wait_time}s..."
                )
                time.sleep(wait_time)
                return self._make_request(url, params, retry_count + 1)
            else:
                logger.error(f"Connection error after {self.max_retries} retries")
                raise APIError(
                    f"Failed to connect to {url}. "
                    "Check your internet connection or try again later."
                )

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e}")
            raise APIError(f"HTTP error {e.response.status_code}: {str(e)}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise APIError(f"Request failed: {str(e)}")

        except ValueError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise APIError(f"Invalid response format: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise APIError(f"Unexpected error: {str(e)}")

    def search(
        self,
        query: str,
        size: int = 10,
        offset: int = 0,
        search_mode: str = "hybrid",
        bm25_weight: float = 0.5,
        vector_weight: float = 0.5,
        categories: Optional[List[str]] = None,
        authors: Optional[List[str]] = None,
        min_citation: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search for papers using hybrid search (BM25 + Vector).

        Args:
            query: Search query string
            size: Number of results to return (default: 10, max: 100)
            offset: Result offset for pagination (default: 0)
            search_mode: Search mode - "bm25", "vector", or "hybrid" (default: "hybrid")
            bm25_weight: BM25 weight for hybrid search (default: 0.5)
            vector_weight: Vector weight for hybrid search (default: 0.5)
            categories: Filter by categories (e.g., ["cs.AI", "cs.CL"])
            authors: Filter by authors
            min_citation: Minimum citation count
            date_from: Publication date from (format: YYYY-MM-DD)
            date_to: Publication date to (format: YYYY-MM-DD)

        Returns:
            Dictionary with search results including 'total', 'took', and 'results' fields

        Raises:
            APIError: If the request fails
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        if size < 1 or size > 100:
            raise ValueError("Size must be between 1 and 100")
        if offset < 0:
            raise ValueError("Offset must be non-negative")

        params: Dict[str, Any] = {
            "type": "retrieve",
            "query": query,
            "size": size,
            "offset": offset,
            "search_mode": search_mode,
        }

        if search_mode == "hybrid":
            params["bm25_weight"] = bm25_weight
            params["vector_weight"] = vector_weight

        if categories:
            params["categories"] = ",".join(categories)
        if authors:
            params["authors"] = ",".join(authors)
        if min_citation is not None:
            params["min_citation"] = min_citation
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to

        result = self._make_request(self.arxiv_endpoint, params=params)
        logger.info(f"Search for '{query}' returned {result.get('total', 0)} results")
        return result or {"total": 0, "results": []}

    def head(self, arxiv_id: str) -> Dict[str, Any]:
        """
        Get paper metadata and structure (head information).

        Args:
            arxiv_id: arXiv ID (e.g., "2409.05591", "2504.21776")

        Returns:
            Dictionary with paper head information including:
            - title: Paper title
            - abstract: Paper abstract
            - authors: List of authors
            - sections: List of section information
            - token_count: Total tokens in the paper
            - categories: arXiv categories
            - publish_at: Publication date

        Raises:
            APIError: If the request fails
        """
        if not arxiv_id or not arxiv_id.strip():
            raise ValueError("arxiv_id cannot be empty")

        params: Dict[str, Any] = {"arxiv_id": arxiv_id, "type": "head"}
        result = self._make_request(self.arxiv_endpoint, params=params)
        return result or {}

    def brief(self, arxiv_id: str) -> Dict[str, Any]:
        """
        Get brief paper information (concise summary for quick overview).

        Args:
            arxiv_id: arXiv ID (e.g., "2409.05591", "2504.21776")

        Returns:
            Dictionary with brief paper information including:
            - arxiv_id: arXiv paper ID
            - title: Paper title
            - tldr: AI-generated summary (if available)
            - keywords: List of keywords (if available)
            - publish_at: Publication date
            - citations: Citation count
            - src_url: Direct link to PDF

        Raises:
            APIError: If the request fails
        """
        if not arxiv_id or not arxiv_id.strip():
            raise ValueError("arxiv_id cannot be empty")

        params: Dict[str, Any] = {"arxiv_id": arxiv_id, "type": "brief"}
        result = self._make_request(self.arxiv_endpoint, params=params)
        return result or {}

    def _match_section_name(self, arxiv_id: str, section_name: str) -> Optional[str]:
        """
        Match user input to actual section name (case-insensitive, partial match).

        Args:
            arxiv_id: arXiv ID
            section_name: User-provided section name (e.g., "Introduction", "introduction")

        Returns:
            Matched section name or None if not found
        """
        head = self.head(arxiv_id)
        if not head or "sections" not in head:
            return None

        sections: List[Dict[str, Any]] = head.get("sections", [])
        section_lower = section_name.lower()

        # Extract section names
        section_names = [
            section["name"] if isinstance(section, dict) else str(section)
            for section in sections
        ]

        # Try exact match first (case-insensitive)
        for name in section_names:
            if name.lower() == section_lower:
                return name

        # Try partial match (section name contains the query)
        for name in section_names:
            # Remove leading numbers like "1. " or "2. "
            clean_name = name.lower()
            if clean_name.startswith(tuple(f"{i}. " for i in range(10))):
                clean_name = clean_name[3:]

            if clean_name == section_lower or section_lower in clean_name:
                return name

        logger.warning(
            f"Section '{section_name}' not found in paper {arxiv_id}. "
            f"Available sections: {', '.join(section_names)}"
        )
        return None

    def section(self, arxiv_id: str, section_name: str) -> str:
        """
        Get a specific section content from a paper.

        Args:
            arxiv_id: arXiv ID (e.g., "2409.05591")
            section_name: Name of the section (e.g., "Introduction", "introduction", "Method")
                         Case-insensitive, partial match supported.

        Returns:
            Section content as string

        Raises:
            APIError: If the request fails
            ValueError: If section is not found
        """
        if not arxiv_id or not arxiv_id.strip():
            raise ValueError("arxiv_id cannot be empty")
        if not section_name or not section_name.strip():
            raise ValueError("section_name cannot be empty")

        # Match section name (case-insensitive)
        matched_name = self._match_section_name(arxiv_id, section_name)
        if not matched_name:
            raise ValueError(
                f"Section '{section_name}' not found in paper {arxiv_id}"
            )

        params: Dict[str, Any] = {
            "arxiv_id": arxiv_id,
            "type": "section",
            "section": matched_name,
        }
        result = self._make_request(self.arxiv_endpoint, params=params)

        return result.get("content", "") if result else ""

    def raw(self, arxiv_id: str) -> str:
        """
        Get the full paper content in markdown format.

        Args:
            arxiv_id: arXiv ID (e.g., "2409.05591")

        Returns:
            Full paper content as markdown string

        Raises:
            APIError: If the request fails
        """
        if not arxiv_id or not arxiv_id.strip():
            raise ValueError("arxiv_id cannot be empty")

        params: Dict[str, Any] = {"arxiv_id": arxiv_id, "type": "raw"}
        result = self._make_request(self.arxiv_endpoint, params=params)

        return result.get("raw", "") if result else ""

    def preview(self, arxiv_id: str) -> Dict[str, Any]:
        """
        Get a preview of the paper (first 10,000 characters).
        Useful for mobile devices or when you want to quickly scan the introduction.

        Args:
            arxiv_id: arXiv ID (e.g., "2409.05591")

        Returns:
            Dictionary with preview information including:
            - content: First 10,000 characters
            - is_truncated: Whether content was truncated
            - total_characters: Total characters in full document

        Raises:
            APIError: If the request fails
        """
        if not arxiv_id or not arxiv_id.strip():
            raise ValueError("arxiv_id cannot be empty")

        params: Dict[str, Any] = {"arxiv_id": arxiv_id, "type": "preview"}
        result = self._make_request(self.arxiv_endpoint, params=params)

        return result or {"content": "", "is_truncated": False}

    def json(self, arxiv_id: str) -> Dict[str, Any]:
        """
        Get the complete structured JSON file with all sections and metadata.

        Args:
            arxiv_id: arXiv ID (e.g., "2409.05591")

        Returns:
            Complete structured JSON with all paper data

        Raises:
            APIError: If the request fails
        """
        if not arxiv_id or not arxiv_id.strip():
            raise ValueError("arxiv_id cannot be empty")

        params: Dict[str, Any] = {"arxiv_id": arxiv_id, "type": "json"}
        result = self._make_request(self.arxiv_endpoint, params=params)

        return result or {}

    def markdown(self, arxiv_id: str) -> str:
        """
        Get the HTML view URL for the paper.

        Args:
            arxiv_id: arXiv ID (e.g., "2409.05591")

        Returns:
            URL to the HTML view of the paper
        """
        if not arxiv_id or not arxiv_id.strip():
            raise ValueError("arxiv_id cannot be empty")

        return f"https://arxiv.org/html/{arxiv_id}"

    # ========== PMC (PubMed Central) Methods ==========

    def pmc_head(self, pmc_id: str) -> Dict[str, Any]:
        """
        Get PMC paper metadata (title, abstract, authors, categories, publication date).

        Args:
            pmc_id: PMC ID (e.g., "PMC544940", "PMC514704")

        Returns:
            Dictionary with PMC paper metadata including:
            - pmc_id: PMC paper ID
            - title: Paper title
            - doi: Digital Object Identifier
            - abstract: Paper abstract
            - authors: List of authors
            - categories: Medical subject categories
            - publish_at: Publication date

        Raises:
            APIError: If the request fails
        """
        if not pmc_id or not pmc_id.strip():
            raise ValueError("pmc_id cannot be empty")

        params: Dict[str, Any] = {"pmc_id": pmc_id, "type": "head"}
        result = self._make_request(self.pmc_endpoint, params=params)

        return result or {}

    def pmc_full(self, pmc_id: str) -> Dict[str, Any]:
        """
        Get the complete PMC paper in structured JSON format with full content and metadata.

        Args:
            pmc_id: PMC ID (e.g., "PMC544940", "PMC514704")

        Returns:
            Complete structured JSON with all PMC paper data

        Raises:
            APIError: If the request fails
        """
        if not pmc_id or not pmc_id.strip():
            raise ValueError("pmc_id cannot be empty")

        params: Dict[str, Any] = {"pmc_id": pmc_id, "type": "json"}
        result = self._make_request(self.pmc_endpoint, params=params)

        return result or {}

    # Alias for backwards compatibility
    def pmc_json(self, pmc_id: str) -> Dict[str, Any]:
        """Alias for pmc_full(). Get the complete PMC paper in JSON format."""
        return self.pmc_full(pmc_id)
