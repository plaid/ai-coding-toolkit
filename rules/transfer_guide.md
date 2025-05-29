# Plaid Transfer Integration (Sandbox End-to-End Guide)

## Overview

This guide provides a complete, step-by-step integration of Plaid's **Transfer** product using the **Sandbox** environment. It is intended to support both **frontend** and **backend** implementations in a language-agnostic format with optional language-specific hints. The goal is to enable an AI agent or developer to execute a fully functional Plaid Transfer integration, from user bank linking to initiating fund transfers.

Assumptions:

- The developer has a Plaid account and Sandbox `client_id` and `secret` are available. If not provided, please ask the users for it.
- The application is able to make HTTP requests.

This document references Plaid's official documentation using markdown links.

> [!WARNING]
This guide is designed to be used for the purpose of building a sample Plaid integration with the use of AI coding tools. You are solely responsible for ensuring the correctness, legality, security, privacy, and compliance of your own app and Plaid integration. This guide is provided under the MIT license and is provided as-is and without warranty of any kind.

## Questions to ask the user

BEFORE you write ANY code, you MUST ask the user what type of flow they want to build, either: 
   - "Implement a Debit Transfer (Collecting Payment)" 
   - "Implement a Credit Transfer (Sending a Payment)". 

Follow the appropriate respective guide.

## Prerequisites

- You have a [Plaid Developer Dashboard](mdc:https:/dashboard.plaid.com) account.
- You have obtained your **client ID** and **Sandbox secret** from the dashboard.
- You are working in the [Sandbox environment](mdc:https:/plaid.com/docs/sandbox/overview) where test credentials and institutions are available.
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
  "products": ["transfer"]
}
```

**Optional Parameters:**

- `webhook`: URL to receive transfer webhooks (recommended in production).
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
- For language-specific implementation, use:
  - `search_documentation("Plaid link token Node.js")`
  - `search_documentation("Plaid link token Python")`

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
    // metadata.accounts contains information about the linked accounts
  },
  onExit: function (err, metadata) {
    // Handle user exit or error
  },
});
handler.open();
```

### 2.3 Sandbox Test Users

- `user_good` / `pass_good` – Successful link
- Various test accounts available for different testing scenarios

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

## Step 4: Backend - Authorize a Transfer

Before creating a transfer, you must authorize it through Plaid's risk assessment engine.

### 4.1 API Endpoint

`POST /transfer/authorization/create`

### 4.2 Required Parameters

```json
{
  "client_id": "<your-client-id>",
  "secret": "<your-sandbox-secret>",
  "access_token": "<access-token>",
  "account_id": "<account-id>",
  "type": "debit",  // or "credit" for sending money to user
  "network": "ach",  // or "same-day-ach", "rtp" for instant payments
  "amount": "100.00",
  "ach_class": "web",  // for ACH transfers
  "user": {
    "legal_name": "John Doe"
  },
  "idempotency_key": "<unique-key>"  // Strongly recommended
}
```

### 4.3 Example Response

```json
{
  "authorization": {
    "id": "authorization-id",
    "created": "2020-09-14T01:29:17Z",
    "decision": "approved",
    "decision_rationale": null
  },
  "request_id": "request-id"
}
```

### 4.4 Handling Authorization Decisions

- `approved`: Ready to create the transfer
- `declined`: Transfer cannot be created (check `decision_rationale`)
- `user_action_required`: Additional user action needed (e.g., stale Item requiring re-authentication)

## Step 5: Backend - Create a Transfer

After receiving authorization approval, you can initiate the actual transfer.

### 5.1 API Endpoint

`POST /transfer/create`

### 5.2 Required Parameters

```json
{
  "client_id": "<your-client-id>",
  "secret": "<your-sandbox-secret>",
  "authorization_id": "<authorization-id>",
  "access_token": "<access-token>",
  "account_id": "<account-id>",
  "description": "Description"
}
```

Note that "description" needs to be 15 characters or fewer

### 5.3 Example Response

