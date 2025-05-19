# Plaid Transactions Integration (Sandbox End-to-End Guide)

## Overview

This guide provides a complete, step-by-step integration of Plaid's **Transactions** product using the **Sandbox** environment. It is intended to support both **frontend** and **backend** implementations in a language-agnostic format with optional language-specific hints. The goal is to enable an AI agent or developer to execute a fully functional Plaid integration, from user bank linking to retrieving transaction data.

Assumptions:

- The developer has a Plaid account and Sandbox `client_id` and `secret` are available. If not provided, please ask the users for it.
- The application is able to make HTTP requests.

This document references Plaid's official documentation using markdown links.

## Prerequisites

Before starting the integration, check with the user and make sure: 
- You have obtained your **client ID** and **Sandbox secret** from the dashboard.
- Your development environment can serve both **frontend** and **backend** logic. The backend must be able to securely manage sensitive credentials and handle API calls.

## Step 1: Backend - Create a Link Token

The Link Token is a short-lived token created server-side that configures the [Plaid Link](mdc:https:/plaid.com/docs/link) flow. This token must be generated on your backend and passed to the frontend.

### 1.1 API Endpoint

`POST /link/token/create`

### 1.2 Required Parameters

Send a POST request to Plaid with the following JSON payload:

```json
{
  "client_id": "<your-client-id>",
  "secret": "<your-sandbox-secret>",
  "client_name": "<your-app-name>",
  "language": "en",
  "country_codes": ["US"],
  "user": {
    "client_user_id": "unique-user-id"
  },
  "products": ["transactions"]
}
```

**Optional Parameters:**

- `transactions.days_requested`: Integer between 1 and 730. Default is 90.
- `webhook`: URL to receive transaction webhooks (recommended in production).
- `redirect_uri`: Required only for OAuth-based institutions.

### 1.3 Example Response

```json
{
  "link_token": "link-sandbox-xxxxxxx",
  "expiration": "2025-05-08T10:00:00Z"
}
```

### 1.4 Notes

- Always generate a new Link Token for each session.
- This call must be done from a **secure server environment**.

## Step 2: Frontend - Initialize and Use Plaid Link

Use the `link_token` generated in Step 1 to initiate the Plaid Link flow on the frontend.

### 2.1 Add Plaid Link Script
And use the link as follows
```html
<script src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"></script>
```
or React SDK
```
npm install --save react-plaid-link
```

### 2.2 Create Plaid Link Handler

```js
const handler = Plaid.create({
  token: "<LINK_TOKEN_FROM_BACKEND>",
  onSuccess: function (public_token, metadata) {
    // Send the public_token to backend
  },
  onExit: function (err, metadata) {
    // Handle user exit or error
  },
});
handler.open();
```

### 2.3 Sandbox Test Users

- `user_good` / `pass_good` – Successful link
- `user_transactions_dynamic` / any password – Simulates real-time updates

## Step 3: Backend - Exchange Public Token for Access Token

After the user completes the Link flow, your frontend receives a `public_token`. This must be exchanged on your backend for an `access_token`, which is used for authenticated Plaid API requests.

### 3.1 API Endpoint

`POST /item/public_token/exchange`

### 3.2 Request Body

```json
{
  "client_id": "<your-client-id>",
  "secret": "<your-sandbox-secret>",
  "public_token": "<token-from-frontend>"
}
```

### 3.3 Response Body

```json
{
  "access_token": "access-sandbox-xxxxxxx",
  "item_id": "item-id-123",
  "request_id": "request-id"
}
```

> Store `access_token` securely on your backend. Never expose it to the frontend.

## Step 4: Backend - Fetch Transactions Data

### `/transactions/sync`

This endpoint supports incremental updates and efficient polling.

#### 4.1 Initial Call

```json
{
  "client_id": "<your-client-id>",
  "secret": "<your-sandbox-secret>",
  "access_token": "<access_token>"
}
```

#### 4.2 Example Response

```json
{
  "added": [...],
  "modified": [...],
  "removed": [...],
  "next_cursor": "cursor-value",
  "has_more": false
}
```

Save `next_cursor` to resume syncs. If `has_more` is `true`, repeat call with cursor.

#### 4.3 Loop Example (Pseudo-code)

```python
cursor = ""
while True:
    response = transactions_sync(cursor)
    process(response.added)
    if not response.has_more:
        break
    cursor = response.next_cursor
```

## Security & Storage Notes

- **Do not log access tokens**.
- Store access tokens securely per user.
- Tokens persist indefinitely unless manually removed or revoked.
- Always validate request origin and authenticate client calls.

## Additional Tips

- Use `transactions/sync` to keep user data fresh.
- Retry on `PRODUCT_NOT_READY` errors.
- Respect rate limits and add exponential backoff.

## Good Practice

- Always add logs for all Plaid API requests and responses in the backend implementation. This includes logging the request payload (excluding sensitive data like client secrets and access tokens), the endpoint being called, and the response status/result.
- Log all errors and exceptions with enough context to debug issues, but never log sensitive credentials or tokens.
- Example (Python):
```python
import logging
logging.basicConfig(level=logging.INFO)

# ...
logging.info(f"Calling Plaid endpoint: {url} with payload: {payload}")
logging.info(f"Plaid response: {response.status_code} {response.text}")
```

