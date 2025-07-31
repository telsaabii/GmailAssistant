import inspect
from langchain_google_community import GmailToolkit

toolkit = GmailToolkit()

tools = toolkit.get_tools()
tools_dict = {tool.name: tool for tool in tools}

print("Available Gmail tools:")
for tool_name, tool in tools_dict.items():
    print(f"  - {tool_name}: {tool.description}")
    if hasattr(tool, 'args_schema') and tool.args_schema:
        print(f"    Args: {tool.args_schema.schema()}")
    print()