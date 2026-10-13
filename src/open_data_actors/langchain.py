"""LangChain adapter. Requires ``pip install open-data-actors-tools[langchain]``."""
from typing import List

from ._common import args_model, make_callable
from .core import list_tools


def get_langchain_tools() -> List["StructuredTool"]:  # noqa: F821
    from langchain_core.tools import StructuredTool

    return [
        StructuredTool.from_function(
            func=make_callable(s), name=s.tool_name, description=s.agent_description, args_schema=args_model(s)
        )
        for s in list_tools()
    ]
