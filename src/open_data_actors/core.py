"""Core: tool registry (generated from the actor catalog) and ``run_actor``."""
from __future__ import annotations

import inspect
import json
import os
from datetime import timedelta
from functools import lru_cache
from importlib import resources
from typing import Any, List, Literal, Optional, Type

from pydantic import BaseModel, ConfigDict, Field, create_model

OWNER = "transparent_meteorite"
DEFAULT_MAX_ITEMS = 25
DEFAULT_TIMEOUT_SECS = 300

_PY = {"string": str, "integer": int, "number": float, "boolean": bool, "any": Any}


class ToolSpec(BaseModel):
    """One agent tool == one public Apify actor."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    slug: str
    tool_name: str
    title: str
    description: str
    url: str
    required: List[str]
    fields: dict
    caps: dict
    sample_input: dict
    input_model: Optional[Type[BaseModel]] = None

    @property
    def actor_id(self) -> str:
        return f"{OWNER}/{self.slug}"

    @property
    def agent_description(self) -> str:
        return (
            f"{self.description} Runs the public Apify actor {self.actor_id}. "
            f"Pay-per-result on the caller's Apify account. Results are capped by max_items."
        )


def _py_type(f: dict):
    t = f["type"]
    if "enum" in f and t == "string":
        return Literal[tuple(f["enum"])]  # type: ignore[valid-type]
    if t == "array":
        return List[_PY.get(f.get("items", "any"), Any)]
    if t == "object":
        return dict
    return _PY[t]


def _build_model(spec: dict) -> Type[BaseModel]:
    fields: dict = {}
    for name, f in spec["fields"].items():
        ann = _py_type(f)
        kw: dict = {"description": f.get("description", "")}
        if f["type"] in ("integer", "number"):
            if "minimum" in f:
                kw["ge"] = f["minimum"]
            if "maximum" in f:
                kw["le"] = f["maximum"]
        if name in spec["required"]:
            fields[name] = (ann, Field(..., **kw))
        else:
            fields[name] = (Optional[ann], Field(None, **kw))
    name = "".join(p.title() for p in spec["slug"].split("-")) + "Input"
    model = create_model(name, __config__=ConfigDict(extra="forbid"), **fields)
    model.__doc__ = spec["description"]
    return model


@lru_cache(maxsize=1)
def load_registry() -> dict:
    """Return {slug: ToolSpec}."""
    raw = json.loads(resources.files("open_data_actors").joinpath("registry.json").read_text(encoding="utf-8"))
    out = {}
    for t in raw["tools"]:
        out[t["slug"]] = ToolSpec(**t, input_model=_build_model(t))
    return out


def list_tools() -> List[ToolSpec]:
    return list(load_registry().values())


def get_tool(slug_or_name: str) -> ToolSpec:
    reg = load_registry()
    key = slug_or_name.replace("_", "-")
    if key not in reg:
        raise KeyError(f"unknown tool {slug_or_name!r}; available: {sorted(reg)}")
    return reg[key]


def _client():
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        raise RuntimeError("Set the APIFY_TOKEN environment variable (https://console.apify.com/account/integrations).")
    from apify_client import ApifyClient

    return ApifyClient(token)


def _get(obj: Any, *names: str) -> Any:
    for n in names:
        if isinstance(obj, dict) and n in obj:
            return obj[n]
        if hasattr(obj, n):
            return getattr(obj, n)
    return None


def build_run_input(slug: str, **inputs: Any) -> dict:
    """Validate ``inputs`` against the tool's model and apply the small default caps."""
    spec = get_tool(slug)
    model = spec.input_model(**{k: v for k, v in inputs.items() if v is not None})
    run_input = model.model_dump(exclude_none=True)
    for key, value in spec.caps.items():
        run_input.setdefault(key, value)
    return run_input


def run_actor(
    slug: str, *, max_items: int = DEFAULT_MAX_ITEMS, timeout_secs: int = DEFAULT_TIMEOUT_SECS, **inputs: Any
) -> List[dict]:
    """Run ``transparent_meteorite/<slug>`` and return at most ``max_items`` dataset rows.

    Inputs are validated; unknown keys raise ``pydantic.ValidationError``. Needs ``APIFY_TOKEN``.
    Billing is pay-per-result on your Apify account, so keep caps small while experimenting.
    """
    spec = get_tool(slug)
    run_input = build_run_input(slug, **inputs)
    client = _client()
    actor = client.actor(spec.actor_id)
    params = inspect.signature(actor.call).parameters
    kwargs: dict = {"run_input": run_input}
    if "run_timeout" in params:  # apify-client >= 3
        kwargs["run_timeout"] = timedelta(seconds=timeout_secs)
        if "max_items" in params:
            kwargs["max_items"] = max_items
    elif "timeout_secs" in params:  # apify-client 1.x / 2.x
        kwargs["timeout_secs"] = timeout_secs
    run = actor.call(**kwargs)
    if not run:
        raise RuntimeError(f"actor run for {spec.actor_id} returned no run object")
    status = _get(run, "status")
    status = getattr(status, "value", status)
    if status not in (None, "SUCCEEDED"):
        raise RuntimeError(f"actor {spec.actor_id} finished with status {status}")
    dataset_id = _get(run, "defaultDatasetId", "default_dataset_id")
    page = client.dataset(dataset_id).list_items(limit=max_items)
    return list(page.items)[:max_items]
