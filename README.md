# AI Coding Tookit for Plaid

A comprehensive toolkit designed to accelerate Plaid integration development using AI coding assistants. This repository provides sandbox MCP tools (mock data generation, documentation search capabilities, etc.) and product-specific guides to help developers build Plaid integrations faster and more efficiently with AI assistance.

## Repository Structure

- `/sandbox`: Contains a sandbox MCP server implementation that helps developers integrate with Plaid more quickly by providing mock data and sandbox API access.
- `/rules`: Contains product-specific guides that can be used either as direct prompts for AI assistants or as Cursor rules to accelerate Plaid integration development.

## Sandbox MCP Server

The sandbox MCP server located in `/sandbox` directory provides a set of tools to facilitate faster integration with Plaid. It offers:

- Mock financial data generation
- Plaid documentation search
- Sandbox API access tokens
- Webhook simulation

This sandbox environment allows developers to test their Plaid integrations without using real financial data.

### Key Features

- **Generate mock financial data** for testing purposes
- **Search Plaid documentation** for relevant API information
- **Obtain sandbox access tokens** for testing
- **Simulate webhooks** to test application handling

### Getting Started

To use the sandbox MCP server, navigate to the `/sandbox` directory and follow the instructions in its README.

```bash
cd sandbox
# Follow instructions in sandbox/README.md for setup and usage
```

## Rules for AI Integration

The `/rules` directory contains comprehensive guides for various Plaid products and features. These guides can be used in two ways:

1. **Direct Prompts**: Copy the content directly into your conversations with AI assistants to provide them with specialized knowledge about Plaid products.

2. **Cursor Rules**: Import them as Cursor rules to enable your AI coding assistant to automatically understand Plaid's integration patterns and best practices.

Using these rules significantly accelerates development by giving AI models the context they need to generate code for Plaid integrations.

> [!WARNING]
These guides are designed to be used for the purpose of building a sample Plaid integration with the use of AI coding tools. You are solely responsible for ensuring the correctness, legality, security, privacy, and compliance of your own app and Plaid integration. This guide is provided under the MIT license and is provided as-is and without warranty of any kind.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
