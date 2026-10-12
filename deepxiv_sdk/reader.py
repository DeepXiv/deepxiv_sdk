"""
Reader class for accessing the arXiv data service API.
Provides typed interface with robust error handling and logging.
"""
import json as _json
import logging
import requests
import time
import warnings
from typing import Dict, Iterator, List, Optional, Any, Union
from urllib.parse import urljoin

# Configure logger
logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base exception for API errors."""
    pass


class AuthenticationError(APIError):
    """Raised when authentication fails (401, invalid token)."""
    pass


class BadRequestError(APIError):
    """Raised when the request is invalid (400)."""
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


def agent_search_sources(event_or_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Pull the source list out of a ``sources`` event or a blocking result.

    The arXiv backend keys its list ``papers`` and the web backend keys it
    ``pages``; the blocking endpoint uses ``sources`` for both. This normalises
    all three so callers don't have to branch on the backend.
    """
    for key in ("papers", "pages", "sources"):
        value = event_or_result.get(key)
        if value is not None:
            return value
    return []


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
        self.agent_search_endpoints = {
            "arxiv": f"{self.base_url}/arxiv/agent/search",
            "web": f"{self.base_url}/web/agent/search",
        }
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
            BadRequestError: Invalid request parameters or malformed IDs (400)
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
            if response.status_code == 400:
                logger.warning(f"Bad request to {url}: {response.text}")
                raise BadRequestError(
                    "Invalid request. Please check your arXiv/PMC ID or command arguments."
                )
            elif response.status_code == 401:
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
            if not response.content:
                logger.debug(f"Empty response body from {url}")
                return {}
            result = response.json()
            logger.debug(f"Successfully received response from {url}")
            return result

        except APIError:
            raise

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

    # ========== Agentic Search Methods ==========

    # Backends served by the agentic search endpoints.
    AGENT_SEARCH_SOURCES = ("arxiv", "web")
    # Effort levels accepted by both backends.
    AGENT_SEARCH_EFFORTS = ("default", "high", "xhigh")
    # Google verticals accepted by the web backend.
    AGENT_SEARCH_WEB_TYPES = ("search", "scholar", "news", "images")
    # Quota units spent per agentic call, from a pool separate from daily_limit.
    AGENT_SEARCH_COST = 1
    # Answer-length bounds enforced upstream.
    AGENT_SEARCH_MIN_ANSWER_TOKENS = 256
    AGENT_SEARCH_MAX_ANSWER_TOKENS = 16384
    # Agentic search runs far longer than a plain lookup, so it gets its own
    # default timeout rather than inheriting ``self.timeout``. Upstream hiccups
    # can stretch a single call past 40s without affecting time-to-first-token.
    AGENT_SEARCH_TIMEOUT = 180

    def _build_agent_search_payload(
        self,
        query: str,
        source: str,
        effort: str,
        verbose: bool,
        stream_answer: bool,
        max_answer_tokens: int,
        language: Optional[str],
        top_k: Optional[int] = None,
        search_type: Optional[str] = None,
        gl: Optional[str] = None,
        hl: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Validate agentic search arguments and build the request body.

        Validation happens client-side so an obviously invalid call fails for
        free instead of spending a quota unit on a 422. Backend-specific
        arguments are rejected rather than silently dropped when they are sent
        to the backend that does not accept them.
        """
        if source not in self.AGENT_SEARCH_SOURCES:
            raise ValueError(
                f"source must be one of {list(self.AGENT_SEARCH_SOURCES)}"
            )
        if not query or not query.strip():
            raise ValueError("query cannot be empty")
        query = query.strip()
        if len(query) > 2000:
            raise ValueError(
                f"query must be at most 2000 characters (got {len(query)})"
            )
        if effort not in self.AGENT_SEARCH_EFFORTS:
            raise ValueError(
                f"effort must be one of {list(self.AGENT_SEARCH_EFFORTS)}"
            )
        if not (
            self.AGENT_SEARCH_MIN_ANSWER_TOKENS
            <= max_answer_tokens
            <= self.AGENT_SEARCH_MAX_ANSWER_TOKENS
        ):
            raise ValueError(
                "max_answer_tokens must be between "
                f"{self.AGENT_SEARCH_MIN_ANSWER_TOKENS} and "
                f"{self.AGENT_SEARCH_MAX_ANSWER_TOKENS}"
            )

        payload: Dict[str, Any] = {
            "query": query,
            "effort": effort,
            "verbose": verbose,
            "stream_answer": stream_answer,
            "max_answer_tokens": max_answer_tokens,
        }
        if language:
            payload["language"] = language

        if source == "arxiv":
            for name, value in (("search_type", search_type), ("gl", gl), ("hl", hl)):
                if value is not None:
                    raise ValueError(f"{name} is only valid for source='web'")
            if top_k is None:
                top_k = 10
            if top_k < 1 or top_k > 30:
                raise ValueError("top_k must be between 1 and 30")
            payload["top_k"] = top_k
        else:
            if top_k is not None:
                raise ValueError("top_k is only valid for source='arxiv'")
            if search_type is None:
                search_type = "search"
            if search_type not in self.AGENT_SEARCH_WEB_TYPES:
                raise ValueError(
                    f"search_type must be one of {list(self.AGENT_SEARCH_WEB_TYPES)}"
                )
            payload["search_type"] = search_type
            # Locale is left to the service unless explicitly pinned — it
            # switches to cn/zh-cn on its own for Chinese queries.
            if gl:
                payload["gl"] = gl
            if hl:
                payload["hl"] = hl

        return payload

    def _raise_for_agent_status(self, response: requests.Response) -> None:
        """Map agentic search HTTP errors onto the SDK exception hierarchy."""
        if response.status_code < 400:
            return

        detail = ""
        try:
            body = response.json()
            detail = body.get("detail", "") if isinstance(body, dict) else ""
            if isinstance(detail, list):  # FastAPI validation errors
                detail = "; ".join(
                    f"{'.'.join(str(x) for x in item.get('loc', [])[1:])}: {item.get('msg', '')}"
                    for item in detail
                )
        except ValueError:
            detail = (response.text or "")[:200]

        if response.status_code == 401:
            raise AuthenticationError(
                "Invalid or expired token. Run 'deepxiv config' to set a valid token."
            )
        if response.status_code == 403:
            # A working SDK token is still not enough here — agentic search is
            # gated to registered accounts, so say exactly what to do next.
            raise AuthenticationError(
                "Agentic search requires a registered account key; the token "
                "deepxiv auto-registers on first use is not eligible. "
                "Register at https://data.rag.ac.cn/register, then run "
                "'deepxiv config' with that key. "
                "Every other deepxiv command keeps working with the current token."
            )
        if response.status_code in (400, 422):
            raise BadRequestError(f"Invalid agentic search request: {detail}")
        if response.status_code == 429:
            raise RateLimitError(
                "Agentic search quota exhausted for today "
                f"({detail or 'see your tier limit'}). This pool is separate "
                "from your general daily limit — other deepxiv commands still "
                "work. Upgrade at https://data.rag.ac.cn/register."
            )
        if response.status_code >= 500:
            raise ServerError(f"Server error {response.status_code}: {detail}")
        raise APIError(f"HTTP error {response.status_code}: {detail}")

    def agent_search_stream(
        self,
        query: str,
        source: str = "arxiv",
        effort: str = "default",
        verbose: bool = False,
        stream_answer: bool = True,
        max_answer_tokens: int = 4096,
        language: Optional[str] = None,
        top_k: Optional[int] = None,
        search_type: Optional[str] = None,
        gl: Optional[str] = None,
        hl: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Iterator[Dict[str, Any]]:
        """
        Run an agentic search, yielding NDJSON events as they arrive.

        The service picks its own tools, reads sources when it needs to, and
        streams back an answer with citations.

        Args:
            query: The question. 1~2000 characters. Be specific — the service
                assumes the query is already refined. Chinese queries work
                directly (arXiv rewrites them to English for retrieval; web
                switches to a Chinese locale) and the answer follows the
                query's language.
            source: ``"arxiv"`` for the local full-text arXiv corpus, or
                ``"web"`` for Google plus cached page bodies.
            effort: ``"default"`` (1~2 gather rounds; ~3~4s to first token on
                arXiv, ~5~9s on web), ``"high"`` (3 rounds), or ``"xhigh"``
                (4~5 rounds).
            verbose: When ``True``, also emit ``tool_call`` / ``tool_result`` /
                ``thinking`` / ``warning`` events.
            stream_answer: When ``True`` the answer arrives as ``answer_delta``
                events; when ``False`` it arrives as a single ``answer`` event.
            max_answer_tokens: Hard cap on answer length.
            language: Answer language. Defaults to the query's language.
            top_k: ``source="arxiv"`` only — first-round retrieval size, 1~30
                (default 10).
            search_type: ``source="web"`` only — ``"search"`` (default),
                ``"scholar"``, ``"news"``, or ``"images"``.
            gl: ``source="web"`` only — Google country code. Left to the
                service by default.
            hl: ``source="web"`` only — Google UI language.
            timeout: Request timeout in seconds. Defaults to
                ``AGENT_SEARCH_TIMEOUT`` (180).

        Yields:
            Event dicts, each with an ``"event"`` key. Always present:
            ``billing`` (carries ``tier`` / ``used`` / ``remaining``),
            ``start``, ``answer_start``, ``answer_delta`` (or ``answer``),
            ``sources``, ``done``. ``error`` may appear instead of a normal
            completion.

            The ``sources`` event keys its payload by backend: ``papers`` for
            arXiv (``arxiv_id`` / ``title`` / ``url``) and ``pages`` for web
            (``url`` / ``title`` / ``read``, where ``read`` marks pages whose
            body the model actually read rather than just its snippet).

            ``answer_delta`` text contains only the final answer — process
            narration goes to ``thinking`` / ``tool_call`` and never overlaps.

        Raises:
            ValueError: On invalid arguments (checked before spending quota).
            AuthenticationError: Missing/invalid token (401), or a token
                without agentic access (403).
            BadRequestError: Rejected parameters (422).
            RateLimitError: Agentic quota exhausted (429).
            ServerError: Upstream failure (5xx).
            APIError: Connection or transport failure.

        Note:
            An ``error`` event is yielded, not raised — a partial answer may
            already have been streamed and the caller decides what to keep.
            Inspect ``done["answer_truncated"]`` before treating the answer as
            complete.

            Unlike other Reader methods this does **not** auto-retry: each call
            spends a quota unit, and a retried stream would re-bill and re-emit
            an answer from the start.

        Example:
            >>> chunks = []
            >>> for ev in reader.agent_search_stream("KV cache eviction ratio"):
            ...     if ev["event"] == "answer_delta":
            ...         chunks.append(ev["text"])
            >>> answer = "".join(chunks)
        """
        payload = self._build_agent_search_payload(
            query, source, effort, verbose, stream_answer, max_answer_tokens,
            language, top_k, search_type, gl, hl,
        )
        url = f"{self.agent_search_endpoints[source]}/stream"
        headers = {"Authorization": f"Bearer {self.token or ''}"}

        try:
            with requests.post(
                url,
                json=payload,
                headers=headers,
                stream=True,
                timeout=timeout or self.AGENT_SEARCH_TIMEOUT,
            ) as response:
                self._raise_for_agent_status(response)
                logger.info(
                    f"Agentic search stream opened (source={source}, effort={effort})"
                )
                for line in response.iter_lines():
                    if not line:
                        continue
                    if isinstance(line, bytes):
                        line = line.decode("utf-8", errors="replace")
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = _json.loads(line)
                    except ValueError:
                        logger.warning(f"Skipping malformed NDJSON line: {line[:120]}")
                        continue
                    yield event

        except APIError:
            raise
        except requests.exceptions.Timeout:
            raise APIError(
                f"Agentic search timed out after "
                f"{timeout or self.AGENT_SEARCH_TIMEOUT}s. "
                "Try effort='default' or a narrower query."
            )
        except requests.exceptions.RequestException as e:
            raise APIError(f"Agentic search request failed: {str(e)}")

    def agent_search(
        self,
        query: str,
        source: str = "arxiv",
        effort: str = "default",
        verbose: bool = False,
        max_answer_tokens: int = 4096,
        language: Optional[str] = None,
        top_k: Optional[int] = None,
        search_type: Optional[str] = None,
        gl: Optional[str] = None,
        hl: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Run an agentic search and return the complete answer at once.

        Blocking equivalent of :meth:`agent_search_stream`. Prefer the streaming
        variant for anything user-facing — this waits for the full answer
        (typically 8~30s) before returning anything.

        Args:
            query: The question. 1~2000 characters. See
                :meth:`agent_search_stream` for guidance on writing queries.
            source: ``"arxiv"`` (default) or ``"web"``.
            effort: ``"default"`` / ``"high"`` / ``"xhigh"``.
            verbose: When ``True`` the response carries a ``trace`` of the
                tool calls the service made.
            max_answer_tokens: Hard cap on answer length.
            language: Answer language. Defaults to the query's language.
            top_k: ``source="arxiv"`` only — first-round retrieval size, 1~30.
            search_type: ``source="web"`` only — ``"search"`` / ``"scholar"`` /
                ``"news"`` / ``"images"``.
            gl: ``source="web"`` only — Google country code.
            hl: ``source="web"`` only — Google UI language.
            timeout: Request timeout in seconds (default: 180).

        Returns:
            ``{"status", "answer", "sources", "stats", "quota"}``, plus
            ``"trace"`` when ``verbose=True``. ``sources`` entries carry
            ``arxiv_id`` / ``title`` / ``url`` for arXiv and ``url`` / ``title``
            / ``read`` for web. ``quota`` carries ``tier`` / ``used`` /
            ``remaining``. Check ``stats["answer_truncated"]`` before treating
            the answer as complete.

        Raises:
            ValueError: On invalid arguments (checked before spending quota).
            AuthenticationError: Missing/invalid token (401), or a token
                without agentic access (403).
            BadRequestError: Rejected parameters (422).
            RateLimitError: Agentic quota exhausted (429).
            ServerError: Upstream failure (5xx).
            APIError: Connection or transport failure.

        Example:
            >>> result = reader.agent_search("what speedup does DEER report")
            >>> print(result["answer"])
            >>> print(result["quota"]["remaining"], "calls left today")
        """
        payload = self._build_agent_search_payload(
            query, source, effort, verbose, False, max_answer_tokens,
            language, top_k, search_type, gl, hl,
        )
        headers = {"Authorization": f"Bearer {self.token or ''}"}

        try:
            response = requests.post(
                self.agent_search_endpoints[source],
                json=payload,
                headers=headers,
                timeout=timeout or self.AGENT_SEARCH_TIMEOUT,
            )
            self._raise_for_agent_status(response)
            result = response.json() if response.content else {}
            logger.info(
                f"Agentic search completed (source={source}, effort={effort}, "
                f"{len(result.get('sources', []))} sources)"
            )
            return result or {}

        except APIError:
            raise
        except requests.exceptions.Timeout:
            raise APIError(
                f"Agentic search timed out after "
                f"{timeout or self.AGENT_SEARCH_TIMEOUT}s. "
                "Try effort='default' or a narrower query."
            )
        except requests.exceptions.RequestException as e:
            raise APIError(f"Agentic search request failed: {str(e)}")
        except ValueError as e:
            raise APIError(f"Invalid response format: {str(e)}")

    # Sources supported by the unified retrieve endpoint.
    _RETRIEVE_SOURCES = ("arxiv", "biorxiv", "medrxiv")
    # Date filter modes accepted by the upstream service.
    _DATE_SEARCH_TYPES = ("between", "exact", "after", "before")

    def search(
        self,
        query: str,
        size: int = 10,
        offset: int = 0,
        source: str = "arxiv",
        categories: Optional[List[str]] = None,
        authors: Optional[List[str]] = None,
        orgs: Optional[List[str]] = None,
        venue: Optional[Union[str, List[str]]] = None,
        venues: Optional[List[str]] = None,
        venue_year: Optional[Union[int, str]] = None,
        min_citation: Optional[int] = None,
        date_search_type: Optional[str] = None,
        date_str: Optional[Any] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        use_fine_rerank: bool = False,
        top_k: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Semantic search across arXiv / bioRxiv / medRxiv.

        Calls the unified retrieve endpoint
        ``GET https://data.rag.ac.cn/arxiv/?type=retrieve``.

        Args:
            query: Search query string (max 500 characters).
            size: Number of results to return (default: 10, range 1~100).
                Mapped to the upstream ``top_k`` parameter.
            offset: Pagination offset (default: 0, range 0~10000).
            source: Paper source: ``"arxiv"`` (default), ``"biorxiv"``, or
                ``"medrxiv"``.
            categories: Filter by categories (e.g., ``["cs.CV", "cs.CL"]``).
                Filter only, does not affect ranking.
            authors: Author name filter; also influences ranking.
            orgs: Organization name filter; also influences ranking.
            venue: Publication venue filter. Accepts a single name or a list,
                e.g. ``"NeurIPS"`` or ``["NeurIPS", "ICLR"]``. Common aliases are
                matched server-side (``NeurIPS`` also matches ``NIPS`` /
                ``Neural Information Processing Systems``).
            venues: Plural alias for ``venue``; merged with it. Either name works.
            venue_year: Filter by conference / venue year, e.g. ``2025``.
            min_citation: Minimum citation count filter.
            date_search_type: One of ``"between"``, ``"exact"``, ``"after"``,
                ``"before"``. Must be paired with ``date_str``.
            date_str: Date string in ``YYYY`` / ``YYYY-MM`` / ``YYYY-MM-DD``.
                When ``date_search_type="between"``, must be a two-element
                ``[start, end]`` list.
            date_from: Convenience legacy param. When provided without
                ``date_search_type``, it is mapped automatically:
                ``date_from`` + ``date_to`` → ``between``;
                only ``date_from`` → ``after``;
                only ``date_to`` → ``before``.
            date_to: See ``date_from``.
            use_fine_rerank: Whether to enable upstream fine reranking.
                Default: ``False`` (the SDK opts out by default; the upstream
                default is ``True``).
            top_k: Optional explicit ``top_k`` override. If provided, takes
                precedence over ``size``.

        Returns:
            Dictionary with the upstream response shape::

                {
                    "status": "success",
                    "total_count": <int>,
                    "result": [ { "arxiv_id" | "biorxiv_id" | "medrxiv_id": ..., ... }, ... ]
                }

            The ID field on each item depends on ``source``. When venue data is
            available, each item also carries ``"venue"`` and ``"venue_year"``.

        Raises:
            ValueError: On invalid arguments.
            APIError: If the upstream request fails.
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        if source not in self._RETRIEVE_SOURCES:
            raise ValueError(
                f"source must be one of {list(self._RETRIEVE_SOURCES)}"
            )
        effective_top_k = top_k if top_k is not None else size
        if effective_top_k < 1 or effective_top_k > 100:
            raise ValueError("size/top_k must be between 1 and 100")
        if offset < 0 or offset > 10000:
            raise ValueError("offset must be between 0 and 10000")

        # Resolve date filter: prefer explicit date_search_type/date_str.
        resolved_date_type = date_search_type
        resolved_date_str: Any = date_str
        if resolved_date_type is None and (date_from or date_to):
            if date_from and date_to:
                resolved_date_type = "between"
                resolved_date_str = [date_from, date_to]
            elif date_from:
                resolved_date_type = "after"
                resolved_date_str = date_from
            else:
                resolved_date_type = "before"
                resolved_date_str = date_to

        if resolved_date_type is not None:
            if resolved_date_type not in self._DATE_SEARCH_TYPES:
                raise ValueError(
                    f"date_search_type must be one of {list(self._DATE_SEARCH_TYPES)}"
                )
            if resolved_date_str is None:
                raise ValueError(
                    "date_str is required when date_search_type is provided"
                )
            if resolved_date_type == "between":
                if not (
                    isinstance(resolved_date_str, (list, tuple))
                    and len(resolved_date_str) == 2
                ):
                    raise ValueError(
                        "date_str must be [start, end] when date_search_type='between'"
                    )
        elif resolved_date_str is not None:
            raise ValueError(
                "date_search_type is required when date_str is provided"
            )

        # Build params; lists are passed as repeated keys by `requests`.
        params: Dict[str, Any] = {
            "type": "retrieve",
            "query": query,
            "source": source,
            "top_k": effective_top_k,
            "offset": offset,
            # The SDK opts out of fine rerank by default.
            "use_fine_rerank": "true" if use_fine_rerank else "false",
        }
        if self.token:
            params["token"] = self.token

        if categories:
            params["categories"] = list(categories)
        if authors:
            params["authors"] = list(authors)
        if orgs:
            params["orgs"] = list(orgs)
        # Venue filter: accept a single string or list under `venue` (recommended)
        # plus a `venues` plural alias; merge and send under `venue` (the upstream
        # treats both names the same and accepts repeated keys).
        venue_list: List[str] = []
        if venue:
            venue_list.extend([venue] if isinstance(venue, str) else list(venue))
        if venues:
            venue_list.extend([venues] if isinstance(venues, str) else list(venues))
        if venue_list:
            params["venue"] = venue_list
        if venue_year is not None:
            params["venue_year"] = venue_year
        if min_citation is not None:
            params["min_citation"] = min_citation
        if resolved_date_type is not None:
            params["date_search_type"] = resolved_date_type
            params["date_str"] = (
                list(resolved_date_str)
                if isinstance(resolved_date_str, (list, tuple))
                else resolved_date_str
            )

        result = self._make_request(self.arxiv_endpoint, params=params)
        result = result or {"status": "success", "total_count": 0, "result": []}
        logger.info(
            f"Search for '{query}' (source={source}) "
            f"returned {result.get('total_count', 0)} results"
        )
        return result

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
            - github_url: Associated GitHub repository URL (if available)

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

    # ========== Trending Methods ==========

    def trending(
        self,
        days: int = 7,
        limit: int = 30,
    ) -> Dict[str, Any]:
        """
        Get trending arXiv papers.

        Args:
            days: Number of days to look back (1~30). Default: 7
            limit: Maximum number of papers to return. Default: 30

        Returns:
            Dictionary with trending papers including:
            - papers: List of trending paper objects with metadata
            - total: Total number of trending papers available
            - days: The days parameter used
            - generated_at: Timestamp when the trending list was generated

        Raises:
            ValueError: If days or limit are invalid
            APIError: If the request fails
        """
        if days < 1 or days > 30:
            raise ValueError("days must be between 1 and 30")
        if limit < 1 or limit > 100:
            raise ValueError("limit must be between 1 and 100")

        # Use the trending API endpoint (no token required)
        trending_url = "https://api.rag.ac.cn/trending_arxiv_papers/api/trending"
        params: Dict[str, Any] = {
            "days": days,
            "limit": limit,
        }

        result = self._make_request(trending_url, params=params)

        # Extract data from nested response structure
        if result and "data" in result:
            data = result["data"]
            logger.info(f"Retrieved {len(data.get('papers', []))} trending papers for last {days} days")
            return data

        logger.info(f"No trending data available for {days} days")
        return {"papers": [], "total": 0}

    # ========== Social Impact Methods ==========

    def social_impact(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """
        Get social media impact metrics for an arXiv paper (trending signal).

        Args:
            arxiv_id: arXiv ID (e.g., "2409.05592", "2506.00002")

        Returns:
            Dictionary with social impact metrics including:
            - total_tweets: Number of tweets mentioning the paper
            - total_likes: Total likes across social media
            - total_views: Number of views
            - total_replies: Number of replies/comments
            - first_seen_date: When the paper first appeared in trending (ISO format)
            - last_seen_date: Most recent trending activity (ISO format)
            - arxiv_id: The paper ID

            Returns None if no data is found for the paper.

        Raises:
            ValueError: If arxiv_id is invalid
            AuthenticationError: If token is missing or invalid (required for this endpoint)
            APIError: If the request fails
        """
        if not arxiv_id or not arxiv_id.strip():
            raise ValueError("arxiv_id cannot be empty")

        if not self.token:
            raise AuthenticationError(
                "Token is required for social impact queries. "
                "Provide a token when initializing Reader: Reader(token='your_token')"
            )

        params: Dict[str, Any] = {
            "arxiv_id": arxiv_id,
            "token": self.token,
        }
        try:
            # Social impact data is served from the data.rag.ac.cn domain and
            # expects the token in query params for compatibility.
            signal_url = f"{self.base_url}/arxiv/trending_signal"
            result = self._make_request(signal_url, params=params)
            logger.info(f"Retrieved social impact metrics for {arxiv_id}")
            return result or None
        except NotFoundError:
            logger.warning(f"No social impact data found for {arxiv_id}")
            return None

    # ========== bioRxiv / medRxiv Methods ==========

    def biomed_search(
        self,
        query: str,
        source: str = "biorxiv",
        top_k: int = 10,
        authors: Optional[List[str]] = None,
        orgs: Optional[List[str]] = None,
        date_search_type: Optional[str] = None,
        date_str: Optional[Any] = None,
        use_fine_rerank: bool = False,
    ) -> Dict[str, Any]:
        """
        Search bioRxiv / medRxiv preprints.

        Thin wrapper around :meth:`search`; the unified
        ``/arxiv/?type=retrieve`` endpoint serves all sources.

        Args:
            query: Search query string.
            source: ``"biorxiv"`` or ``"medrxiv"`` (default: ``"biorxiv"``).
            top_k: Number of results to return (default: 10).
            authors: Author name filter.
            orgs: Organization name filter.
            date_search_type: ``"between"`` / ``"exact"`` / ``"after"`` /
                ``"before"``.
            date_str: See :meth:`search`.
            use_fine_rerank: Whether to enable upstream fine reranking
                (default: ``False``).

        Returns:
            ``{"status": ..., "total_count": ..., "result": [...]}``

        Note:
            The retrieve endpoint serves metadata and ranking only. Fetch paper
            content with :meth:`biomed_data`, :meth:`raw`, :meth:`section`, or
            :meth:`json` instead.
        """
        if source not in ("biorxiv", "medrxiv"):
            raise ValueError('source must be "biorxiv" or "medrxiv"')

        return self.search(
            query=query,
            size=top_k,
            source=source,
            authors=authors,
            orgs=orgs,
            date_search_type=date_search_type,
            date_str=date_str,
            use_fine_rerank=use_fine_rerank,
        )

    def biomed_data(
        self,
        source_id: str,
        source: str = "biorxiv",
        data_type: str = "metadata",
        section_names: Optional[List[str]] = None,
        roc_num: Optional[int] = None,
        fields: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve a single bioRxiv / medRxiv paper's data.

        Args:
            source_id: Paper DOI, e.g. "10.1101/2021.02.26.433129"
            source: "biorxiv" or "medrxiv" (default: "biorxiv")
            data_type: "metadata" | "section" | "roc" (default: "metadata")
            section_names: List of section names to retrieve (used when data_type="section")
            roc_num: Number of cited-by-reason entries (used when data_type="roc")
            fields: Comma-separated field filter

        Returns:
            Dictionary with paper data

        Raises:
            ValueError: If source or data_type is invalid
            APIError: If the request fails
        """
        if source not in ("biorxiv", "medrxiv"):
            raise ValueError('source must be "biorxiv" or "medrxiv"')
        if data_type not in ("metadata", "section", "roc"):
            raise ValueError('data_type must be "metadata", "section", or "roc"')
        if not source_id or not source_id.strip():
            raise ValueError("source_id cannot be empty")

        url = f"{self.base_url}/{source}/data"
        params: Dict[str, Any] = {
            "source_id": source_id.strip(),
            "type": data_type,
        }
        if section_names:
            params["section_names"] = (
                ",".join(section_names)
                if isinstance(section_names, list)
                else section_names
            )
        if roc_num is not None:
            params["roc_num"] = roc_num
        if fields:
            params["fields"] = fields

        result = self._make_request(url, params=params)
        logger.info(f"biomed_data (source={source}, type={data_type}) for '{source_id}' completed")
        return result or {}

    # ========== Talent (deprecated: use FAClient) ==========

    def fa(self) -> "FAClient":
        """Client for the 1stAuthor domains (talent, law, cases, ...) with this token."""
        from .fa import FAClient
        return FAClient(token=self.token, base_url=f"{self.base_url}/fa", timeout=self.timeout)

    def talent_search(self, query: str, limit: int = 10, offset: int = 0, **_ignored: Any) -> Dict[str, Any]:
        """Deprecated: use ``reader.fa().search("talent", query)``.

        The old ``/talent/search`` endpoint is gone (410). This forwards to the
        1stAuthor talent domain, whose response shape and person IDs differ
        from the old index. Old filters (``semantic``, ``tags``, ``sort``...)
        are ignored.
        """
        warnings.warn(
            'Reader.talent_search is deprecated; use Reader.fa().search("talent", query)',
            DeprecationWarning, stacklevel=2,
        )
        return self.fa().search("talent", query, top_k=limit, offset=offset or None)

    def talent_survey(self, person_id: Any, **_ignored: Any) -> Dict[str, Any]:
        """Deprecated: use ``reader.fa().read("talent", person_id)``.

        The old ``/talent/survey/{id}`` endpoint is gone (410); IDs from the
        old index do not carry over.
        """
        warnings.warn(
            'Reader.talent_survey is deprecated; use Reader.fa().read("talent", person_id)',
            DeprecationWarning, stacklevel=2,
        )
        return self.fa().read("talent", person_id)
