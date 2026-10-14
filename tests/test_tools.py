"""Mocked tests: no network, no Apify token, no spend."""
import json
import sys
import types

import pytest
from pydantic import ValidationError

import open_data_actors.core as core
from open_data_actors import build_run_input, get_tool, list_tools, run_actor

SLUGS = [t.slug for t in list_tools()]


class FakeDataset:
    def __init__(self, rows):
        self.rows = rows

    def list_items(self, limit=None, **_):
        return types.SimpleNamespace(items=self.rows[:limit] if limit else self.rows)


class FakeActor:
    def __init__(self, client, actor_id):
        self.client, self.actor_id = client, actor_id

    def call(self, run_input=None, **kw):
        self.client.calls.append((self.actor_id, run_input, kw))
        return {"status": "SUCCEEDED", "defaultDatasetId": "ds1"}


class FakeClient:
    def __init__(self, rows):
        self.rows, self.calls = rows, []

    def actor(self, actor_id):
        return FakeActor(self, actor_id)

    def dataset(self, _id):
        return FakeDataset(self.rows)


@pytest.fixture
def fake(monkeypatch):
    client = FakeClient([{"i": i} for i in range(100)])
    monkeypatch.setattr(core, "_client", lambda: client)
    return client


def test_registry_has_29_unique_tools():
    tools = list_tools()
    assert len(tools) == 29
    assert len({t.tool_name for t in tools}) == 29
    for t in tools:
        assert t.description and t.input_model is not None
        assert t.actor_id == f"transparent_meteorite/{t.slug}"
        for r in t.required:
            assert r in t.fields


def test_no_secret_fields_exposed():
    for t in list_tools():
        for name in t.fields:
            low = name.lower()
            assert "apikey" not in low and "token" not in low and "webhook" not in low


@pytest.mark.parametrize("slug", SLUGS)
def test_sample_input_validates_and_runs(slug, fake):
    t = get_tool(slug)
    rows = run_actor(slug, max_items=7, **t.sample_input)
    assert len(rows) == 7
    actor_id, run_input, _ = fake.calls[-1]
    assert actor_id == t.actor_id
    for k, v in t.sample_input.items():
        assert run_input[k] == v


@pytest.mark.parametrize("slug", SLUGS)
def test_rejects_unknown_field(slug):
    t = get_tool(slug)
    with pytest.raises(ValidationError):
        build_run_input(slug, **t.sample_input, definitely_not_a_field=1)


@pytest.mark.parametrize("slug", SLUGS)
def test_required_fields_enforced(slug):
    t = get_tool(slug)
    if not t.required:
        pytest.skip("no required fields")
    with pytest.raises(ValidationError):
        build_run_input(slug)


def test_default_cap_applied_when_omitted():
    run_input = build_run_input("sanctions-screening", names=["Acme"])
    assert run_input["maxMatchesPerName"] == 3
    run_input = build_run_input("fmcsa-new-carrier-leads")
    assert run_input["maxResults"] == 5


def test_missing_token_message(monkeypatch):
    monkeypatch.delenv("APIFY_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="APIFY_TOKEN"):
        run_actor("sanctions-screening", names=["x"])


def test_failed_run_raises(monkeypatch):
    class Bad(FakeClient):
        def actor(self, actor_id):
            a = FakeActor(self, actor_id)
            a.call = lambda **kw: {"status": "FAILED", "defaultDatasetId": "d"}
            return a

    monkeypatch.setattr(core, "_client", lambda: Bad([]))
    with pytest.raises(RuntimeError, match="FAILED"):
        run_actor("sanctions-screening", names=["x"])


# ---- adapters -------------------------------------------------------------

def _available(mod):
    try:
        __import__(mod)
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _available("langchain_core"), reason="langchain-core not installed")
def test_langchain_tools(fake):
    from open_data_actors.langchain import get_langchain_tools

    tools = get_langchain_tools()
    assert len(tools) == 29
    names = {t.name for t in tools}
    assert names == {t.tool_name for t in list_tools()}
    tool = next(t for t in tools if t.name == "sanctions_screening")
    out = json.loads(tool.invoke({"names": ["Acme"], "max_items": 3}))
    assert len(out) == 3
    assert fake.calls[-1][1]["names"] == ["Acme"]


@pytest.mark.skipif(not _available("llama_index.core"), reason="llama-index-core not installed")
def test_llamaindex_tools(fake):
    from open_data_actors.llamaindex import get_llamaindex_tools

    tools = get_llamaindex_tools()
    assert len(tools) == 29
    tool = next(t for t in tools if t.metadata.name == "domain_intelligence_lookup")
    out = tool.call(domains=["example.com"], max_items=2)
    assert len(json.loads(out.content)) == 2


@pytest.mark.skipif(not _available("crewai"), reason="crewai not installed")
def test_crewai_tools(fake):
    from open_data_actors.crewai import get_crewai_tools

    tools = get_crewai_tools()
    assert len(tools) == 29
    tool = next(t for t in tools if t.name == "sanctions_screening")
    assert len(json.loads(tool.run(names=["Acme"], max_items=2))) == 2


def test_crewai_adapter_with_stub(monkeypatch, fake):
    """Always runs: exercises the adapter against a minimal stand-in for crewai.tools.BaseTool."""
    if _available("crewai"):
        pytest.skip("real crewai present; covered by test_crewai_tools")

    class BaseTool:
        name = ""
        description = ""
        args_schema = None

        def run(self, **kw):
            return self._run(**kw)

    crewai = types.ModuleType("crewai")
    tools_mod = types.ModuleType("crewai.tools")
    tools_mod.BaseTool = BaseTool
    crewai.tools = tools_mod
    monkeypatch.setitem(sys.modules, "crewai", crewai)
    monkeypatch.setitem(sys.modules, "crewai.tools", tools_mod)
    from open_data_actors.crewai import get_crewai_tools

    tools = get_crewai_tools()
    assert len(tools) == 29
    tool = next(t for t in tools if t.name == "domain_intelligence_lookup")
    assert issubclass(type(tool), BaseTool)
    assert len(json.loads(tool.run(domains=["example.com"], max_items=2))) == 2
