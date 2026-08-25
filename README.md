# CBE Webhook Server

A Python Flask-based webhook server for processing Commercial Bank of Ethiopia (CBE) EMV QR code transactions.

## Features

- **EMV QR Parsing**: Extracts transaction data from EMV-format QR codes
- **SQLite Ledger**: Stores all transactions in a local SQLite database
- **CBE API Integration**: Forwards transactions to CBE API with proper JSON payload format
- **Transaction Tracking**: Maintains complete transaction history with timestamps and status

## Setup

### Prerequisites

- Python 3.7+
- pip

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

Set environment variables:

```bash
# Path to SQLite database (default: ~/ledger.db)
export LEDGER_DB="~/ledger.db"

# CBE API endpoint URL for transaction verification
export CBE_FORWARD_URL="https://your-cbe-api-endpoint/api/v1/transactions/public/transaction-detail"

# API key for CBE service
export CBE_API_KEY="your_actual_api_key_here"
```

## Running the Server

```bash
python webhook_server.py
```

The server will start on `http://0.0.0.0:5000`

## API Endpoints

### POST /webhook/cbe

Receives EMV QR code data and processes the transaction.

**Request:**
- Content-Type: text/plain or application/octet-stream
- Body: EMV-format QR code string

**Response:**
```json
{
  "transaction_id": "Txn_10036304012E",
  "amount": 8208750000.0,
  "forward_status": "HTTP_200",
  "status": "received"
}
```

## Testing

```bash
curl -X POST http://127.0.0.1:5000/webhook/cbe \
  -H "Content-Type: text/plain" \
  -d '00020101021128360003CBE0108CBETETAA02131000698634514520400005303...'
```

## Database Schema

The SQLite database contains a `transactions` table with:

- `transaction_id` (TEXT, PRIMARY KEY)
- `reference_number` (TEXT)
- `payer_account` (TEXT)
- `receiver_account` (TEXT)
- `gross_amount` (REAL)
- `switch_fee` (REAL)
- `net_amount` (REAL)
- `currency` (TEXT)
- `settlement_status` (TEXT)
- `cbe_response` (TEXT) - CBE API response for debugging
- `created_at` (TEXT)
- `updated_at` (TEXT)

## Troubleshooting

### HTTP 400 - Invalid Request / @class Error

The CBE API uses Jackson polymorphic deserialization and requires a `@class` property.

**Fix**: The webhook server now automatically includes:
```json
{
  "@class": "com.cbe.transaction.dto.TransactionDetailRequest",
  "transactionId": "Txn_...",
  "amount": 1000.0,
  "currency": "ETB"
}
```

### HTTP 403 - Forbidden

Check that:
- `CBE_API_KEY` is set correctly
- The API key has permission to access the endpoint
- The endpoint URL is correct

### Connection Timeouts

Increase the timeout value in `forward_to_cbe()` function or check network connectivity.

## License

MIT
