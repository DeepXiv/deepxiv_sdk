"""
Reader class for accessing the arXiv data service API.
"""
import requests
from typing import Dict, List, Optional, Any


class Reader:
    """Reader for accessing arXiv papers via the data service API."""
    
    def __init__(self, token: Optional[str] = None, base_url: str = "https://data.rag.ac.cn"):
        """
        Initialize the Reader.
        
        Args:
            token: API token for authentication (optional for free papers)
            base_url: Base URL of the data service (default: https://data.rag.ac.cn)
        """
        self.token = token
        self.base_url = base_url.rstrip('/')
        self.arxiv_endpoint = f"{self.base_url}/arxiv/"
        self.timeout = 60
    
    def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """
        Make a request to the API.
        
        Args:
            url: URL to request
            params: Query parameters
            
        Returns:
            Response JSON or None on error
        """
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout as e:
            print(f"Timeout error: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
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
        date_to: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Search for papers using Elasticsearch hybrid search (BM25 + Vector).
        
        Args:
            query: Search query string
            size: Number of results to return (default: 10)
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
        """
        params = {
            "type": "retrieve",
            "query": query,
            "size": size,
            "offset": offset,
            "search_mode": search_mode
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
        
        return self._make_request(self.arxiv_endpoint, params=params)
    
    def head(self, arxiv_id: str) -> Optional[Dict]:
        """
        Get paper head information (metadata, abstract, sections overview).
        
        Args:
            arxiv_id: arXiv ID (e.g., "2409.05591", "2504.21776")
            
        Returns:
            Dictionary with paper head information including:
            - title: Paper title
            - abstract: Paper abstract
            - authors: List of authors
            - sections: Section names and metadata
            - token_count: Total tokens in the paper
            - categories: arXiv categories
            - publish_at: Publication date
        """
        params = {
            "arxiv_id": arxiv_id,
            "type": "head"
        }
        return self._make_request(self.arxiv_endpoint, params=params)
    
    def section(self, arxiv_id: str, section_name: str) -> Optional[str]:
        """
        Get a specific section content from a paper.
        
        Args:
            arxiv_id: arXiv ID (e.g., "2409.05591")
            section_name: Name of the section (e.g., "Introduction", "Methods", "Conclusion")
            
        Returns:
            Section content as string
        """
        params = {
            "arxiv_id": arxiv_id,
            "type": "section",
            "section": section_name
        }
        result = self._make_request(self.arxiv_endpoint, params=params)
        
        if result:
            return result.get("content", "")
        return None
    
    def raw(self, arxiv_id: str) -> Optional[str]:
        """
        Get the full paper content in markdown format.
        
        Args:
            arxiv_id: arXiv ID (e.g., "2409.05591")
            
        Returns:
            Full paper content as markdown string
        """
        params = {
            "arxiv_id": arxiv_id,
            "type": "raw"
        }
        result = self._make_request(self.arxiv_endpoint, params=params)
        
        if result:
            return result.get("raw", "")
        return None
    
    def preview(self, arxiv_id: str) -> Optional[Dict]:
        """
        Get a preview of the paper (first 10,000 characters).
        Useful for mobile devices or when you want to quickly scan the introduction.
        
        Args:
            arxiv_id: arXiv ID (e.g., "2409.05591")
            
        Returns:
            Dictionary with preview information including:
            - preview: First 10,000 characters
            - is_truncated: Whether content was truncated
            - total_characters: Total characters in full document
            - preview_characters: Characters in preview (10,000)
        """
        params = {
            "arxiv_id": arxiv_id,
            "type": "preview"
        }
        return self._make_request(self.arxiv_endpoint, params=params)
    
    def json(self, arxiv_id: str) -> Optional[Dict]:
        """
        Get the complete structured JSON file with all sections and metadata.
        
        Args:
            arxiv_id: arXiv ID (e.g., "2409.05591")
            
        Returns:
            Complete structured JSON with all paper data
        """
        params = {
            "arxiv_id": arxiv_id,
            "type": "json"
        }
        return self._make_request(self.arxiv_endpoint, params=params)
    
    def markdown(self, arxiv_id: str) -> str:
        """
        Get the URL for beautifully rendered HTML page for viewing in a browser.
        
        Args:
            arxiv_id: arXiv ID (e.g., "2409.05591")
            
        Returns:
            URL string for the HTML view
        """
        params = {
            "arxiv_id": arxiv_id,
            "type": "markdown"
        }
        # For markdown view, return the URL directly since it returns HTML
        from urllib.parse import urlencode
        query_string = urlencode(params)
        return f"{self.arxiv_endpoint}?{query_string}"