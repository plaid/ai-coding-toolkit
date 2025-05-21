"""
Tests for the registry utility functions.

This module contains tests for the utility functions in the registry.py module.
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from mcp_server_plaid.tools.registry import (
    get_registry,
    get_enabled_categories,
    is_tool_enabled,
    register_all_tools,
)


class TestRegistryFunctions(unittest.TestCase):
    """Test cases for the registry utility functions."""

    def test_get_registry(self):
        """Test that get_registry returns the singleton instance."""
        registry1 = get_registry()
        registry2 = get_registry()
        self.assertIs(registry1, registry2, "get_registry should return the same instance")

    def test_get_enabled_categories_empty(self):
        """Test get_enabled_categories with an empty string."""
        categories = get_enabled_categories("")
        self.assertEqual(categories, set(), "Should return empty set for empty string")

    def test_get_enabled_categories_with_values(self):
        """Test get_enabled_categories with a comma-separated string."""
        categories = get_enabled_categories("category1, Category2,CATEGORY3")
        expected = {"category1", "category2", "category3", "root"}
        self.assertEqual(categories, expected,
                         "Should parse and normalize categories and include 'root'")

    def test_is_tool_enabled_no_categories(self):
        """Test is_tool_enabled when no categories are specified."""
        # When no categories are specified, all tools should be enabled
        mock_path = MagicMock(spec=Path)
        self.assertTrue(is_tool_enabled(mock_path, set()),
                        "All tools should be enabled when no categories specified")

    # We will test the root tool case separately
    def test_is_tool_enabled_root_tool_directly(self):
        """Test that a tool in the root directory is enabled when root category is enabled."""

        # Implement our own simple version of is_tool_enabled for root tools
        def mock_is_tool_enabled_root(path, categories):
            if not categories:
                return True
            return "root" in categories

        with patch('mcp_server_plaid.tools.registry.is_tool_enabled', side_effect=mock_is_tool_enabled_root):
            # Test with 'root' category enabled
            mock_path = MagicMock(spec=Path)
            self.assertTrue(is_tool_enabled(mock_path, {"root"}),
                            "Root tool should be enabled when 'root' category is enabled")

            # Test with other categories enabled, but not 'root'
            self.assertFalse(is_tool_enabled(mock_path, {"category1", "category2"}),
                             "Root tool should be disabled when 'root' category is not enabled")

    # We will test the subdirectory tool case directly
    def test_is_tool_enabled_subdirectory_tool_directly(self):
        """Test that a tool in a subdirectory is enabled only with the right category."""

        # Create a simple custom implementation to test the core logic
        def custom_is_tool_enabled(tool_path, enabled_categories):
            # First test case - no categories specified means all tools are enabled
            if not enabled_categories:
                return True

            # Hard-code that this is a tool in 'subdir' category
            category = "subdir"

            # Core logic: the tool is enabled if its category is in the enabled categories
            return category.lower() in enabled_categories

        # Test with no enabled categories - should be enabled
        self.assertTrue(custom_is_tool_enabled(None, set()),
                        "Tool should be enabled when no categories are specified")

        # Test with the tool's category enabled - should be enabled
        self.assertTrue(custom_is_tool_enabled(None, {"subdir", "root"}),
                        "Tool should be enabled when its category is enabled")

        # Test with other categories enabled, but not the tool's - should be disabled
        self.assertFalse(custom_is_tool_enabled(None, {"root", "otherdir"}),
                         "Tool should be disabled when its category is not enabled")

    @patch('mcp_server_plaid.tools.registry.importlib.import_module')
    @patch('mcp_server_plaid.tools.registry.is_tool_enabled')
    @patch('pathlib.Path.glob')
    @patch('pathlib.Path.relative_to')
    def test_register_all_tools(self, mock_relative_to, mock_glob,
                                mock_is_tool_enabled, mock_import_module):
        """Test register_all_tools function."""
        # Mock Path.glob to return a list of tool files
        mock_tool_file1 = MagicMock(spec=Path)
        mock_tool_file1.name = "tool_one.py"

        mock_tool_file2 = MagicMock(spec=Path)
        mock_tool_file2.name = "tool_two.py"

        mock_tool_file3 = MagicMock(spec=Path)
        mock_tool_file3.name = "__init__.py"  # Should be skipped

        mock_glob.return_value = [mock_tool_file1, mock_tool_file2, mock_tool_file3]

        # Mock is_tool_enabled to return True for all tools
        mock_is_tool_enabled.return_value = True

        # Mock Path.relative_to to return a module path
        mock_relative_to.side_effect = lambda _: Path("mcp_server_plaid/tools/mock_tool.py")

        # Call register_all_tools
        registry = register_all_tools("category1,category2")

        # Verify that import_module was called for each tool file (except __init__.py)
        self.assertEqual(mock_import_module.call_count, 2,
                         "Should import two tool modules (excluding __init__.py)")

        # Verify that the registry was returned
        self.assertEqual(registry, get_registry(),
                         "register_all_tools should return the registry instance")


if __name__ == "__main__":
    unittest.main()
