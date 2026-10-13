"""LlamaIndex adapter. Requires ``pip install open-data-actors-tools[llamaindex]``."""
from typing import List

from ._common import args_model, make_callable
from .core import list_tools


def get_llamaindex_tools() -> List["FunctionTool"]:  # noqa: F821
    from llama_index.core.tools import FunctionTool

    return [
        FunctionTool.from_defaults(
            fn=make_callable(s), name=s.tool_name, description=s.agent_description, fn_schema=args_model(s)
        )
        for s in list_tools()
    ]
