"""
Tests for the 1stAuthor client (deepxiv_sdk.fa) and the `deepxiv fa` commands.
"""
import json
from unittest import mock

import pytest
from click.testing import CliRunner

from deepxiv_sdk.cli import main
from deepxiv_sdk.fa import (
    FAClient,
    FAError,
    FilterError,
    build_filters,
    error_from_response,
    quota_from_headers,
)


class FakeResponse:
    def __init__(self, status=200, body=None, headers=None, lines=None, text=None):
        self.status_code = status
        self._body = body
        self.headers = {"Content-Type": "application/json", **(headers or {})}
        self._lines = lines or []
        self.text = text if text is not None else (json.dumps(body) if body is not None else "")

    def json(self):
        if self._body is None:
            raise ValueError("no json")
        return self._body

    def iter_lines(self, decode_unicode=False):
        for line in self._lines:
            yield line.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FakeSession:
    """Records calls; answers from a queue of FakeResponses."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    def _next(self, method, url, **kw):
        self.calls.append({"method": method, "url": url, **kw})
        return self.responses.pop(0)

    def request(self, method, url, **kw):
        return self._next(method, url, **kw)

    def post(self, url, **kw):
        return self._next("POST", url, **kw)


QUOTA_HEADERS = {
    "X-DeepXiv-Quota-Cost": "2",
    "X-DeepXiv-Quota-Used": "10",
    "X-DeepXiv-Quota-Daily-Limit": "1000",
    "X-DeepXiv-Quota-Remaining": "990",
}

SEARCH_BODY = {
    "domain": "talent",
    "query": "Geoffrey Hinton",
    "hits": [{
        "id": "15023",
        "score": 8.0,
        "brief": {
            "person_id": "15023",
            "name_line": "Geoffrey Hinton · University of Toronto",
            "role": "Emeritus Professor",
            "h_index": 109,
            "citations_all": 68707,
            "areas": ["Deep Learning", "Neural Networks"],
        },
    }],
    "warnings": [],
    "meta": {"quota": {"cost": 2, "used": 10, "daily_limit": 1000, "remaining": 990}},
}

SPEC_BODY = {
    "id": "talent",
    "search": {"filters": {
        "org": {"type": "keyword", "ops": ["eq", "any"]},
        "h_index": {"type": "integer", "ops": ["eq", "range"]},
        "has_profile": {"type": "bool", "ops": ["eq"]},
        "names": {"type": "text", "ops": ["text"]},
    }},
}


def ndjson(*events):
    return [json.dumps(e, ensure_ascii=False) for e in events]


# ---- filters ------------------------------------------------------------------

class TestBuildFilters:
    schema = SPEC_BODY["search"]["filters"]

    def test_all_operators(self):
        out = build_filters(
            ["org=清华大学,北京大学", "h_index>=20", "h_index<=80", "has_profile=yes", "names~Wen"],
            self.schema,
        )
        assert out == {
            "org": ["清华大学", "北京大学"],
            "h_index": {"gte": 20, "lte": 80},
            "has_profile": True,
            "names": {"text": "Wen"},
        }

    def test_range_syntax(self):
        assert build_filters(["h_index=10..30"], self.schema) == {"h_index": {"gte": 10, "lte": 30}}

    def test_unknown_field(self):
        with pytest.raises(FilterError, match="unknown filter field 'bogus'"):
            build_filters(["bogus=1"], self.schema)

    def test_operator_not_allowed(self):
        with pytest.raises(FilterError, match="not allowed"):
            build_filters(["org>=3"], self.schema)

    def test_bad_type(self):
        with pytest.raises(FilterError, match="expected an integer"):
            build_filters(["h_index>=lots"], self.schema)

    def test_unparseable(self):
        with pytest.raises(FilterError, match="can't parse"):
            build_filters(["just words"], None)

    def test_without_schema_coerces_ints(self):
        assert build_filters(["year=2024", "q=abc"], None) == {"year": 2024, "q": "abc"}


# ---- errors and quota ---------------------------------------------------------

class TestErrors:
    def test_deepxiv_detail_shape(self):
        e = error_from_response(403, {}, json.dumps({
            "detail": "Agentic search requires a registered account key. SDK auto-registered tokens are not eligible."
        }))
        assert e.status == 403
        assert e.needs_registered_key

    def test_fa_error_shape(self):
        e = error_from_response(400, {}, json.dumps({
            "error": {"code": "invalid_request", "message": "unknown extra 'x'",
                      "details": {"extras": ["papers"]}},
            "request_id": "req_1",
        }))
        assert (e.code, e.message, e.request_id) == ("invalid_request", "unknown extra 'x'", "req_1")
        assert e.details == {"extras": ["papers"]}
        assert not e.needs_registered_key

    def test_retry_after_and_non_json(self):
        e = error_from_response(429, {"Retry-After": "3"}, "<html>busy</html>")
        assert e.retry_after == 3.0
        assert "busy" in e.message

    def test_quota_headers(self):
        q = quota_from_headers({**QUOTA_HEADERS, "X-DeepXiv-Agent-Tier": "free",
                                "X-DeepXiv-Agent-Remaining": "299"})
        assert q["general"] == {"cost": 2, "used": 10, "daily_limit": 1000, "remaining": 990}
        assert q["agent"]["tier"] == "free" and q["agent"]["remaining"] == 299


# ---- client -------------------------------------------------------------------

class TestClient:
    def test_search_request(self):
        s = FakeSession(FakeResponse(body=SEARCH_BODY, headers=QUOTA_HEADERS))
        c = FAClient(token="tok", session=s)
        out = c.search("talent", "Geoffrey Hinton", top_k=3, filters={"org": "x"}, fields="head")
        call = s.calls[0]
        assert call["method"] == "POST"
        assert call["url"] == "https://data.rag.ac.cn/fa/v1/talent/search"
        assert call["json"] == {"query": "Geoffrey Hinton", "top_k": 3, "filters": {"org": "x"}, "fields": "head"}
        assert call["headers"]["Authorization"] == "Bearer tok"
        assert out["hits"][0]["id"] == "15023"
        assert c.last_quota["general"]["remaining"] == 990

    def test_read_uses_read_path_with_params(self):
        s = FakeSession(FakeResponse(body={"data": {}}))
        FAClient(token="tok", session=s).read("talent", 15023, level="full", section="教育")
        assert s.calls[0]["url"].endswith("/v1/talent/read/15023")
        assert s.calls[0]["params"] == {"level": "full", "section": "教育"}

    def test_read_html_returns_text(self):
        s = FakeSession(FakeResponse(headers={"Content-Type": "text/html; charset=utf-8"},
                                     text="<!doctype html>"))
        out = FAClient(token="tok", session=s).read("talent", 15023, format="html")
        assert out["text"] == "<!doctype html>"

    def test_ask_paths(self):
        assert FAClient._ask_path(None, stream=False) == "/v1/ask"
        assert FAClient._ask_path("law", stream=True) == "/v1/law/ask/stream"

    def test_error_raised(self):
        s = FakeSession(FakeResponse(status=401, body={"detail": "Invalid or inactive token"}))
        with pytest.raises(FAError) as ei:
            FAClient(token="bad", session=s).domains()
        assert ei.value.status == 401

    def test_429_with_short_retry_after_is_retried_once(self):
        s = FakeSession(
            FakeResponse(status=429, body={"detail": "busy"}, headers={"Retry-After": "0"}),
            FakeResponse(body={"domains": []}),
        )
        with mock.patch("deepxiv_sdk.fa.time.sleep") as sleep:
            assert FAClient(token="tok", session=s).domains() == {"domains": []}
        sleep.assert_called_once_with(0.0)
        assert len(s.calls) == 2

    def test_stream_yields_events(self):
        s = FakeSession(FakeResponse(lines=ndjson({"event": "start"}, {"event": "done"}) + [""]))
        events = list(FAClient(token="tok", session=s).ask_stream("q", "talent"))
        assert [e["event"] for e in events] == ["start", "done"]
        assert s.calls[0]["json"] == {"query": "q"}


# ---- CLI ----------------------------------------------------------------------

@pytest.fixture
def fake(monkeypatch):
    """Install a FakeSession into every FAClient the CLI creates."""
    holder = {}

    def install(*responses):
        session = FakeSession(*responses)
        holder["session"] = session
        real_init = FAClient.__init__

        def init(self, token=None, base_url="https://data.rag.ac.cn/fa", timeout=120.0, session_=None):
            real_init(self, token=token, base_url=base_url, timeout=timeout, session=session)

        monkeypatch.setattr(FAClient, "__init__", init)
        return session

    return install


def run(*args):
    return CliRunner().invoke(main, ["fa", *args, "-t", "tok"])


class TestFaCli:
    def test_search_text(self, fake):
        fake(FakeResponse(body=SEARCH_BODY))
        r = run("search", "talent", "Geoffrey Hinton")
        assert r.exit_code == 0, r.output
        assert "[15023] Geoffrey Hinton" in r.stdout
        assert "h-index: 109" in r.stdout
        assert "💳 cost 2 · 990/1000" in r.stderr
        assert "💳" not in r.stdout

    def test_search_json_stdout_is_pure(self, fake):
        fake(FakeResponse(body=SEARCH_BODY))
        r = run("search", "talent", "Geoffrey Hinton", "--json")
        assert json.loads(r.stdout)["hits"][0]["id"] == "15023"

    def test_search_filters_validated_against_spec(self, fake):
        s = fake(FakeResponse(body=SPEC_BODY), FakeResponse(body=SEARCH_BODY))
        r = run("search", "talent", "RAG", "-F", "org=University of Toronto", "-F", "h_index>=30", "--head")
        assert r.exit_code == 0, r.output
        assert s.calls[1]["json"]["filters"] == {"org": "University of Toronto", "h_index": {"gte": 30}}
        assert s.calls[1]["json"]["fields"] == "head"

    def test_search_bad_filter_exits_2(self, fake):
        fake(FakeResponse(body=SPEC_BODY))
        r = run("search", "talent", "RAG", "-F", "bogus=1")
        assert r.exit_code == 2
        assert "unknown filter field" in r.stderr

    def test_read_prints_data(self, fake):
        fake(FakeResponse(body={"data": {"person_id": "15023"}, "meta": {}}))
        r = run("read", "talent", "15023", "--level", "brief")
        assert r.exit_code == 0
        assert json.loads(r.stdout) == {"person_id": "15023"}

    def test_read_full_prints_markdown(self, fake):
        fake(FakeResponse(body={"text": "# Geoffrey Hinton", "meta": {}}))
        r = run("read", "talent", "15023", "--level", "full")
        assert r.stdout.strip() == "# Geoffrey Hinton"

    def test_read_error_lists_allowed_values(self, fake):
        fake(FakeResponse(status=400, body={"error": {
            "code": "invalid_request", "message": "unknown extra 'nope'",
            "details": {"extras": ["papers", "network"]}}}))
        r = run("read", "talent", "15023", "--extra", "nope")
        assert r.exit_code == 1
        assert "extras: papers, network" in r.stderr

    def test_ask_sdk_token_gets_register_hint(self, fake):
        fake(FakeResponse(status=403, body={"detail": "Agentic search requires a registered account key. "
                                                      "SDK auto-registered tokens are not eligible."}))
        r = run("ask", "who works on RAG", "--domain", "talent")
        assert r.exit_code == 1
        assert "https://data.rag.ac.cn/register" in r.stderr
        assert r.stdout == ""

    def test_ask_stream_routes_answer_and_sources(self, fake):
        s = fake(FakeResponse(
            headers={"X-DeepXiv-Agent-Tier": "free", "X-DeepXiv-Agent-Remaining": "3"},
            lines=ndjson(
                {"event": "route", "domain": "talent"},
                {"event": "start"},
                {"event": "answer_start"},
                {"event": "answer_delta", "delta": "Geoffrey Hinton "},
                {"event": "answer_delta", "delta": "[talent:15023]"},
                {"event": "sources", "sources": [{"id": "15023", "name_line": "Geoffrey Hinton"}]},
                {"event": "done"},
            )))
        r = run("ask", "deep learning pioneers")
        assert r.exit_code == 0, r.output
        assert s.calls[0]["url"].endswith("/v1/ask/stream")
        assert r.stdout == "Geoffrey Hinton [talent:15023]\n"
        assert "routed to talent" in r.stderr
        assert "[15023] Geoffrey Hinton" in r.stderr
        assert "3 agentic call(s) left" in r.stderr

    def test_ask_stream_error_event_exits_nonzero(self, fake):
        fake(FakeResponse(lines=ndjson(
            {"event": "start"},
            {"event": "answer_delta", "delta": "partial"},
            {"event": "error", "code": "upstream_error", "message": "model failed", "refunded": True},
        )))
        r = run("ask", "q", "-d", "law", "--effort", "high")
        assert r.exit_code == 1
        assert r.stdout == "partial\n"
        assert "upstream_error: model failed (quota refunded)" in r.stderr

    def test_ask_params_are_typed_into_the_body(self, fake):
        s = fake(FakeResponse(body={"answer": "ok", "sources": {"laws": [], "cases": []}}))
        r = run("ask", "q", "-d", "law", "--no-stream", "-p", "scope=law", "-p", "top_k=5",
                "-p", 'filters={"stance": "positive"}')
        assert r.exit_code == 0, r.output
        assert s.calls[0]["json"] == {"query": "q", "scope": "law", "top_k": 5,
                                      "filters": {"stance": "positive"}}
        assert "Sources" not in r.stderr

    def test_ask_sources_use_name_field(self, fake):
        fake(FakeResponse(body={"answer": "a", "sources": {"people": [{"id": "3426", "name": "Yann LeCun"}]}}))
        r = run("ask", "q", "-d", "talent", "--no-stream")
        assert "[3426] Yann LeCun" in r.stderr

    def test_ask_no_stream(self, fake):
        s = fake(FakeResponse(body={"answer": "done.", "sources": [], "meta": {}}))
        r = run("ask", "q", "-d", "law", "--no-stream")
        assert r.exit_code == 0
        assert s.calls[0]["url"].endswith("/v1/law/ask")
        assert r.stdout == "done.\n"

    def test_concurrency_429(self, fake):
        fake(FakeResponse(status=429, body={"detail": "too many concurrent agentic calls"},
                          headers={"Retry-After": "120"}))
        r = run("ask", "q", "--no-stream")
        assert r.exit_code == 1
        assert "Retry in 120s" in r.stderr

    def test_daily_limit_429(self, fake):
        fake(FakeResponse(status=429, body={"detail": "Daily limit reached"}))
        r = run("search", "talent", "x")
        assert r.exit_code == 1
        assert "daily usage limit" in r.stderr

    def test_whoami(self, fake):
        fake(FakeResponse(body={"source": "sdk", "name": "deepxiv_x",
                                "quota": {"used": 1, "daily_limit": 1000, "remaining": 999},
                                "agent": None, "agent_note": "ask requires a registered account key"}))
        r = run("whoami")
        assert "general: 1/1000 used" in r.stdout
        assert "registered account key" in r.stdout


class TestNoBundledKeys:
    def test_package_has_no_fa_key(self):
        import pathlib
        import deepxiv_sdk
        root = pathlib.Path(deepxiv_sdk.__file__).parent
        for path in root.rglob("*.py"):
            assert "fa_live_" not in path.read_text("utf-8"), path
