import os
import re
import logging
import sqlite3
import requests
import json
from datetime import datetime, timezone
from flask import Flask, request, jsonify

DB_PATH = os.path.expanduser(os.environ.get("LEDGER_DB", "~/ledger.db"))
CBE_FORWARD_URL = os.environ.get("CBE_FORWARD_URL", "https://mb.cbe.com.et/api/v1/transactions/public/transaction-detail")
CBE_APP_ID = os.environ.get("CBE_APP_ID", "")
CBE_APP_VERSION = os.environ.get("CBE_APP_VERSION", "")

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("webhook-server")

app = Flask(__name__)

def init_db():
    """Initialize SQLite database with transactions table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            reference_number TEXT,
            payer_account TEXT,
            receiver_account TEXT,
            gross_amount REAL,
            switch_fee REAL,
            net_amount REAL,
            currency TEXT,
            settlement_status TEXT,
            cbe_response TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def parse_emv_qr(qr_string: str) -> dict:
    """Parse EMV-format QR code string into a dictionary"""
    data = {}
    i = 0
    while i + 4 <= len(qr_string):
        tag = qr_string[i:i+2]
        length_str = qr_string[i+2:i+4]
        if not length_str.isdigit():
            break
        length = int(length_str)
        data[tag] = qr_string[i+4:i+4+length]
        i += 4 + length
    return data

def forward_to_cbe(tx_id: str, parsed_qr: dict, amount: float):
    """Forward transaction to CBE API with multiple payload format attempts"""
    if not CBE_FORWARD_URL:
        return "skipped", None
    
    headers_base = {
        "Content-Type": "application/json",
        "X-App-Id": CBE_APP_ID,
        "X-App-Version": CBE_APP_VERSION,
    }
    
    # Test different payload formats
    payloads_to_try = [
        # Format 1: Array of objects (since error mentions "index 0")
        {
            "name": "Array Format",
            "payload": [
                {
                    "@class": "com.cbe.transaction.dto.TransactionDetailRequest",
                    "transactionId": tx_id,
                }
            ]
        },
        # Format 2: Object with @class (original)
        {
            "name": "Object with @class",
            "payload": {
                "@class": "com.cbe.transaction.dto.TransactionDetailRequest",
                "transactionId": tx_id,
            }
        },
        # Format 3: Just transaction ID
        {
            "name": "Simple Object",
            "payload": {
                "transactionId": tx_id,
            }
        },
        # Format 4: Array with simple object
        {
            "name": "Array Simple",
            "payload": [
                {
                    "transactionId": tx_id,
                }
            ]
        },
    ]
    
    for attempt in payloads_to_try:
        try:
            log.info(f"[ATTEMPT] {attempt['name']}")
            log.info(f"[PAYLOAD] {json.dumps(attempt['payload'])}")
            
            resp = requests.post(
                CBE_FORWARD_URL, 
                json=attempt['payload'], 
                headers=headers_base, 
                timeout=10, 
                verify=False
            )
            status = f"HTTP_{resp.status_code}"
            
            log.info(f"[RESPONSE] Status: {status}")
            log.info(f"[RESPONSE] Body: {resp.text[:500]}")
            
            # Store response with attempt info
            response_text = f"Format: {attempt['name']}\nStatus: {status}\n{resp.text}"
            
            # Return first response (could be success or we analyze all)
            return status, response_text
        except Exception as exc:
            log.error(f"[ERROR] {attempt['name']}: {str(exc)}")
            continue
    
    return "all_attempts_failed", None

@app.before_request
def setup():
    """Initialize database on startup"""
    if not hasattr(app, 'db_initialized'):
        init_db()
        app.db_initialized = True

@app.route('/webhook/cbe', methods=['POST'])
def handle_webhook():
    """Handle CBE EMV QR code webhook"""
    try:
        raw_bytes = request.get_data()
        qr_string = raw_bytes.decode('utf-8', errors='ignore')
        
        log.info(f"[WEBHOOK] Received QR of length: {len(qr_string)}")
        
        # Extract transaction ID from QR
        txn_match = re.search(r"(Txn_[A-Za-z0-9]+)", qr_string)
        txn_id = txn_match.group(1) if txn_match else f"Txn_{int(datetime.now().timestamp())}"
        
        # Parse EMV QR data
        parsed_qr = parse_emv_qr(qr_string)
        
        # Extract amount (tag 54 in EMV format)
        amount_str = parsed_qr.get("54", "0")
        try:
            amount_val = float(amount_str) if amount_str.replace(".", "", 1).isdigit() else 0.0
        except:
            amount_val = 0.0
        
        # Get receiver account (tag 59 in EMV format)
        receiver = parsed_qr.get("59", "Unknown")
        
        # Current timestamp
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        
        # Forward to CBE and get response
        forward_status, cbe_response = forward_to_cbe(txn_id, parsed_qr, amount_val)
        
        # Store in database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO transactions
            (transaction_id, receiver_account, gross_amount, net_amount, currency, settlement_status, cbe_response, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (txn_id, receiver, amount_val, amount_val, "ETB", "SETTLED", cbe_response, now_str, now_str))
        conn.commit()
        conn.close()
        
        log.info(f"[WEBHOOK] Stored: {txn_id} -> {forward_status}")
        
        return jsonify({
            "transaction_id": txn_id,
            "amount": amount_val,
            "forward_status": forward_status,
            "status": "received"
        }), 200
    
    except Exception as e:
        log.error(f"[ERROR] Webhook error: {str(e)}")
        return jsonify({"error": str(e), "status": "error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
