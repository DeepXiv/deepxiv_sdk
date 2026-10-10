"""
Tests for the deprecated talent aliases (CLI and Reader), which now forward
to the 1stAuthor talent domain.
"""
import pytest
from unittest import mock
from click.testing import CliRunner

from deepxiv_sdk import Reader
from deepxiv_sdk.cli import main
from deepxiv_sdk.fa import FAClient

from tests.test_fa import FakeResponse, FakeSession, SEARCH_BODY, fake  # noqa: F401


class TestReaderAliases:
    def test_talent_search_forwards_and_warns(self):
        reader = Reader(token="tok")
        with mock.patch.object(FAClient, "search", return_value=SEARCH_BODY) as search:
            with pytest.warns(DeprecationWarning):
                out = reader.talent_search("Geoffrey Hinton", semantic=True, limit=3)
        search.assert_called_once_with("talent", "Geoffrey Hinton", top_k=3, offset=None)
        assert out is SEARCH_BODY

    def test_talent_survey_forwards_and_warns(self):
        reader = Reader(token="tok")
        with mock.patch.object(FAClient, "read", return_value={"data": {}}) as read:
            with pytest.warns(DeprecationWarning):
                reader.talent_survey(15023, refresh=True)
        read.assert_called_once_with("talent", 15023)

    def test_fa_client_shares_token_and_base_url(self):
        c = Reader(token="tok", base_url="http://x/").fa()
        assert (c.token, c.base_url) == ("tok", "http://x/fa")


class TestCliAliases:
    def test_search_alias(self, fake):
        s = fake(FakeResponse(body=SEARCH_BODY))
        r = CliRunner().invoke(main, ["talent", "search", "Geoffrey Hinton", "-s", "--limit", "3", "-t", "tok"])
        assert r.exit_code == 0, r.output
        assert "deprecated" in r.stderr and "deepxiv fa search talent" in r.stderr
        assert "Ignored" in r.stderr and "--semantic" in r.stderr
        assert s.calls[0]["url"].endswith("/v1/talent/search")
        assert s.calls[0]["json"]["top_k"] == 3
        assert "[15023] Geoffrey Hinton" in r.stdout

    def test_search_alias_maps_tags_and_stage_to_filters(self, fake):
        s = fake(
            FakeResponse(body={"search": {"filters": {
                "areas": {"type": "keyword", "ops": ["eq", "any"]},
                "career_stage": {"type": "keyword", "ops": ["eq", "any"]},
            }}}),
            FakeResponse(body=SEARCH_BODY),
        )
        r = CliRunner().invoke(main, ["talent", "search", "--tags", "LLM,Agent",
                                      "--career-stage", "junior", "-t", "tok"])
        assert r.exit_code == 0, r.output
        body = s.calls[1]["json"]
        assert body["query"] == "LLM Agent"
        assert body["filters"] == {"areas": ["LLM", "Agent"], "career_stage": "junior"}

    def test_search_alias_requires_query(self):
        r = CliRunner().invoke(main, ["talent", "search", "-t", "tok"])
        assert r.exit_code == 1

    def test_survey_alias(self, fake):
        s = fake(FakeResponse(body={"data": {"person_id": "15023"}}))
        r = CliRunner().invoke(main, ["talent", "survey", "15023", "-t", "tok"])
        assert r.exit_code == 0, r.output
        assert "deepxiv fa read talent" in r.stderr
        assert s.calls[0]["url"].endswith("/v1/talent/read/15023")
        assert '"person_id": "15023"' in r.stdout

    def test_survey_markdown_reads_full_level(self, fake):
        s = fake(FakeResponse(body={"text": "# Report"}))
        r = CliRunner().invoke(main, ["talent", "survey", "15023", "-f", "markdown", "-t", "tok"])
        assert s.calls[0]["params"] == {"level": "full"}
        assert r.stdout.strip() == "# Report"
