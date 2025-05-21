"""
Documentation-related tools for the Plaid MCP server.

This module implements tools related to Plaid documentation and Q&A.
"""

from typing import Any, Dict, List

import mcp.types as types
import plaid
from plaid.api import plaid_api
from plaid.model.auth_get_request import AuthGetRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.sandbox_public_token_create_request_options import SandboxPublicTokenCreateRequestOptions

from mcp_server_plaid.tools.registry import registry

# Tool definition
GET_SANDBOX_ACCESS_TOKEN_TOOL = types.Tool(
    name="get_sandbox_access_token",
    description="""Get a workable access token for the Plaid sandbox environment. So that we can
    test the integration with sandbox mocked data. For a success response, the tool will return both
    access_token and item_id. 
    <important>
    BEFORE you call this tool:
    - You MUST ask the user if they would like to provide the webhook url to listen to events update.
    - You MUST ask the user if they would like to provide the customized account data to be associated with the access token. 
      If they do, you MUST use the tool `get_mock_data_prompt` to generate the mock data with the format we accept.
    </important>
    """,
    inputSchema={
        "type": "object",
        "properties": {
            "initial_products": {
                "type": "string",
                "description": """The plaid products to use for the access token, separated by commas. 
                You should not pass `balance` in this array. The Balance product is fetched on demand 
                so it doesn't require initialization through Link. Instead, you initialize with the 
                other products you need (for example, auth, identity, or transactions)""",
            },
            "webhook": {
                "type": "string",
                "description": """The webhook to use for listening to events from the sandbox environment. This is 
                optional.""",
                "default": "",
            },
            "customized_account_data": {
                "type": "string",
                "description": """The customized test used account data to be associated with the access token. User can 
                use the tool `get_mock_data_prompt` to generate the mock data with the format we accept. You should always
                ask the user if they want to use customized account data for the test. If they want to, use this tool to 
                generate the mock data and pass the generated data to this tool. """,
                "default": "",
            },
        },
        "required": ["initial_products"],
    },
)


# Tool handler
async def handle_get_sandbox_access_token(
        arguments: Dict[str, Any], *, plaid_client: plaid_api.PlaidApi, **_
) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    try:
        # Create options with conditional assignments
        options_kwargs = {}

        # Only add webhook if it was provided and not empty
        if arguments.get("webhook"):
            options_kwargs["webhook"] = arguments.get("webhook")

        # Add username/password override only if customized data is provided
        if arguments.get("customized_account_data"):
            options_kwargs["override_username"] = "user_custom"
            options_kwargs["override_password"] = arguments.get(
                "customized_account_data"
            )

        options = SandboxPublicTokenCreateRequestOptions(**options_kwargs)

        # Convert comma-separated products to list of Products
        product_list = [
            Products(p.strip()) for p in arguments["initial_products"].split(",")
        ]

        pt_request = SandboxPublicTokenCreateRequest(
            institution_id="ins_109508",
            initial_products=product_list,
            options=options,
        )

        # Get public token
        pt_response = plaid_client.sandbox_public_token_create(pt_request)

        # Exchange for access token
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=pt_response["public_token"]
        )
        exchange_response = plaid_client.item_public_token_exchange(exchange_request)

        text = f"Access Token: {exchange_response['access_token']}\nItem ID: {exchange_response['item_id']}"

        if "transfer" in arguments.get("initial_products"):
            # Call auth_get_request to get the accounts
            auth_request = AuthGetRequest(
                access_token=exchange_response["access_token"]
            )
            auth_response = plaid_client.auth_get(auth_request)

            # Get the accounts
            accounts = auth_response["accounts"]
            text += f"\nAccounts: {accounts}"

        # Return formatted response
        return [types.TextContent(type="text", text=text)]
    except plaid.ApiException as e:
        error_code = getattr(e, "code", "unknown")
        error_message = getattr(e, "body", str(e))
        return [
            types.TextContent(type="text", text=f"Error {error_code}: {error_message}")
        ]


# Register the tool with the registry
registry.register(GET_SANDBOX_ACCESS_TOKEN_TOOL, handle_get_sandbox_access_token)
