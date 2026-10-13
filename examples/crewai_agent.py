from open_data_actors.crewai import get_crewai_tools

tools = get_crewai_tools()
print([t.name for t in tools][:5])
# e.g. Agent(role="Analyst", goal="...", backstory="...", tools=tools)
