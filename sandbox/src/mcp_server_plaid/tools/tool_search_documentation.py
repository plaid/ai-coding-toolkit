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


def _escape_md_brackets(text: str) -> str:
    """Escape characters that would break a markdown link's title text."""
    return text.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def _format_sources(sources: List[Dict[str, Any]]) -> str:
    """Format AskBill source metadata as a deduplicated markdown bullet list."""
    seen_urls = set()
    lines = []
    for source in sources:
        url = source.get("url", "")
        title = source.get("title", "") or url
        if url and url in seen_urls:
            continue
        if url:
            seen_urls.add(url)
            if title != url:
                lines.append(f"- [{_escape_md_brackets(title)}](<{url}>)")
            else:
                lines.append(f"- <{url}>")
        elif title:
            lines.append(f"- {_escape_md_brackets(title)}")
    return "\n".join(lines)


# Tool handler
async def handle_search_documentation(
        arguments: Dict[str, Any], *, bill_client: AskBillClient, **_
) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    response = await bill_client.ask_question(question=arguments["question"])
    answer = str(response["answer"])
    sources = response.get("sources") or []
    formatted_sources = _format_sources(sources)
    if formatted_sources:
        answer = f"{answer.rstrip()}\n\n## Sources\n{formatted_sources}"
    return [types.TextContent(type="text", text=answer)]


registry.register(SEARCH_DOCUMENTATION_TOOL, handle_search_documentation)
