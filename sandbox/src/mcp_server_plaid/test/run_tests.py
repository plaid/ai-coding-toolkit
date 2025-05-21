#!/usr/bin/env python
"""
Test runner for MCP Server Plaid tests.

This script discovers and runs all tests in the test directory.
"""

import unittest
import sys
from pathlib import Path


def run_tests() -> bool:
    """
    Discover and run all tests in the test directory.
    
    Returns:
        True if all tests passed, False otherwise
    """
    # Get the directory containing this file
    test_dir = Path(__file__).parent
    
    # Discover all tests
    loader = unittest.TestLoader()
    suite = loader.discover(str(test_dir), pattern="test_*.py")
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return True if all tests passed, False otherwise
    return result.wasSuccessful()


if __name__ == "__main__":
    # Run the tests and exit with the appropriate exit code
    success = run_tests()
    sys.exit(0 if success else 1) 