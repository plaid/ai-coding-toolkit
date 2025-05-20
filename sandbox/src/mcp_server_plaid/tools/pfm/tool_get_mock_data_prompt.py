from datetime import datetime
from string import Template
from typing import Any, Dict, List

import mcp.types as types

from mcp_server_plaid.tools.registry import registry

TEMPLATE_CONTEXT = Template("""
```xml
<context>
Create realistic mock banking data for testing purposes following the specified JSON structure.
Generate data that mimics real-world banking transactions with appropriate patterns, descriptions,
and financial behaviors. Please directly generate $num_of_transactions transactions for each account 
based on the following guidelines.
</context>

<requirements>
  <account_types>
    <types>
      - depository
      - credit
      - loan
      - investment
    </types>
    <subtypes>
      - depository: checking, savings
      - credit: credit card
      - loan: mortgage
      - investment: 401k
    </subtypes>
  </account_types>

  <transaction_patterns>
    <date_patterns>
      - Date_transacted should be 1 day before date_posted
      - Dates should follow chronological order from newest to oldest
      - Use realistic date patterns spanning 3-6 months from the $current_date
    </date_patterns>

    <amount_patterns>
      - Business Accounts: $9 to $15,000
      - Personal Accounts: $1 to $5,000
      - Include both positive (credits) and negative (debits) values
      - Recurring transactions should have similar amounts each month
    </amount_patterns>

    <description_patterns>
      <business_accounts>
        - Subscription: AWS, Twilio, Typeform, Hubspot
        - Payroll: GUSTO, ADP
        - Insurance: United Healthcare
        - Utilities: AT&T, Comcast
        - Supplies: Amazon, Staples
        - Professional: Accounting Services, Legal Services
        - Transfers: Account Transfers
        - Loans: Loan Payments
      </business_accounts>

      <personal_accounts>
        - Groceries: Trader Joe's, Whole Foods, Safeway
        - Food: DoorDash, Uber Eats, Local Restaurants
        - Transportation: Uber, Lyft, Public Transit
        - Utilities: Electric Company, Water Company, Internet Provider
        - Entertainment: Netflix, Spotify, Disney+
        - Shopping: Amazon, Target
        - Housing: Rent/Mortgage Payments
        - Income: Payroll Deposits
        - Transfers: Account Transfers
      </personal_accounts>
    </description_patterns>

    <recurring_patterns>
      - Monthly: Subscriptions (same day each month)
      - Bi-weekly: Payroll deposits
      - Quarterly: Tax payments
      - Weekly: Grocery shopping
      - Monthly: Rent/mortgage payments
    </recurring_patterns>
  </transaction_patterns>
</requirements>

<identity_guidelines>
  - Use realistic but fictional names and addresses
  - Keep identity consistent across accounts for the same user/business
  - For business accounts, use business names rather than personal names
</identity_guidelines>

<pattern_examples>
  <business_account_patterns>
    - Monthly SaaS subscriptions on similar dates each month
    - Bi-weekly payroll processing
    - Monthly insurance payments
    - Quarterly tax payments
    - Occasional large transfers between accounts
    - Monthly loan payments
  </business_account_patterns>

  <personal_account_patterns>
    - Bi-weekly payroll deposits (consistent amounts)
    - Monthly rent/mortgage payments (same day each month)
    - Weekly grocery shopping (varying amounts within a range)
    - Monthly subscription services (same amount, same day)
    - Occasional larger purchases
    - Weekly restaurant/food delivery charges
  </personal_account_patterns>
</pattern_examples>

<special_instructions>
  - Make sure the transactions tell a realistic "story" about the account holder's financial behavior
  - Ensure date sequences are chronologically realistic
  - Use appropriate merchant names that match the transaction descriptions
  - For business accounts, include industry-specific services and vendors
  - Balance the number of credits and debits to maintain realistic account behavior
  - Include occasional unusual but realistic transactions
  - Generate at least 30-50 transactions per account for proper testing
</special_instructions>

<format_details>
  <transaction_description_format>
    - Business Format: [VENDOR NAME]; [TRANSACTION TYPE]:[REFERENCE NUMBER]
    - Business Example: GUSTO; GUSTO:6HA8310KNB Merchant name: GUSTO
    - Personal Format: [TRANSACTION TYPE] [VENDOR] [NUMERIC ID] [ALPHANUMERIC STRING]
    - Personal Example: DEBIT CRD AUTOPAY 98712 000000000098712 WRSGTKIUYPKF KJHAUXYOTLL
  </transaction_description_format>

  <merchant_name_inclusion>
    - Format: Primary description. Merchant name: [Merchant]
    - Example: Amazon web services. Merchant name: Amazon Web Services
  </merchant_name_inclusion>

  <amount_conventions>
    - Expenses (money leaving the account) are negative numbers
    - Income (money entering the account) are positive numbers
    - Transfers between accounts follow the appropriate sign convention
  </amount_conventions>

  <date_formatting>
    - ISO format: YYYY-MM-DD
    - Ensure weekends and holidays are accounted for in posting dates
  </date_formatting>
</format_details>

<sample_transactions>
  <business_account>
    - SaaS: AWS (~$800-6000), Twilio (~$700-1500), Typeform (~$10-50), Hubspot (~$50-100)
    - Payroll: GUSTO or ADP (~$2000-5000 bi-weekly)
    - Insurance: United Healthcare (~$5000-7500 monthly), Hiscox (~$200-250 monthly)
    - Utilities: ATT (~$300-450 monthly)
    - Travel: American Airlines (~$200-500 per trip)
    - Professional: LinkedIn (~$200-600 quarterly)
    - Transfers: Regular transfers to other accounts (~$3000-10000)
    - Loans: SBA Loan (~$2500-5000 monthly)
  </business_account>

  <personal_account>
    - Income: Payroll deposits (~$2000-4000 bi-weekly)
    - Housing: Rent/Mortgage (~$1500-3000 monthly)
    - Groceries: Groceries (~$100-300 weekly)
    - Food: Restaurants (~$20-100, several times weekly)
    - Entertainment: Netflix (~$15), Spotify (~$10)
    - Utilities: Electric (~$100-200), Internet (~$50-100)
    - Shopping: Amazon, Target, etc. (varying amounts)
    - Transportation: Uber, Lyft (~$15-50 per ride)
  </personal_account>
</sample_transactions>

<output_format>
{
    "override_accounts": [
        {
            "type": "[account type]",
            "subtype": "[account subtype]",
            "starting_balance": [optional balance amount],
            "meta": {
                "name": "[bank name]",
                "official_name": "[official account name]"
            },
            "numbers": {
                "account": "[account number]",
                "ach_routing": "021000021"
            },
            "transactions": [
                {
                    "date_transacted": "[YYYY-MM-DD]",
                    "date_posted": "[YYYY-MM-DD]",
                    "amount": [transaction amount],
                    "description": "[transaction description]",
                    "currency": "[currency code]"
                },
                ...
            ],
            "identity": {
                "names": [
                    "[account holder name]"
                ],
                "addresses": [
                    {
                        "primary": true,
                        "data": {
                            "country": "[country code]",
                            "city": "[city name]",
                            "street": "[street address]",
                            "postal_code": "[postal code]",
                            "region": "[state/province code]"
                        }
                    }
                ]
            }
        }
    ]
}
</output_format>

<important>
  - The output MUST be a *stringified* JSON object without any `\n` characters and copied to the clipboard.
  - You MUST also ask the user if they would like to persist the mock data to a local file, and if they do, you MUST write the mock data to a file named `mock_data.json` in the current working directory.
</important>
""")

# Tool definition
GET_MOCK_DATA_PROMPT_TOOL = types.Tool(
    name="get_mock_data_prompt",
    description="""Get the mock data prompt for the AI agent to generate mock data for testing purposes. 
    <important>
    - You must have a real time generation display of the mock data to the end user. 
    - You must ask use if they would like to persist the mock data to a local file, and 
      if they do, you MUST write the mock data to a file named `mock_data.json` in the current working directory.
    </important>
   """,
    inputSchema={
        "type": "object",
        "properties": {
            "num_of_transactions": {
                "type": "string",
                "description": "number of transactions to generate",
                "default": "10"
            }
        },
        "required": ["num_of_transactions"],
    },
)


# Tool handler
async def handle_get_mock_data_prompt(
        arguments: Dict[str, Any], **_
) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    # Concatenate the template parts with the number of transactions
    prompt_text = TEMPLATE_CONTEXT.safe_substitute(
        num_of_transactions=arguments["num_of_transactions"],
        current_date=datetime.now().strftime("%Y-%m-%d"),
    )

    return [
        types.TextContent(
            type="text",
            text=prompt_text,
        )
    ]


# Register the tool with the registry
registry.register(GET_MOCK_DATA_PROMPT_TOOL, handle_get_mock_data_prompt)