```json
{
  "transfer": {
    "id": "transfer-id",
    "ach_class": "web",
    "account_id": "account-id",
    "type": "debit",
    "user": {
      "legal_name": "John Doe"
    },
    "amount": "100.00",
    "description": "Description",
    "created": "2020-09-14T01:30:17Z",
    "status": "pending",
    "network": "ach",
    "cancellable": true
  },
  "request_id": "request-id"
}
```

## Step 6: Monitoring Transfer Status

Transfers go through various status changes as they progress through the payment network. You can track these changes via API or webhooks.

### 6.1 API Method: Transfer Event Sync

`POST /transfer/event/sync`

#### 6.1.1 Request Body

```json
{
  "client_id": "<your-client-id>",
  "secret": "<your-sandbox-secret>",
  "after_id": "<last-event-id>"  // Optional, to only get new events
}
```

#### 6.1.2 Response Body

```json
{
  "transfer_events": [
    {
      "event_id": "event-id-1",
      "timestamp": "2022-01-01T12:00:00Z", 
      "event_type": "TRANSFER_CREATED",
      "account_id": "account-id-xxx",
      "transfer_id": "transfer-id-xxx",
      "origination_account_id": "origination-account-id",
      "transfer_type": "debit",
      "transfer_amount": "100.00"
    },
    {
      "event_id": "event-id-2",
      "timestamp": "2022-01-02T15:30:00Z",
      "event_type": "TRANSFER_STATUS_UPDATE",
      "account_id": "account-id-xxx",
      "transfer_id": "transfer-id-xxx",
      "origination_account_id": "origination-account-id",
      "transfer_type": "debit",
      "transfer_amount": "100.00"
    }
  ],
  "request_id": "request-id"
}
```

#### 6.1.3 Transfer Event Types

All possible values for `event_type` include:

  ##### Transfer Events
  - **pending**: A new transfer was created; it is in the pending state.
  - **cancelled**: The transfer was cancelled by the client.
  - **failed**: The transfer failed, no funds were moved.
  - **posted**: The transfer has been successfully submitted to the payment network.
  - **settled**: The transfer has been successfully completed by the payment network.
  - **funds_available**: Funds from the transfer have been released from hold and applied to the ledger's available balance. (Only applicable to ACH debits.)
  - **returned**: A posted transfer was returned.
  - **swept**: The transfer was swept to / from the sweep account.
  - **swept_settled**: Credits are available to be withdrawn or debits have been deducted from the customer's business checking account.
  - **return_swept**: Due to the transfer being returned, funds were pulled from or pushed back to the sweep account.

  ##### Ledger Sweep Events
  - **sweep.pending**: A new ledger sweep was created; it is in the pending state.
  - **sweep.posted**: The ledger sweep has been successfully submitted to the payment network.
  - **sweep.settled**: The transaction has settled in the funding account. This means that funds withdrawn from Plaid Ledger balance have reached the funding account, or funds to be 
  deposited into the Plaid Ledger Balance have been pulled, and the hold period has begun.
  - **sweep.returned**: A posted ledger sweep was returned.
  - **sweep.failed**: The ledger sweep failed, no funds were moved.
  - **sweep.funds_available**: Funds from the ledger sweep have been released from hold and applied to the ledger's available balance. This is only applicable to debits.

  ##### Refund Events
  - **refund.pending**: A new refund was created; it is in the pending state.
  - **refund.cancelled**: The refund was cancelled.
  - **refund.failed**: The refund failed, no funds were moved.
  - **refund.posted**: The refund has been successfully submitted to the payment network.
  - **refund.settled**: The refund transaction has settled in the Plaid linked account.
  - **refund.returned**: A posted refund was returned.
  - **refund.swept**: The refund was swept from the sweep account.
  - **refund.return_swept**: Due to the refund being returned, funds were pushed back to the sweep account.

### 6.2 Webhook Method

Configure a webhook URL in your Link token creation to receive event notifications automatically.

## Step 7: Sandbox Testing

In Sandbox, no real money movement occurs. You can simulate different transfer scenarios:

### 7.1 Simulate Transfer Status Updates

`POST /sandbox/transfer/simulate`

