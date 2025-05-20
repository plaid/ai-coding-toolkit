"""
Tool registry for Plaid MCP server.

This module provides a registry system for MCP tools, allowing them to be
registered from various modules and retrieved for use by the MCP server.
"""

import importlib
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Set

import mcp.types as types

logger = logging.getLogger("plaid-mcp-server.tools")


class ToolHandler(Protocol):
    """Protocol for tool handler functions."""

    async def __call__(
            self, arguments: Dict[str, Any], **context: Any
    ) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """
        Handle a tool call with the given arguments and context.

        Args:
            arguments: The arguments passed to the tool
            **context: Additional context, such as clients

        Returns:
            A list of MCP content objects as the tool's response
        """
        ...


class ToolRegistry:
    """
    Registry for MCP tools.

    This class maintains a registry of tools and their handlers, allowing
    tools to be registered from various modules and retrieved for use by
    the MCP server.

    This class implements the Singleton pattern, ensuring that only one
    instance exists throughout the application.
    """

    _instance = None

    def __new__(cls):
        """Ensure only one instance of ToolRegistry exists."""
        if cls._instance is None:
            cls._instance = super(ToolRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the tool registry if not already initialized."""
        if not getattr(self, "_initialized", False):
            self._tools: Dict[str, types.Tool] = {}
            self._handlers: Dict[str, ToolHandler] = {}
            self._initialized = True

    def register(self, tool: types.Tool, handler: ToolHandler) -> None:
        """
        Register a tool and its handler.

        Args:
            tool: The tool definition
            handler: The function that handles calls to this tool
        """
        if tool.name in self._tools:
            logger.warning(f"Tool {tool.name} already registered, overwriting")

        self._tools[tool.name] = tool
        self._handlers[tool.name] = handler
        logger.info(f"Registered tool: {tool.name}")

    def get_tools(self) -> List[types.Tool]:
        """
        Get all registered tools.

        Returns:
            A list of all registered tools
        """
        return list(self._tools.values())

    def get_handler(self, name: str) -> Optional[ToolHandler]:
        """
        Get the handler for a tool by name.

        Args:
            name: The name of the tool

        Returns:
            The handler function, or None if the tool is not registered
        """
        return self._handlers.get(name)

    def has_tool(self, name: str) -> bool:
        """
        Check if a tool is registered.

        Args:
            name: The name of the tool

        Returns:
            True if the tool is registered, False otherwise
        """
        return name in self._tools

    def reset(self) -> None:
        """
        Reset the registry, clearing all registered tools.

        This is primarily useful for testing.
        """
        self._tools = {}
        self._handlers = {}
        logger.info("Registry has been reset")


# Function to get the singleton registry instance
def get_registry() -> ToolRegistry:
    """
    Get the singleton registry instance.

    Returns:
        The singleton ToolRegistry instance
    """
    return ToolRegistry()


def get_enabled_categories(enabled_categories_str: str) -> Set[str]:
    """
    Get the list of enabled tool categories from environment variable.

    If the environment variable is not set, all categories are enabled.

    Returns:
        A set of enabled category names
    """
    if not enabled_categories_str:
        # If no categories specified, enable all
        return set()

    # Parse comma-separated categories
    parsed_categories = {
        category.strip().lower() for category in enabled_categories_str.split(",")
    }
    parsed_categories.add("root")
    return parsed_categories


def is_tool_enabled(tool_path: Path, enabled_categories: Set[str]) -> bool:
    """
    Determine if a tool should be enabled based on its path and enabled categories.

    Args:
        tool_path: Path to the tool file
        enabled_categories: Set of enabled category names

    Returns:
        True if the tool should be enabled, False otherwise
    """
    # If no specific categories are enabled, enable all tools
    if not enabled_categories:
        return True

    # Get the tool's category from its path
    # For tools directly in the tools directory, the category is "root"
    # For tools in subdirectories, the category is the directory name
    parts = tool_path.relative_to(Path(__file__).parent).parts
    if len(parts) <= 1:  # Tool is in the root tools directory
        category = "root"
    else:
        category = parts[0]  # Tool is in a subdirectory

    return category.lower() in enabled_categories


def register_all_tools(enabled_categories: str) -> ToolRegistry:
    """
    Register all available tools from the tools directory.

    This function discovers and imports all tool modules in the tools
    directory and its subdirectories, which will register their tools with the registry.

    If the PLAID_TOOLS_TO_ENABLE environment variable is set, only tools in the
    specified categories will be registered.

    Returns:
        The registry with all tools registered
    """
    # Get the registry instance
    registry_instance = get_registry()

    logger.info(f"Enabled categories: {enabled_categories}")

    # Get the directory containing this file
    tools_dir = Path(__file__).parent

    # Get the list of enabled categories
    enabled_categories = get_enabled_categories(enabled_categories)

    if enabled_categories:
        logger.info(f"Enabled tool categories: {', '.join(enabled_categories)}")
    else:
        logger.info("All tool categories enabled")

    # Find all Python files in the tools directory and subdirectories that start with tool_
    for tool_file in tools_dir.glob("**/tool_*.py"):
        # Skip __init__.py and registry.py
        if tool_file.name in ["__init__.py", "registry.py"]:
            continue

        # Check if the tool is in an enabled category
        if not is_tool_enabled(tool_file, enabled_categories):
            logger.info(f"Skipping disabled tool: {tool_file}")
            continue

        # Create the proper module import path
        module_path = tool_file.relative_to(Path(__file__).parents[2])  # src directory
        module_name = str(module_path.with_suffix("")).replace(os.sep, ".")

        try:
            importlib.import_module(module_name)
            logger.info(f"Imported tool module: {module_name}")
        except Exception as e:
            logger.error(f"Error importing tool module {module_name}: {e}")

    return registry_instance


# Export the registry instance for use by tool modules
registry = get_registry()
