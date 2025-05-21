"""
Webhook simulation tools for the Plaid MCP server.

This module implements tools related to simulating webhooks in the Plaid sandbox environment.
"""

from typing import Any, Dict, List

import mcp.types as types
import plaid
from plaid.api import plaid_api
from plaid.model.sandbox_item_fire_webhook_request import SandboxItemFireWebhookRequest
from plaid.model.webhook_type import WebhookType

from mcp_server_plaid.tools.registry import registry

# Tool definition
SIMULATE_WEBHOOK_TOOL = types.Tool(
    name="simulate_webhook",
    description="""Simulate a Plaid webhook event in the sandbox environment to test your application's webhook handling. 
    This tool triggers specific webhook events like transaction updates, account status changes, or transfer notifications. 
    Specify the access_token for the item and the webhook_code representing the event type you want to trigger. 
    <important>
    - Unless user specifies the webhook_code and webhook_type, you MUST use the tool `search_documentation` to find the right
      webhook_code and webhook_type.
    </important>""",
    inputSchema={
        "type": "object",
        "properties": {
            "access_token": {
                "type": "string",
                "description": """A valid Plaid access token for the Item you want to trigger a webhook for. You can 
                obtain this token from a successful /item/public_token/exchange response or using the get_sandbox_access_token 
                tool.""",
            },
            "webhook_code": {
                "type": "string",
                "description": """The specific webhook event code to simulate (e.g., 'DEFAULT_UPDATE', 'SYNC_UPDATES_AVAILABLE', 
                'TRANSACTIONS_REMOVED'). Common codes include 'DEFAULT_UPDATE' for new transactions, 'HISTORICAL_UPDATE' for 
                initial transaction fetch, and 'USER_PERMISSION_REVOKED' for revoked access. You can use the 'ask_bill' tool to 
                find appropriate values.""",
            },
            "webhook_type": {
                "type": "string",
                "description": """The category of webhook to fire (e.g., 'TRANSACTIONS', 'ITEM', 'AUTH'). Must be compatible 
                with the webhook_code. For example, 'DEFAULT_UPDATE' requires 'TRANSACTIONS' type. You can use the 'ask_bill' tool 
                to find appropriate values.""",
                "default": "",
            },
        },
        "required": ["access_token", "webhook_code"],
    },
)


# Tool handler
async def handle_simulate_webhook(
        arguments: Dict[str, Any], *, plaid_client: plaid_api.PlaidApi, **_
) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle the simulate_webhook tool request.

    Args:
        arguments: The tool arguments containing access_token, webhook_code, and optional webhook_type
        plaid_client: The Plaid API client

    Returns:
        A list of content elements with the webhook simulation result
    """
    access_token = arguments["access_token"]
    webhook_code = arguments["webhook_code"]
    webhook_type = arguments.get("webhook_type", "")

    try:
        # Build the webhook request
        webhook_request = SandboxItemFireWebhookRequest(
            access_token=access_token,
            webhook_code=webhook_code,
        )

        # Only set webhook_type if provided
        if webhook_type:
            webhook_request.webhook_type = WebhookType(webhook_type)

        # Fire the webhook
        response = plaid_client.sandbox_item_fire_webhook(webhook_request)

        # Extract response data
        webhook_fired = response.get("webhook_fired", False)
        status_code = response.get("status_code")

        return [
            types.TextContent(
                type="text",
                text=f"Webhook fired: {webhook_fired}, Status code: {status_code}",
            )
        ]
    except plaid.ApiException as e:
        # Enhanced error handling with more details
        error_msg = f"Error simulating webhook: {str(e)}"
        status_code = getattr(e, "status", None)
        if status_code:
            error_msg += f" (Status code: {status_code})"
        return [types.TextContent(type="text", text=error_msg)]
    except Exception as e:
        # Catch any other unexpected errors
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]


# Register the tool with the registry
registry.register(SIMULATE_WEBHOOK_TOOL, handle_simulate_webhook)
