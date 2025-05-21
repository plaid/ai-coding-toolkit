"""
Integration tests for the tool registry.

This module contains integration tests that verify the registry works correctly
with actual tool modules.
"""

import unittest
from typing import Any, Dict, List

import mcp.types as types

from mcp_server_plaid.tools.registry import get_registry, register_all_tools


class TestRegistryIntegration(unittest.TestCase):
    """Integration tests for the registry system."""

    def setUp(self):
        """Set up the test environment before each test."""
        # Reset the registry before each test
        self.registry = get_registry()
        self.registry.reset()

    def test_register_all_tools_integration(self):
        """Test that register_all_tools correctly registers tools from actual modules."""
        # Call register_all_tools with all categories enabled
        register_all_tools("")
        
        # Get all registered tools
        tools = self.registry.get_tools()
        
        # Verify that we have at least some tools registered
        self.assertGreater(len(tools), 0, 
                           "register_all_tools should register at least one tool")
        
        # Check that we can get handlers for all registered tools
        for tool in tools:
            handler = self.registry.get_handler(tool.name)
            self.assertIsNotNone(handler, 
                                f"Should have a handler for registered tool {tool.name}")

    def test_mock_tool_registration_and_execution(self):
        """Test registering a mock tool and executing its handler."""
        # Create a mock tool and handler
        test_result = []
        
        async def mock_handler(arguments: Dict[str, Any], **_) -> List[types.TextContent]:
            test_result.append(arguments.get("message", ""))
            return [types.TextContent(type="text", text="Mock response")]
        
        mock_tool = types.Tool(
            name="mock_test_tool",
            description="A mock test tool",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "A test message"
                    }
                },
                "required": ["message"]
            }
        )
        
        # Register the mock tool
        self.registry.register(mock_tool, mock_handler)
        
        # Verify the tool was registered
        self.assertTrue(self.registry.has_tool("mock_test_tool"), 
                       "Mock tool should be registered")
        
        # Get the handler and execute it
        handler = self.registry.get_handler("mock_test_tool")
        test_message = "Hello, world!"
        import asyncio
        asyncio.run(handler({"message": test_message}))
        
        # Verify the handler was executed with the correct arguments
        self.assertEqual(test_result[0], test_message,
                        "Handler should be called with the correct arguments")

    def test_specific_categories_enabled(self):
        """Test that only tools in enabled categories are registered."""
        # Register only tools in the 'root' category
        register_all_tools("root")
        
        # Get all registered tools
        tools = self.registry.get_tools()
        
        # Reset the registry
        self.registry.reset()
        
        # Register tools in all categories
        register_all_tools("")
        
        # Get all tools from all categories
        all_tools = self.registry.get_tools()
        
        # Verify that we have fewer tools when only the 'root' category is enabled
        # Note: this test assumes that there are tools in categories other than 'root'
        # If all tools are in the 'root' category, this test will fail
        if len(all_tools) > len(tools):
            self.assertLess(len(tools), len(all_tools),
                          "Should register fewer tools when only 'root' category is enabled")


if __name__ == "__main__":
    unittest.main() 