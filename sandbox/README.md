# mcp-server-plaid: A Plaid MCP server

## Overview

A Model Context Protocol server for facilitating integration with Plaid. This server provides tools to generate mock financial data, search Plaid documentation, and interact with sandbox APIs for testing purposes.

### Tools

1. `get_mock_data_prompt`
   - Return prompt to generate customized mock financial data for testing

2. `search_documentation`
   - Search Plaid documentation for relevant information about products or API endpoints
   - Returns: Detailed information from Plaid's documentation

3. `get_sandbox_access_token`
   - Obtain a working access token for the Plaid sandbox environment
   - Returns: Access token and item ID for testing with sandbox mocked data

4. `simulate_webhook`
   - Simulate a Plaid webhook event in the sandbox environment
   - Useful for testing your application's webhook handling
   - Returns: Webhook fired status and status code

## Configuration

### Obtaining API Credentials

1. Sign in to your [Plaid Developer Dashboard](https://developer.plaid.com) account
2. Navigate to **Developers** → **[Keys](https://dashboard.plaid.com/developers/keys)**
3. Locate your **sandbox credentials** as illustrated in the screenshot below.

>[!Important]
All `PLAID_CLIENT_ID` and `PLAID_SECRET` references in the following MCP configuration use **sandbox credentials**.


<img width="890" alt="image" src="https://github.com/user-attachments/assets/d0c0030a-93c9-4d3f-bb21-1f12b5c1e8e9" />



### Usage with Claude Desktop

Add this to your `claude_desktop_config.json`:

<details>
<summary>Using uvx</summary>

```json
{
  "mcpServers": {
    "plaid": {
      "command": "uvx",
      "args": [
        "mcp-server-plaid",
        "--client-id",
        "YOUR_PLAID_CLIENT_ID",
        "--secret",
        "YOUR_PLAID_SECRET"
      ]
    }
  }
}
```
</details>

<details>
<summary>Using pip installation</summary>

```json
{
  "mcpServers": {
    "plaid": {
      "command": "python",
      "args": [
        "-m",
        "mcp_server_plaid",
        "--client-id",
        "YOUR_PLAID_CLIENT_ID",
        "--secret",
        "YOUR_PLAID_SECRET"
      ]
    }
  }
}
```
</details>

### Usage with Cursor
For quick installation, use the one-click installation button 

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/install-mcp?name=plaid&config=eyJjb21tYW5kIjoidXZ4IG1jcC1zZXJ2ZXItcGxhaWQiLCJlbnYiOnsiUExBSURfQ0xJRU5UX0lEIjoiQUREX1l)

For manual installation, add the following JSON block to Cursor MCP config file,
<details>
<summary>Using uvx</summary>

```json
{
  "mcpServers": {
    "plaid": {
      "command": "uvx",
      "args": [
        "mcp-server-plaid",
        "--client-id",
        "YOUR_PLAID_CLIENT_ID",
        "--secret",
        "YOUR_PLAID_SECRET"
      ]
    }
  }
}
```
</details>

<details>
<summary>Using pip installation</summary>

```json
{
  "mcpServers": {
    "plaid": {
      "command": "python",
      "args": [
        "-m",
        "mcp_server_plaid",
        "--client-id",
        "YOUR_PLAID_CLIENT_ID",
        "--secret",
        "YOUR_PLAID_SECRET"
      ]
    }
  }
}
```
</details>

### Usage with VS Code

For quick installation, use one of the one-click installation buttons below,

[![Install with UV in VS Code](https://img.shields.io/badge/VS_Code-UV-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=plaid&inputs=%5B%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22client_id%22%2C%22description%22%3A%22Plaid%20Client%20ID%22%2C%22password%22%3Afalse%7D%2C%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22secret%22%2C%22description%22%3A%22Plaid%20Secret%22%2C%22password%22%3Atrue%7D%5D&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22mcp-server-plaid%22%5D%2C%22env%22%3A%7B%22PLAID_CLIENT_ID%22%3A%22%24%7Binput%3Aclient_id%7D%22%2C%22PLAID_SECRET%22%3A%22%24%7Binput%3Asecret%7D%22%7D%7D) [![Install with UV in VS Code Insiders](https://img.shields.io/badge/VS_Code_Insiders-UV-24bfa5?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=plaid&inputs=%5B%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22client_id%22%2C%22description%22%3A%22Plaid%20Client%20ID%22%2C%22password%22%3Afalse%7D%2C%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22secret%22%2C%22description%22%3A%22Plaid%20Secret%22%2C%22password%22%3Atrue%7D%5D&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22mcp-server-plaid%22%5D%2C%22env%22%3A%7B%22PLAID_CLIENT_ID%22%3A%22%24%7Binput%3Aclient_id%7D%22%2C%22PLAID_SECRET%22%3A%22%24%7Binput%3Asecret%7D%22%7D%7D&quality=insiders)

For manual installation, add the following JSON block to your User Settings (JSON) file in VS Code. You can do this by pressing `Ctrl + Shift + P` and typing `Preferences: Open Settings (JSON)`.

Optionally, you can add it to a file called `.vscode/mcp.json` in your workspace. This will allow you to share the configuration with others.

> Note that the `mcp` key is needed when using the `mcp.json` file.

<details>
<summary>Using uvx</summary>

```json
{
  "mcp": {
    "inputs": [
      {
        "type": "promptString",
        "id": "client_id",
        "description": "Plaid Client ID",
        "password": false
      },
      {
        "type": "promptString",
        "id": "secret",
        "description": "Plaid Secret",
        "password": true
      }
    ],
    "servers": {
      "plaid": {
        "command": "uvx",
        "args": ["mcp-server-plaid"],
        "env": {
          "PLAID_CLIENT_ID": "${input:client_id}",
          "PLAID_SECRET": "${input:secret}"
        }
      }
    }
  }
}
```
</details>

### Usage with [Zed](https://github.com/zed-industries/zed)

Add to your Zed settings.json:

<details>
<summary>Using uvx</summary>

```json
{
   "context_servers": {
      "mcp-server-plaid": {
         "command": {
            "path": "uvx",
            "args": [
               "mcp-server-plaid",
               "--client-id",
               "YOUR_PLAID_CLIENT_ID",
               "--secret",
               "YOUR_PLAID_SECRET"
            ]
         }
      }
   }
}
```
</details>

<details>
<summary>Using pip installation</summary>

```json
{
  "context_servers": {
    "mcp-server-plaid": {
      "command": "python",
      "args": [
        "-m",
        "mcp_server_plaid",
        "--client-id",
        "YOUR_PLAID_CLIENT_ID",
        "--secret",
        "YOUR_PLAID_SECRET"
      ]
    }
  }
}
```
</details>

## Debugging

You can use the MCP inspector to debug the server. For uvx installations:

```
npx @modelcontextprotocol/inspector uvx mcp-server-plaid --client-id YOUR_PLAID_CLIENT_ID --secret YOUR_PLAID_SECRET
```

Or if you've installed the package in a specific directory or are developing on it:

```
cd path/to/servers/src/plaid
npx @modelcontextprotocol/inspector uv run mcp-server-plaid --client-id YOUR_PLAID_CLIENT_ID --secret YOUR_PLAID_SECRET
```

## License

This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