```json
{
  "client_id": "<your-client-id>",
  "secret": "<your-sandbox-secret>",
  "transfer_id": "<transfer-id>",
  "event_type": "posted"  // or "settled", "returned", etc.
}
```

### 7.2 Testing with Plaid Ledger

For testing balance management and fund availability:

1. Call `/transfer/ledger/deposit` to add funds to your Ledger balance
2. Simulate balance updates with `/sandbox/transfer/ledger/deposit/simulate` and `/sandbox/transfer/ledger/simulate_available`
3. View your ledger balance with `/transfer/ledger/get`

## Integration Example 1: Implementing a Debit Transfer (Collecting Payment)

This example shows how to collect payments from a user's bank account.

### Step 1: Link User's Bank Account
Follow Steps 1-3 above to link a user's bank account and obtain an `access_token`.

### Step 2: Authorize a Debit Transfer

```json
// Request
POST /transfer/authorization/create
{
  "client_id": "client_id_123abc",
  "secret": "secret_123abc",
  "access_token": "access-sandbox-ab1def2gh3jkl4",
  "account_id": "9aRbcd3EfGh4ijKlm5nO6pQ7",
  "type": "debit",
  "network": "same-day-ach",
  "amount": "125.00",
  "ach_class": "web",
  "user": {
    "legal_name": "Jane Doe"
  },
  "idempotency_key": "debit-transaction-123456"
}

// Response
{
  "authorization": {
    "id": "auth-sandbox-123456",
    "created": "2023-03-18T15:22:06Z",
    "decision": "approved",
    "decision_rationale": null
  },
  "request_id": "request-id-123456"
}
```

### Step 3: Create the Debit Transfer

```json
// Request
POST /transfer/create
{
  "client_id": "client_id_123abc",
  "secret": "secret_123abc",
  "authorization_id": "auth-sandbox-123456",
  "account_id": "9aRbcd3EfGh4ijKlm5nO6pQ7",
  "access_token": "access-sandbox-ab1def2gh3jkl4",
  "description": "Payment123"
}

// Response
{
  "transfer": {
    "id": "transfer-sandbox-123456",
    "ach_class": "web",
    "account_id": "9aRbcd3EfGh4ijKlm5nO6pQ7",
    "type": "debit",
    "user": {
      "legal_name": "Jane Doe"
    },
    "amount": "125.00",
    "description": "Payment123",
    "created": "2023-03-18T15:22:30Z",
    "status": "pending",
    "network": "same-day-ach",
    "cancellable": true,
    "failure_reason": null,
    "metadata": {}
  },
  "request_id": "request-id-123457"
}
```

### Step 4: Simulate Status Updates in Sandbox

```json
// Request (simulate posted status)
POST /sandbox/transfer/simulate
{
  "client_id": "client_id_123abc",
  "secret": "secret_123abc",
  "transfer_id": "transfer-sandbox-123456",
  "event_type": "posted"
}

// Request (simulate settled status)
POST /sandbox/transfer/simulate
{
  "client_id": "client_id_123abc",
  "secret": "secret_123abc",
  "transfer_id": "transfer-sandbox-123456",
  "event_type": "settled"
}

// Request (simulate funds available)
POST /sandbox/transfer/simulate
{
  "client_id": "client_id_123abc",
  "secret": "secret_123abc",
  "transfer_id": "transfer-sandbox-123456",
  "event_type": "funds_available"
}
```

## Integration Example 2: Implementing a Credit Transfer (Sending a Payment)

This example shows how to send payments to a user's bank account. First, you need to fund your Plaid Ledger.

### Step 1: Fund your Plaid Ledger 

This step is required because if there are no (fake) funds in the Plaid Ledger, the authorization will be declined.

```json
// Request
POST /transfer/ledger/deposit
{
  "client_id": "client_id_123abc",
  "secret": "secret_123abc",
  "amount": "1000.00",
  "idempotency_key": "ledger-deposit-987654",
  "network": "same-day-ach",
  "description": "Add funds"
}

// Response
{
  "sweep": {
    "id": "sweep-sandbox-123456",
    "funding_account_id": "funding-account-123",
    "ledger_id": "ledger-sandbox-123",
    "created": "2023-03-18T14:00:00Z",
    "amount": "1000.00",
    "iso_currency_code": "USD",
    "settled": null,
    "status": "pending",
    "trigger": "manual",
    "description": "Add funds",
    "network_trace_id": null,
    "failure_reason": null
  },
  "request_id": "request-id-789012"
}
```

