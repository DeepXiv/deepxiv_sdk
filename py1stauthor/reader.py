"""
Reader class for accessing the arXiv data service API.
"""
import requests
from typing import Dict, List, Optional, Any


class Reader:
    """Reader for accessing arXiv papers via the data service API."""
    
    def __init__(self, token: str, base_url: str = "https://data.rag.ac.cn"):
        """
        Initialize the Reader.
        
        Args:
            token: API token for authentication
            base_url: Base URL of the data service (default: https://data.rag.ac.cn)
        """
        self.token = token
        self.base_url = base_url.rstrip('/')
        self.arxiv_endpoint = f"{self.base_url}/arxiv/"
        self.search_endpoint = f"{self.base_url}/search"
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
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
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
    
    def list_service(self) -> Optional[Dict]:
        """
        List available services.
        
        Returns:
            Dictionary with service information
        """
        url = f"{self.base_url}/api/service"
        return self._make_request(url, params={"token": self.token})
    
    def search(
        self, 
        query: str, 
        top_k: int = 10,
        filters: Optional[Dict] = None
    ) -> Optional[List[Dict]]:
        """
        Search for papers.
        
        Args:
            query: Search query string
            top_k: Number of results to return (default: 10)
            filters: Optional filters for the search
            
        Returns:
            List of search results
        """
        params = {
            "query": query,
            "top_k": top_k,
            "token": self.token
        }
        
        if filters:
            params.update(filters)
        
        result = self._make_request(self.search_endpoint, params=params)
        
        if result and "results" in result:
            return result["results"]
        return result
    
    def head(self, arxiv_id: str) -> Optional[Dict]:
        """
        Get paper head information (metadata, abstract, sections overview).
        
        Args:
            arxiv_id: arXiv ID (e.g., "2503.04975")
            
        Returns:
            Dictionary with paper head information
        """
        params = {
            "arxiv_id": arxiv_id,
            "type": "head",
            "token": self.token
        }
        return self._make_request(self.arxiv_endpoint, params=params)
    
    def section(self, arxiv_id: str, section_name: str) -> Optional[str]:
        """
        Get a specific section content from a paper.
        
        Args:
            arxiv_id: arXiv ID (e.g., "2503.04975")
            section_name: Name of the section (e.g., "Introduction", "Method")
            
        Returns:
            Section content as string
        """
        params = {
            "arxiv_id": arxiv_id,
            "type": "section",
            "section": section_name,
            "token": self.token
        }
        result = self._make_request(self.arxiv_endpoint, params=params)
        
        if result:
            return result.get("content", "")
        return None
    
    def raw(self, arxiv_id: str) -> Optional[str]:
        """
        Get the full paper content in markdown format.
        
        Args:
            arxiv_id: arXiv ID (e.g., "2503.04975")
            
        Returns:
            Full paper content as string
        """
        params = {
            "arxiv_id": arxiv_id,
            "type": "raw",
            "token": self.token
        }
        result = self._make_request(self.arxiv_endpoint, params=params)
        
        if result:
            return result.get("raw", "")
        return None
    
    def meta(self, arxiv_id: str) -> Optional[Dict]:
        """
        Get paper metadata.
        
        Args:
            arxiv_id: arXiv ID (e.g., "2503.04975")
            
        Returns:
            Dictionary with paper metadata
        """
        params = {
            "arxiv_id": arxiv_id,
            "type": "meta",
            "token": self.token
        }
        return self._make_request(self.arxiv_endpoint, params=params)
    
    def preview(self, arxiv_id: str, max_tokens: int = 2000) -> Optional[Dict]:
        """
        Get a preview of the paper with limited tokens.
        
        Args:
            arxiv_id: arXiv ID (e.g., "2503.04975")
            max_tokens: Maximum tokens to return (default: 2000)
            
        Returns:
            Dictionary with preview information
        """
        params = {
            "arxiv_id": arxiv_id,
            "type": "preview",
            "max_tokens": max_tokens,
            "token": self.token
        }
        return self._make_request(self.arxiv_endpoint, params=params)
