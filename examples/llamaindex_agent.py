from open_data_actors.llamaindex import get_llamaindex_tools

tools = get_llamaindex_tools()
print([t.metadata.name for t in tools][:5])
# e.g. FunctionAgent(tools=tools, llm=your_llm)