### Step 2: Simulate the Ledger Deposit Status Updates

```json
// Simulate posted status
POST /sandbox/transfer/ledger/deposit/simulate
{
  "client_id": "client_id_123abc",
  "secret": "secret_123abc",
  "sweep_id": "sweep-sandbox-123456",
  "event_type": "sweep.posted"
}

// Simulate settled status
POST /sandbox/transfer/ledger/deposit/simulate
{
  "client_id": "client_id_123abc",
  "secret": "secret_123abc",
  "sweep_id": "sweep-sandbox-123456",
  "event_type": "sweep.settled"
}

// Simulate making funds available
POST /sandbox/transfer/ledger/simulate_available
{
  "client_id": "client_id_123abc",
  "secret": "secret_123abc"
}
```

### Step 3: Link User's Bank Account
Follow Steps 1-3 of the main guide to link a user's bank account and obtain an `access_token`.

### Step 4: Authorize a Credit Transfer

```json
// Request
POST /transfer/authorization/create
{
  "client_id": "client_id_123abc",
  "secret": "secret_123abc",
  "access_token": "access-sandbox-ab1def2gh3jkl4",
  "account_id": "9aRbcd3EfGh4ijKlm5nO6pQ7",
  "type": "credit",
  "network": "rtp",  // Use RTP for instant payouts
  "amount": "250.00",
  "user": {
    "legal_name": "John Smith"
  },
  "idempotency_key": "credit-transaction-987654"
}

// Response
{
  "authorization": {
    "id": "auth-sandbox-654321",
    "created": "2023-03-18T16:30:00Z",
    "decision": "approved",
    "decision_rationale": null
  },
  "request_id": "request-id-654321"
}
```

### Step 5: Create the Credit Transfer

```json
// Request
POST /transfer/create
{
  "client_id": "client_id_123abc",
  "secret": "secret_123abc",
  "authorization_id": "auth-sandbox-654321",
  "account_id": "9aRbcd3EfGh4ijKlm5nO6pQ7",
  "access_token": "access-sandbox-ab1def2gh3jkl4",
  "description": "Payout456"
}

// Response
{
  "transfer": {
    "id": "transfer-sandbox-654321",
    "account_id": "9aRbcd3EfGh4ijKlm5nO6pQ7",
    "type": "credit",
    "user": {
      "legal_name": "John Smith"
    },
    "amount": "250.00",
    "description": "Payout456",
    "created": "2023-03-18T16:30:30Z",
    "status": "pending",
    "network": "rtp",
    "cancellable": false,
    "failure_reason": null,
    "metadata": {}
  },
  "request_id": "request-id-654322"
}
```

### Step 6: Simulate Status Updates for the Credit Transfer

```json
// Request (simulate posted status)
POST /sandbox/transfer/simulate
{
  "client_id": "client_id_123abc",
  "secret": "secret_123abc",
  "transfer_id": "transfer-sandbox-654321",
  "event_type": "posted"
}

// Request (simulate settled status)
POST /sandbox/transfer/simulate
{
  "client_id": "client_id_123abc",
  "secret": "secret_123abc",
  "transfer_id": "transfer-sandbox-654321",
  "event_type": "settled"
}
```

## Security & Storage Notes

- **Do not log access tokens or other sensitive credentials**.
- Store access tokens securely per user.
- Tokens persist indefinitely unless manually removed or revoked.
- Always validate request origin and authenticate client calls.
- Use idempotency keys to prevent duplicate transfers.

## Additional Tips

- Always include idempotency keys with authorization requests to prevent duplicates
- Handle 500 errors safely by checking if the transfer was still created
- For ACH debits, consider using same-day ACH to reduce NSF (insufficient funds) returns
- Monitor your transfer limits to avoid declined authorizations
- Keep sufficient funds in your Plaid Ledger for credit transfers

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