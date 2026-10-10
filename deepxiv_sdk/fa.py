"""
Client for the 1stAuthor vertical domains (talent, law, cases, trials, ...),
served through the deepxiv data service at ``https://data.rag.ac.cn/fa``.

The deepxiv backend proxies every call to 1stAuthor's fa-api with its own
partner key, so callers only ever send their deepxiv token. Paths and bodies
are the same as fa-api's ``/v1/*``.
"""
from __future__ import annotations

import json
import logging
import re
import time
from typing import Any, Dict, Iterable, Iterator, List, Optional

import requests

from .reader import APIError

logger = logging.getLogger(__name__)

DEFAULT_FA_BASE_URL = "https://data.rag.ac.cn/fa"
REGISTER_URL = "https://data.rag.ac.cn/register"
# A Retry-After longer than this is surfaced as an error instead of waited out.
MAX_RETRY_AFTER = 30.0


class FAError(APIError):
    """A non-2xx answer from ``/fa`` (or an ``error`` event inside an ask stream).

    The service answers in two shapes: deepxiv's own ``{"detail": "..."}``
    (auth, daily quota, ask eligibility) and fa-api's passthrough
    ``{"error": {"code", "message", "details"}}``. Both land here.
    """

    def __init__(
        self,
        message: str,
        *,
        status: Optional[int] = None,
        code: Optional[str] = None,
        details: Any = None,
        retry_after: Optional[float] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code
        self.details = details
        self.retry_after = retry_after
        self.request_id = request_id

    @property
    def needs_registered_key(self) -> bool:
        """True when the call is reserved for registered keys (SDK tokens get 403)."""
        return self.status == 403 and "registered account key" in self.message.lower()

    def __str__(self) -> str:
        head = f"HTTP {self.status}" if self.status else "error"
        if self.code:
            head += f" {self.code}"
        s = f"{head}: {self.message}"
        if self.request_id:
            s += f" (request_id {self.request_id})"
        return s


def _retry_after(headers: Any) -> Optional[float]:
    value = headers.get("Retry-After") if headers is not None else None
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        return None


def error_from_response(status: int, headers: Any, text: str) -> FAError:
    """Build an :class:`FAError` from either error shape; tolerate non-JSON bodies."""
    message = (text or "").strip()[:300] or f"HTTP {status}"
    code = None
    details = None
    request_id = headers.get("X-FA-Request-Id") if headers is not None else None
    try:
        body = json.loads(text) if text else {}
    except ValueError:
        body = {}
    if isinstance(body, dict):
        err = body.get("error")
        detail = body.get("detail")
        if isinstance(err, dict):
            code = err.get("code")
            message = err.get("message") or message
            details = err.get("details")
        elif isinstance(err, str):
            message = err
        elif isinstance(detail, str):
            message = detail
        elif detail is not None:
            # FastAPI validation errors: a list of {loc, msg, type}.
            message = json.dumps(detail, ensure_ascii=False)[:300]
        request_id = body.get("request_id") or request_id
    return FAError(
        message,
        status=status,
        code=code,
        details=details,
        retry_after=_retry_after(headers),
        request_id=request_id,
    )


def _int(value: Any) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def quota_from_headers(headers: Any) -> Dict[str, Any]:
    """Pull the deepxiv quota headers into ``{"general": {...}, "agent": {...}}``.

    ``general`` mirrors ``meta.quota`` (cost/used/daily_limit/remaining);
    ``agent`` is the agentic pool that ask draws on (tier/daily_limit/used/remaining).
    Either is omitted when its headers are absent.
    """
    out: Dict[str, Any] = {}
    if headers is None:
        return out
    general = {
        key: _int(headers.get(f"X-DeepXiv-Quota-{name}"))
        for key, name in (("cost", "Cost"), ("used", "Used"),
                          ("daily_limit", "Daily-Limit"), ("remaining", "Remaining"))
    }
    if any(v is not None for v in general.values()):
        out["general"] = general
    agent = {
        key: _int(headers.get(f"X-DeepXiv-Agent-{name}"))
        for key, name in (("daily_limit", "Daily-Limit"), ("used", "Used"),
                          ("remaining", "Remaining"))
    }
    tier = headers.get("X-DeepXiv-Agent-Tier")
    if tier or any(v is not None for v in agent.values()):
        agent["tier"] = tier
        out["agent"] = agent
    return out


# ---- --filter syntax ----------------------------------------------------------
#
# Same syntax as the 1stAuthor CLI, so docs and examples carry over:
#
#     k=v          equals                  {"k": "v"}
#     k=a,b        any of                  {"k": ["a", "b"]}
#     k>=n  k<=n   bound                   {"k": {"gte": n}} / {"k": {"lte": n}}
#     k=n..m       inclusive range         {"k": {"gte": n, "lte": m}}
#     k~text       full-text match         {"k": {"text": "text"}}

_FILTER_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_.]*)\s*(>=|<=|=|~)\s*(.*)$", re.S)


