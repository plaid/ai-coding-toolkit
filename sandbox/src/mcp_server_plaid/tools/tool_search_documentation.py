"""
Documentation-related tools for the Plaid MCP server.

This module implements tools related to Plaid documentation and Q&A.
"""

from typing import Any, Dict, List

import mcp.types as types

from mcp_server_plaid.clients.bill import AskBillClient
from mcp_server_plaid.tools.registry import registry

# Tool definition
SEARCH_DOCUMENTATION_TOOL = types.Tool(
    name="search_documentation",
    description="""Search Plaid documentation for relevant information. 
    <important>
    - You MUST use this tool when the user asks questions about Plaid's products, or API endpoints.
    - You MUST use this tool when you run into any coding issues or errors you cannot resolve and need
      more information about the API endpoints or products.
    </important>""",
    inputSchema={
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "question to ask in natural language, please be specific and concise",
            }
        },
        "required": ["question"],
    },
)


# Tool handler
async def handle_search_documentation(
        arguments: Dict[str, Any], *, bill_client: AskBillClient, **_
) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    response = await bill_client.ask_question(question=arguments["question"])
    return [types.TextContent(type="text", text=str(response["answer"]))]


registry.register(SEARCH_DOCUMENTATION_TOOL, handle_search_documentation)
