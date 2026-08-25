import os
import re
import logging
import sqlite3
import requests
import json
from datetime import datetime, timezone
from flask import Flask, request, jsonify

DB_PATH = os.path.expanduser(os.environ.get("LEDGER_DB", "~/ledger.db"))
CBE_FORWARD_URL = os.environ.get("CBE_FORWARD_URL", "https://mb.cbe.com.et/api/v1/transactions/notify")
CBE_APP_ID = os.environ.get("CBE_APP_ID", "")
CBE_APP_VERSION = os.environ.get("CBE_APP_VERSION", "")
CBE_API_KEY = os.environ.get("CBE_API_KEY", "")

logging.basicConfig(level=logging.INFO)
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

def forward_to_cbe(tx_id: str, parsed_qr: dict, amount: float, receiver: str):
    """Forward transaction notification to CBE API with multiple @class attempts"""
    if not CBE_FORWARD_URL:
        return "skipped", None
    
    headers_base = {
        "Content-Type": "application/json",
        "X-App-Id": CBE_APP_ID,
        "X-App-Version": CBE_APP_VERSION,
    }
    
    if CBE_API_KEY:
        headers_base["Authorization"] = f"Bearer {CBE_API_KEY}"
    
    # Test different @class values for /notify endpoint
    class_names = [
        "com.cbe.transaction.dto.TransactionNotifyRequest",
        "com.cbe.api.transaction.TransactionNotifyRequest",
        "com.cbe.transaction.TransactionNotifyRequest",
        "com.cbe.notification.TransactionNotifyRequest",
        "com.cbe.dto.TransactionNotifyRequest",
        "TransactionNotifyRequest",
    ]
    
    for class_name in class_names:
        try:
            payload = {
                "@class": class_name,
                "transactionId": tx_id,
                "amount": amount,
                "currency": "ETB",
                "beneficiary": receiver,
                "status": "COMPLETED",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            log.info(f"[NOTIFY ATTEMPT] @class={class_name}")
            log.info(f"[PAYLOAD] {json.dumps(payload)}")
            
            resp = requests.post(
                CBE_FORWARD_URL,
                json=payload,
                headers=headers_base,
                timeout=10,
                verify=False
            )
            status = f"HTTP_{resp.status_code}"
            
            log.info(f"[RESPONSE] Status: {status}")
            log.info(f"[RESPONSE] Body: {resp.text[:300]}")
            
            # Store response with class name info
            response_text = f"@class: {class_name}\nStatus: {status}\n{resp.text}"
            return status, response_text
            
        except Exception as exc:
            log.error(f"[ERROR] {class_name}: {str(exc)}")
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
        
        # Forward to CBE
        forward_status, cbe_response = forward_to_cbe(txn_id, parsed_qr, amount_val, receiver)
        
        # Store in database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO transactions
            (transaction_id, receiver_account, gross_amount, net_amount, currency, settlement_status, cbe_response, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (txn_id, receiver, amount_val, amount_val, "ETB", "NOTIFIED", cbe_response, now_str, now_str))
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
