"""
Tests for the server module.

This module contains tests for the server initialization and functionality.
"""

import asyncio
import unittest
from unittest.mock import MagicMock, patch, AsyncMock

import mcp.types as types
from mcp.server import Server, NotificationOptions

from mcp_server_plaid.server import serve


class TestServer(unittest.TestCase):
    """Test cases for the server module."""

    @patch('mcp_server_plaid.server.AskBillClient')
    @patch('mcp_server_plaid.server.plaid_api.PlaidApi')
    @patch('mcp_server_plaid.server.register_all_tools')
    async def async_test_serve_initialization(self, mock_register_all_tools, mock_plaid_api, mock_bill_client):
        """Test that the serve function initializes the server correctly."""
        # Setup mocks
        mock_tool_registry = MagicMock()
        mock_tool = types.Tool(
            name="test_tool",
            description="A test tool",
            inputSchema={"type": "object", "properties": {}}
        )
        mock_tool_registry.get_tools.return_value = [mock_tool]
        mock_tool_registry.has_tool.return_value = True
        
        mock_handler = AsyncMock()
        mock_handler.return_value = [types.TextContent(type="text", text="Test response")]
        mock_tool_registry.get_handler.return_value = mock_handler
        
        mock_register_all_tools.return_value = mock_tool_registry
        
        # Call the function being tested
        server = await serve("test_client_id", "test_secret", "")
        
        # Verify the server was created and has the correct type
        self.assertIsInstance(server, Server)
        
        # Verify the registry was initialized with the correct parameters
        mock_register_all_tools.assert_called_once_with("")
        
        # Don't test too many implementation details that could change
        # Just verify the server can be initialized without errors

    def test_serve_initialization(self):
        """Run the async test."""
        asyncio.run(self.async_test_serve_initialization())
        
    @patch('mcp_server_plaid.server.plaid_api.PlaidApi')
    @patch('mcp_server_plaid.server.register_all_tools')
    @patch('mcp_server_plaid.server.Server')
    async def async_test_serve_unknown_tool(self, mock_server_class, mock_register_all_tools, mock_plaid_api):
        """Test the handler's behavior when calling an unknown tool."""
        # Setup mocks
        mock_tool_registry = MagicMock()
        mock_tool_registry.has_tool.return_value = False
        mock_register_all_tools.return_value = mock_tool_registry
        
        # Mock server and get the call_tool handler
        mock_server = MagicMock()
        mock_server_class.return_value = mock_server
        
        # Capture the handler function
        server = await serve("test_client_id", "test_secret", "")
        
        # Extract the call_tool handler - we need to find which decorator it was registered with
        call_tool_handler = None
        for call in mock_server.call_tool.mock_calls:
            # Extract the function that was decorated
            handler_func = call.args[0] if call.args else None
            if handler_func:
                call_tool_handler = handler_func
                break
                
        self.assertIsNotNone(call_tool_handler, "Could not find call_tool handler")
        
        # Test that calling an unknown tool raises a ValueError
        with self.assertRaises(ValueError) as cm:
            await call_tool_handler("unknown_tool", {})
        
        self.assertEqual(str(cm.exception), "Unknown tool: unknown_tool")
        
    def test_serve_unknown_tool(self):
        """Run the async test."""
        asyncio.run(self.async_test_serve_unknown_tool())
        
    @patch('mcp_server_plaid.server.plaid_api.PlaidApi')
    @patch('mcp_server_plaid.server.register_all_tools')
    @patch('mcp_server_plaid.server.Server')
    async def async_test_serve_no_handler(self, mock_server_class, mock_register_all_tools, mock_plaid_api):
        """Test the handler's behavior when a tool has no handler."""
        # Setup mocks
        mock_tool_registry = MagicMock()
        mock_tool_registry.has_tool.return_value = True
        mock_tool_registry.get_handler.return_value = None
        mock_register_all_tools.return_value = mock_tool_registry
        
        # Mock server and get the call_tool handler
        mock_server = MagicMock()
        mock_server_class.return_value = mock_server
        
        # Capture the handler function
        server = await serve("test_client_id", "test_secret", "")
        
        # Extract the call_tool handler
        call_tool_handler = None
        for call in mock_server.call_tool.mock_calls:
            # Extract the function that was decorated
            handler_func = call.args[0] if call.args else None
            if handler_func:
                call_tool_handler = handler_func
                break
                
        self.assertIsNotNone(call_tool_handler, "Could not find call_tool handler")
        
        # Test that calling a tool with no handler raises a ValueError
        with self.assertRaises(ValueError) as cm:
            await call_tool_handler("test_tool", {})
        
        self.assertEqual(str(cm.exception), "No handler registered for tool: test_tool")
        
    def test_serve_no_handler(self):
        """Run the async test."""
        asyncio.run(self.async_test_serve_no_handler())
        
    @patch('asyncio.run')
    @patch('mcp_server_plaid.server.mcp.server.stdio.stdio_server')
    @patch('mcp_server_plaid.server.serve')
    def test_main_function(self, mock_serve, mock_stdio_server, mock_asyncio_run):
        """Test that the main function works correctly."""
        # Import the main function here to avoid accidentally running it
        from mcp_server_plaid.server import main
        
        # Setup mocks
        mock_server = MagicMock()
        mock_serve.return_value = mock_server
        
        mock_read_stream = MagicMock()
        mock_write_stream = MagicMock()
        mock_stdio_context = MagicMock()
        mock_stdio_context.__aenter__.return_value = (mock_read_stream, mock_write_stream)
        mock_stdio_server.return_value = mock_stdio_context
        
        # Call the main function with test arguments
        args = ["--client-id", "test_client_id", "--secret", "test_secret", "--enabled-categories", "cat1,cat2"]
        with patch('sys.argv', ['server.py'] + args):
            # We're not actually executing main() here, we're just checking 
            # that asyncio.run would be called with a function
            main.callback(client_id="test_client_id", secret="test_secret", enabled_categories="cat1,cat2")
            
        # Verify that asyncio.run was called
        self.assertEqual(mock_asyncio_run.call_count, 1)


if __name__ == "__main__":
    unittest.main() 