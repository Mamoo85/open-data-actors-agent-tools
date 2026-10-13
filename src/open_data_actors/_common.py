import json
from typing import Any, Callable

from pydantic import Field, create_model

from .core import ToolSpec, run_actor


def make_callable(spec: ToolSpec) -> Callable[..., str]:
    def _run(**kwargs: Any) -> str:
        max_items = kwargs.pop("max_items", None)
        extra = {"max_items": max_items} if max_items else {}
        rows = run_actor(spec.slug, **extra, **kwargs)
        return json.dumps(rows, default=str)

    _run.__name__ = spec.tool_name
    return _run


def args_model(spec: ToolSpec):
    """Input model plus a ``max_items`` result limit."""
    return create_model(
        spec.input_model.__name__ + "Args",
        __base__=spec.input_model,
        max_items=(int, Field(25, ge=1, le=500, description="Max result rows returned to the agent.")),
    )
