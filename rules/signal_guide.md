# Plaid Signal Integration (Sandbox End-to-End Guide)

## Overview

This guide provides a complete, step-by-step integration of Plaid's **Signal** product using the **Sandbox** environment. It is intended to support both **frontend** and **backend** implementations in a language-agnostic format with optional language-specific hints. The goal is to enable an AI agent or developer to execute a fully functional Plaid Signal integration, from user bank linking to evaluating ACH payment risk.

Assumptions:
- The developer has a Plaid account and Sandbox `client_id` and `secret` are available. If not provided, please ask the users for it.
- The application is able to make HTTP requests.
- You have been approved for Signal access (or are using Sandbox while waiting for approval).

This document references Plaid's official documentation using markdown links.

## Prerequisites

Before starting the integration, ensure the following:

- You have a [Plaid Developer Dashboard](https:/dashboard.plaid.com) account.
- You have obtained your **client ID** and **Sandbox secret** from the dashboard.
- You are working in the [Sandbox environment](https:/plaid.com/docs/sandbox/overview) where test credentials and institutions are available.
- Your development environment can serve both **frontend** and **backend** logic. The backend must be able to securely manage sensitive credentials and handle API calls.
- You have applied for and received approval for Signal (or have received Sandbox access while waiting for approval).

## Step 1: Create a Signal Ruleset in the Dashboard

Before beginning your integration, first create a ruleset in the Plaid Dashboard.

### 1.1 Access Signal Rules Dashboard

- Navigate to the [Signal Rules Dashboard](https:/dashboard.plaid.com/signal/risk-profiles) page.
- Toggle Sandbox mode in the top right corner.

### 1.2 Create a Ruleset

- Create a new ruleset, either from scratch or use a Plaid-suggested template.
- Configure rules with appropriate risk thresholds.
- Note your `ruleset_key` for use in API calls.

## Step 2: Backend - Create a Link Token

The Link Token is a short-lived token created server-side that configures the [Plaid Link](https:/plaid.com/docs/link) flow. This token must be generated on your backend and passed to the frontend.

### 2.1 API Endpoint

`POST /link/token/create`