class FilterError(ValueError):
    """A ``--filter`` expression that can't be parsed or isn't allowed by the domain."""


def _coerce(field: str, ftype: Optional[str], raw: str) -> Any:
    raw = raw.strip()
    if ftype in ("integer", "int"):
        try:
            return int(raw)
        except ValueError:
            raise FilterError(f"{field}: expected an integer, got {raw!r}") from None
    if ftype in ("number", "float"):
        try:
            return float(raw)
        except ValueError:
            raise FilterError(f"{field}: expected a number, got {raw!r}") from None
    if ftype in ("bool", "boolean"):
        low = raw.lower()
        if low in ("1", "true", "yes", "y"):
            return True
        if low in ("0", "false", "no", "n"):
            return False
        raise FilterError(f"{field}: expected true/false, got {raw!r}")
    if ftype is None and re.fullmatch(r"-?\d+", raw):
        return int(raw)
    return raw


def parse_filter(expr: str):
    """Return ``(field, op, value)`` with ``op`` in eq | any | range | text."""
    m = _FILTER_RE.match(expr)
    if not m or m.group(3) == "":
        raise FilterError(
            f"can't parse filter {expr!r}; use k=v, k=a,b, k>=n, k<=n, k=n..m or k~text"
        )
    field, sym, raw = m.group(1), m.group(2), m.group(3).strip()
    if sym == "~":
        return field, "text", {"text": raw}
    if sym == ">=":
        return field, "range", {"gte": raw}
    if sym == "<=":
        return field, "range", {"lte": raw}
    if ".." in raw:
        lo, _, hi = raw.partition("..")
        rng = {}
        if lo.strip():
            rng["gte"] = lo.strip()
        if hi.strip():
            rng["lte"] = hi.strip()
        if not rng:
            raise FilterError(f"{field}: empty range")
        return field, "range", rng
    if "," in raw:
        return field, "any", [v.strip() for v in raw.split(",") if v.strip()]
    return field, "eq", raw


def _ops_allow(ops: List[str], op: str) -> bool:
    if op == "range":
        return any(o in ops for o in ("range", "gte", "lte"))
    return op in ops


