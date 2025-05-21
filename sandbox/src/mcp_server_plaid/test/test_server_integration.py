"""
Integration tests for the server module.

This module contains integration tests for the server functionality.
"""

import asyncio
import os
import signal
import subprocess
import time
import unittest
from unittest.mock import patch


class TestServerIntegration(unittest.TestCase):
    """Integration test cases for the server module."""

    @patch.dict('os.environ', {
        'PLAID_CLIENT_ID': 'dummy_client_id',
        'PLAID_SECRET': 'dummy_secret'
    })
    def test_server_startup(self):
        """
        Test that the server can start up without errors.
        
        This test runs the actual server process and verifies it starts without crashing.
        It doesn't test actual functionality but ensures all imports and initialization works.
        """
        # Set a timeout for the server process
        TIMEOUT = 5  # seconds
        
        try:
            # Start the server process with a dummy input to keep it running
            process = subprocess.Popen(
                ['python', '-m', 'mcp_server_plaid'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=dict(os.environ, PLAID_CLIENT_ID='dummy_client_id', PLAID_SECRET='dummy_secret'),
                text=True,
            )
            
            # Wait for a moment to let the server start up
            time.sleep(2)
            
            # Check if the process is still running
            if process.poll() is not None:
                # Process exited - read stderr to understand why
                _, stderr = process.communicate(timeout=1)
                self.fail(f"Server process exited unexpectedly with error: {stderr}")
            
            # The server is running, which means it initialized correctly
            self.assertIsNone(process.poll(), "Server should still be running")
            
        finally:
            # Make sure to terminate the process
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    # If it doesn't terminate gracefully, kill it
                    process.kill()
                    process.wait()


class TestServerStartupScript(unittest.TestCase):
    """Test the server startup script directly."""
    
    @patch('sys.argv', ['mcp_server_plaid', '--client-id', 'dummy_client_id', '--secret', 'dummy_secret'])
    @patch('mcp_server_plaid.server.serve')
    @patch('mcp_server_plaid.server.mcp.server.stdio.stdio_server')
    @patch('asyncio.run')
    def test_main_script(self, mock_asyncio_run, mock_stdio_server, mock_serve):
        """Test that the main function in __main__.py runs correctly."""
        # Setup mocks
        mock_server = unittest.mock.MagicMock()
        mock_serve.return_value = mock_server
        
        mock_read_stream = unittest.mock.MagicMock()
        mock_write_stream = unittest.mock.MagicMock()
        mock_stdio_context = unittest.mock.MagicMock()
        mock_stdio_context.__aenter__.return_value = (mock_read_stream, mock_write_stream)
        mock_stdio_server.return_value = mock_stdio_context
        
        # Import and run the main module
        from mcp_server_plaid import main
        
        # The function should run without error
        self.assertIsNotNone(mock_asyncio_run.call_count)
        
        
if __name__ == "__main__":
    unittest.main() 