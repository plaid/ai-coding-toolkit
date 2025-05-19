from . import server_test


def main():
    """Main entry point for the package."""
    server_test.main()


# Optionally expose other important items at package level
__all__ = ["main", "server"]