def build_filters(exprs: Iterable[str], schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Merge ``--filter`` expressions into one filter dict.

    ``schema`` is ``spec["search"]["filters"]`` from :meth:`FAClient.spec`; it
    types the values and rejects unknown fields and operators. Pass ``None``
    to skip validation (values are then coerced by shape only).
    """
    out: Dict[str, Any] = {}
    for expr in exprs:
        field, op, value = parse_filter(expr)
        fdef = None
        if schema is not None:
            fdef = schema.get(field)
            if fdef is None:
                allowed = ", ".join(sorted(schema)) or "none"
                raise FilterError(f"unknown filter field {field!r}; this domain has: {allowed}")
            ops = list(fdef.get("ops") or [])
            if ops and not _ops_allow(ops, op):
                raise FilterError(
                    f"{field}: operator {op!r} not allowed (allowed: {', '.join(ops)})"
                )
        ftype = (fdef or {}).get("type")
        if op == "range":
            value = {k: _coerce(field, ftype, v) for k, v in value.items()}
            prev = out.get(field)
            if isinstance(prev, dict) and set(prev) & {"gte", "lte"}:
                prev.update(value)
                continue
        elif op == "any":
            value = [_coerce(field, ftype, v) for v in value]
        elif op == "eq":
            value = _coerce(field, ftype, value)
        if field in out:
            raise FilterError(f"{field}: given twice")
        out[field] = value
    return out


# ---- client -------------------------------------------------------------------

def _clean(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}


class FAClient:
    """Thin client for ``https://data.rag.ac.cn/fa``.

    Every method returns the decoded JSON body. Responses carry
    ``meta.quota`` ({cost, used, daily_limit, remaining}); the raw quota
    headers of the last call are in :attr:`last_quota`.

    Billing: search/read/facets/resolve draw on the general daily limit at
    1stAuthor's prices; ``domains``, ``spec`` and ``whoami`` are free. ``ask``
    draws on the agentic quota and needs a registered account key — the
    token the SDK auto-registers gets a 403 (:attr:`FAError.needs_registered_key`).

    Example:
        >>> fa = FAClient(token="your_deepxiv_token")
        >>> hits = fa.search("talent", "文继荣", top_k=3)
        >>> person = fa.read("talent", hits["hits"][0]["id"], level="brief")
    """

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = DEFAULT_FA_BASE_URL,
        timeout: float = 120.0,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.last_quota: Dict[str, Any] = {}

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _send(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = self.base_url + path
        backed_off = False
        network_retried = False
        while True:
            try:
                resp = self.session.request(
                    method, url, json=json_body, params=params,
                    headers=self._headers(), timeout=self.timeout,
                )
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                # Only GETs are retried: a POST that landed would be charged twice.
                if method == "GET" and not network_retried:
                    network_retried = True
                    continue
                raise FAError(f"could not reach {url}: {e}") from e
            if resp.status_code == 429 and not backed_off:
                wait = _retry_after(resp.headers)
                if wait is not None and wait <= MAX_RETRY_AFTER:
                    backed_off = True
                    logger.info(f"429 from {path}; retrying in {wait}s")
                    time.sleep(wait)
                    continue
            self.last_quota = quota_from_headers(resp.headers)
            if resp.status_code >= 400:
                raise error_from_response(resp.status_code, resp.headers, resp.text)
            content_type = resp.headers.get("Content-Type", "")
            if content_type.startswith(("text/html", "text/markdown", "text/plain")):
                # format=html (and friends) return the rendered page itself.
                return {"text": resp.text, "content_type": content_type,
                        "meta": {"quota": self.last_quota.get("general")}}
            try:
                body = resp.json()
            except ValueError as e:
                raise FAError(
                    f"non-JSON response (HTTP {resp.status_code}): {resp.text[:200]!r}",
                    status=resp.status_code,
                ) from e
            return body if isinstance(body, dict) else {"data": body}

    # -- free ------------------------------------------------------------------

    def domains(self) -> Dict[str, Any]:
        """GET /v1/domains — every domain with status and corpus size. Free."""
        return self._send("GET", "/v1/domains")

    def spec(self, domain: str) -> Dict[str, Any]:
        """GET /v1/{domain} — filters, read levels/extras, views, prices, quickstart. Free."""
        return self._send("GET", f"/v1/{domain}")

    def whoami(self) -> Dict[str, Any]:
        """GET /v1/whoami — token source, general quota, and agentic quota for registered keys."""
        return self._send("GET", "/v1/whoami")

    # -- general daily limit ---------------------------------------------------

    def search(
        self,
        domain: str,
        query: str,
        *,
        top_k: Optional[int] = None,
        offset: Optional[int] = None,
        mode: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        fields: Optional[str] = None,
        sort: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """POST /v1/{domain}/search.

        ``filters`` uses fa's filter dict, e.g. ``{"org": "清华大学", "h_index": {"gte": 30}}``
        (see :func:`build_filters`). ``fields="head"`` returns richer hits at a higher price.
        """
        body = _clean({
            "query": query, "top_k": top_k, "offset": offset, "mode": mode,
            "filters": filters or None, "fields": fields, "sort": sort,
        })
        return self._send("POST", f"/v1/{domain}/search", json_body=body)

    def read(
        self,
        domain: str,
        doc_id: Any,
        *,
        level: Optional[str] = None,
        extra: Optional[str] = None,
        format: Optional[str] = None,
        **params: Any,
    ) -> Dict[str, Any]:
        """GET /v1/{domain}/read/{id}?level=brief|detail|full[&extra=…][&format=json|md|html].

        Extra keyword arguments go through as query parameters
        (e.g. ``section="教育"`` with ``level="full"``, or ``n=3`` with ``extra="source"``).
        """
        query = _clean({"level": level, "extra": extra, "format": format, **params})
        return self._send("GET", f"/v1/{domain}/read/{doc_id}", params=query)

    def read_many(
        self,
        domain: str,
        ids: Iterable[Any],
        *,
        level: Optional[str] = None,
        extra: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """POST /v1/{domain}/read — several ids in one call."""
        body = _clean({"ids": [str(i) for i in ids], "level": level, "extra": extra,
                       "params": params or None})
        return self._send("POST", f"/v1/{domain}/read", json_body=body)

    def doc(self, domain: str, doc_id: Any, view: Optional[str] = None, **params: Any) -> Dict[str, Any]:
        """GET /v1/{domain}/doc/{id}?view=… — read one named view (see ``spec()["views"]``)."""
        query = _clean({"view": view, **params})
        return self._send("GET", f"/v1/{domain}/doc/{doc_id}", params=query)

    def facets(self, domain: str, field: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """GET /v1/{domain}/facets?field=… — value counts for a filter field."""
        return self._send("GET", f"/v1/{domain}/facets",
                          params=_clean({"field": field, "limit": limit}))

    def resolve(self, names: Iterable[str]) -> Dict[str, Any]:
        """POST /v1/talent/resolve — person names to in-corpus talent ids (≤50 per call)."""
        return self._send("POST", "/v1/talent/resolve", json_body={"names": list(names)})

    # -- agentic quota (registered keys only) ----------------------------------

    @staticmethod
    def _ask_path(domain: Optional[str], stream: bool) -> str:
        base = f"/v1/{domain}/ask" if domain else "/v1/ask"
        return base + ("/stream" if stream else "")

    def ask(
        self,
        query: str,
        domain: Optional[str] = None,
        *,
        effort: Optional[str] = None,
        **extra: Any,
    ) -> Dict[str, Any]:
        """POST /v1/{domain}/ask, or /v1/ask to let fa pick the domain. Blocks until done."""
        body = _clean({"query": query, "effort": effort, **extra})
        return self._send("POST", self._ask_path(domain, stream=False), json_body=body)

    def ask_stream(
        self,
        query: str,
        domain: Optional[str] = None,
        *,
        effort: Optional[str] = None,
        **extra: Any,
    ) -> Iterator[Dict[str, Any]]:
        """POST /v1/{domain}/ask/stream — yield one dict per NDJSON event.

        Order: ``route`` (only without a domain) → ``start`` → ``answer_start`` →
        ``answer_delta``… → ``sources`` → ``done``. A failure after the stream
        opened arrives as ``{"event": "error", "code", "message", "refunded"}``
        with HTTP 200 — callers must check for it. The agentic quota headers
        are in :attr:`last_quota` once the first event is yielded.
        """
        url = self.base_url + self._ask_path(domain, stream=True)
        body = _clean({"query": query, "effort": effort, **extra})
        headers = self._headers()
        headers["Accept"] = "application/x-ndjson"
        try:
            resp = self.session.post(url, json=body, headers=headers,
                                     timeout=self.timeout, stream=True)
        except requests.exceptions.RequestException as e:
            raise FAError(f"could not reach {url}: {e}") from e
        with resp:
            self.last_quota = quota_from_headers(resp.headers)
            if resp.status_code >= 400:
                raise error_from_response(resp.status_code, resp.headers, resp.text)
            try:
                for line in resp.iter_lines(decode_unicode=False):
                    if not line:
                        continue
                    try:
                        event = json.loads(line.decode("utf-8", "replace"))
                    except ValueError:
                        yield {"event": "warning", "message": f"unparseable stream line: {line[:200]!r}"}
                        continue
                    if isinstance(event, dict):
                        yield event
            except requests.exceptions.RequestException as e:
                raise FAError(f"stream interrupted: {e}") from e
