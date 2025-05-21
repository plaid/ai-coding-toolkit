"""
Tests for the tool registry module.

This module contains tests for the ToolRegistry class and related functions in registry.py.
"""

import unittest
from unittest.mock import MagicMock

import mcp.types as types

from mcp_server_plaid.tools.registry import ToolRegistry


class TestToolRegistry(unittest.TestCase):
    """Test cases for the ToolRegistry class."""

    def setUp(self):
        """Set up the test environment before each test."""
        # Reset the registry before each test
        self.registry = ToolRegistry()
        self.registry.reset()

    def test_registry_singleton(self):
        """Test that ToolRegistry implements the Singleton pattern."""
        registry1 = ToolRegistry()
        registry2 = ToolRegistry()
        self.assertIs(registry1, registry2, "ToolRegistry should be a singleton")

    def test_register_tool(self):
        """Test registering a tool and its handler."""
        # Create a mock tool and handler
        mock_tool = types.Tool(
            name="test_tool",
            description="A test tool",
            inputSchema={"type": "object", "properties": {}}
        )
        mock_handler = MagicMock()

        # Register the tool
        self.registry.register(mock_tool, mock_handler)

        # Check that the tool was registered
        self.assertTrue(self.registry.has_tool("test_tool"), "Tool should be registered")
        self.assertEqual(self.registry.get_handler("test_tool"), mock_handler, 
                         "Handler should be retrievable")
        self.assertIn(mock_tool, self.registry.get_tools(), "Tool should be in the list of registered tools")

    def test_register_duplicate_tool(self):
        """Test registering a tool with the same name twice."""
        # Create two mock tools with the same name
        mock_tool1 = types.Tool(
            name="duplicate_tool",
            description="First tool",
            inputSchema={"type": "object", "properties": {}}
        )
        mock_handler1 = MagicMock()

        mock_tool2 = types.Tool(
            name="duplicate_tool",
            description="Second tool",
            inputSchema={"type": "object", "properties": {}}
        )
        mock_handler2 = MagicMock()

        # Register both tools
        self.registry.register(mock_tool1, mock_handler1)
        self.registry.register(mock_tool2, mock_handler2)

        # The second registration should overwrite the first
        self.assertEqual(self.registry.get_handler("duplicate_tool"), mock_handler2,
                         "Second handler should overwrite the first")
        self.assertEqual(len([t for t in self.registry.get_tools() if t.name == "duplicate_tool"]), 1,
                         "Should only be one tool with the given name")

    def test_get_nonexistent_tool(self):
        """Test getting a tool that hasn't been registered."""
        self.assertFalse(self.registry.has_tool("nonexistent_tool"),
                         "Should return False for nonexistent tools")
        self.assertIsNone(self.registry.get_handler("nonexistent_tool"),
                          "Should return None for nonexistent tool handlers")

    def test_reset_registry(self):
        """Test resetting the registry."""
        # Register a tool
        mock_tool = types.Tool(
            name="test_tool",
            description="A test tool",
            inputSchema={"type": "object", "properties": {}}
        )
        mock_handler = MagicMock()
        self.registry.register(mock_tool, mock_handler)

        # Reset the registry
        self.registry.reset()

        # Check that the registry is empty
        self.assertFalse(self.registry.has_tool("test_tool"),
                         "Tool should not be in registry after reset")
        self.assertEqual(len(self.registry.get_tools()), 0,
                         "Registry should be empty after reset")


if __name__ == "__main__":
    unittest.main() 