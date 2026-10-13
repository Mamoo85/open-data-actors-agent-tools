"""Pass the tools to any tool-calling LangChain/LangGraph agent. Requires APIFY_TOKEN and your own LLM."""
from open_data_actors.langchain import get_langchain_tools

tools = [t for t in get_langchain_tools() if t.name in {"sanctions_screening", "domain_intelligence_lookup"}]
print([t.name for t in tools])
# e.g. langgraph.prebuilt.create_react_agent(your_llm, tools)
