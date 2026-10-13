"""CrewAI adapter (``crewai.tools.BaseTool`` subclasses). Requires the ``[crewai]`` extra."""
from typing import List, Type

from pydantic import BaseModel

from ._common import args_model, make_callable
from .core import list_tools


def get_crewai_tools() -> List["BaseTool"]:  # noqa: F821
    from crewai.tools import BaseTool

    tools = []
    for s in list_tools():
        run = make_callable(s)

        def _run(self, _run=run, **kwargs):
            return _run(**kwargs)

        cls = type(
            "".join(p.title() for p in s.slug.split("-")) + "Tool",
            (BaseTool,),
            {
                "__module__": __name__,
                "__annotations__": {"name": str, "description": str, "args_schema": Type[BaseModel]},
                "name": s.tool_name,
                "description": s.agent_description,
                "args_schema": args_model(s),
                "_run": _run,
            },
        )
        tools.append(cls())
    return tools