### 2.2 Required Parameters

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
  "products": ["auth"],
  "optional_products": ["signal"]
}
```

**Optional Parameters:**
- `webhook`: URL to receive webhooks (recommended in production).
- `redirect_uri`: Required only for OAuth-based institutions.

### 2.3 Example Response

```json
{
  "link_token": "link-sandbox-xxxxxxx",
  "expiration": "2025-05-08T10:00:00Z"
}
```

### 2.4 Notes

- Always generate a new Link Token for each session.
- This call must be done from a **secure server environment**

## Step 3: Frontend - Initialize and Use Plaid Link

Use the `link_token` generated in Step 2 to initiate the Plaid Link flow on the frontend.

### 3.1 Add Plaid Link Script
And use the link as follows
```html
<script src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"></script>
```
or React SDK
```
npm install --save react-plaid-link
```

### 3.2 Create Plaid Link Handler

```js
const handler = Plaid.create({
  token: "<LINK_TOKEN_FROM_BACKEND>",
  onSuccess: function (public_token, metadata) {
    // Send the public_token and account_id to backend
    const selectedAccount = metadata.accounts[0];
    const accountId = selectedAccount.id;
    
    // Send public_token and accountId to your backend
  },
  onExit: function (err, metadata) {
    // Handle user exit or error
  },
});
handler.open();
```

### 3.3 Sandbox Test Users

- `user_good` / `pass_good` – Successful link
- Other Sandbox credentials as needed

## Step 4: Backend - Exchange Public Token for Access Token

After the user completes the Link flow, your frontend receives a `public_token`. This must be exchanged on your backend for an `access_token`, which is used for authenticated Plaid API requests.

### 4.1 API Endpoint

`POST /item/public_token/exchange`

### 4.2 Request Body

```json
{
  "client_id": "<your-client-id>",
  "secret": "<your-sandbox-secret>",
  "public_token": "<token-from-frontend>"
}
```

### 4.3 Response Body

```json
{
  "access_token": "access-sandbox-xxxxxxx",
  "item_id": "item-id-123",
  "request_id": "request-id"
}
```

> Store `access_token` securely on your backend. Never expose it to the frontend.

## Step 5: Backend - Evaluate Transaction Risk with Signal

Now that you have an access token and account ID, you can evaluate the risk of an ACH transaction using Signal.

### 5.1 API Endpoint

`POST /signal/evaluate`

### 5.2 Request Body

```json
{
  "client_id": "<your-client-id>",
  "secret": "<your-sandbox-secret>",
  "access_token": "<access_token>",
  "account_id": "<account_id>",
  "client_transaction_id": "unique-transaction-id",
  "amount": 100.00,
  "user_present": true,
  "client_user_id": "user-123",
  "ruleset_key": "<ruleset_key_from_dashboard>"
}
```

All of the above are REQUIRED properties

### 5.3 Sandbox Testing

In Sandbox, you can influence the returned score by providing the following test amounts:
- `3.53`: Returns a score of 10 (low risk)
- `12.17`: Returns a score of 60 (medium risk)
- `27.53`: Returns a score of 90 (high risk)

### 5.4 Example Response

```json
{
  "request_id": "request-id",
  "scores": {
    "bank_initiated_return_risk": {
      "score": 45,
    },
    "customer_initiated_return_risk": {
      "score": 30,
    }
  },
  "core_attributes": {
    "days_since_first_plaid_connection": 32,
    "plaid_connections_count": 1,
    "is_savings_or_money_market_account": false,
    "is_account_closed": false
  },
  "ruleset": {
    "ruleset_key": "first_time_users",
    "result": "ACCEPT",
    "triggered_rule_details": {
      "internal_note": "Low risk transaction",
      "custom_action_key": "3-day-hold"
    }
  }
}
```

### 5.5 Processing the Response

- Check the `ruleset.result` property which will contain one of:
  - `ACCEPT`: Process the transaction
  - `REVIEW`: Conduct additional review before processing
  - `REROUTE`: Direct customer to another payment method due to high risk
- Optionally, check `ruleset.triggered_rule_details.custom_action_key` for additional actions (e.g., hold time)
- You can also examine raw scores and core attributes for custom risk models

## Step 6: Backend - Report Transaction Decision

After deciding whether to process a transaction, report your decision back to Plaid. This helps Plaid improve accuracy and allows you to track transaction outcomes.

### 6.1 API Endpoint

`POST /signal/decision/report`

### 6.2 Request Body

```json
{
  "client_id": "<your-client-id>",
  "secret": "<your-sandbox-secret>",
  "client_transaction_id": "unique-transaction-id",
  "initiated": true,
}
```

### 6.3 Response Body

```json
{
  "request_id": "request-id"
}
```

## Step 7: Backend - Report an ACH Return

If a transaction is returned (e.g., insufficient funds), report this to Plaid to improve future risk assessments. This is a very important step.

### 7.1 API Endpoint

`POST /signal/return/report`

### 7.2 Request Body

```json
{
  "client_id": "<your-client-id>",
  "secret": "<your-sandbox-secret>",
  "client_transaction_id": "unique-transaction-id",
  "return_code": "R01"
}
```

**Optional Parameter:**
- `returned_at`: ISO 8601 timestamp of when the return occurred

### 7.3 Response Body

```json
{
  "request_id": "request-id"
}
```

## Security & Storage Notes

- **Do not log access tokens** or other sensitive credentials.
- Store access tokens securely per user.
- Tokens persist indefinitely unless manually removed or revoked.
- Always validate request origin and authenticate client calls.

## Additional Tips

- Always use a unique `client_transaction_id` for each transaction.
- Ensure you report ACH returns to improve Signal's accuracy over time.

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