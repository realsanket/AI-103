# Register this blueprint by adding the following line of code 
# to your entry point file.  
# app.register_functions(blueprint) 
# 
# Please refer to https://aka.ms/azure-functions-python-blueprints


import azure.functions as func
import logging

blueprint = func.Blueprint()


@blueprint.mcp_tool_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    tool_name="hello_mcp",
    description="Hello world.",
    toolProperties="[]",
)
def mcp_trigger(context) -> None:
    return "Hello I am MCPTool!"