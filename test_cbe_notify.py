#!/usr/bin/env python3
"""
Direct test of CBE /notify endpoint with different @class values
"""

import requests
import json
from datetime import datetime, timezone

CBE_URL = "https://mb.cbe.com.et/api/v1/transactions/notify"
CBE_APP_ID = "123e4567-e89b-12d3-a456-426614174000"
CBE_APP_VERSION = "223e4567-e89b-12d3-a456-426614174000"
CBE_API_KEY = "your_real_api_key"

class_names = [
    "com.cbe.transaction.dto.TransactionNotifyRequest",
    "com.cbe.api.transaction.TransactionNotifyRequest",
    "com.cbe.transaction.TransactionNotifyRequest",
    "com.cbe.notification.TransactionNotifyRequest",
    "com.cbe.dto.TransactionNotifyRequest",
    "TransactionNotifyRequest",
]

print("=== Testing CBE /notify endpoint ===\n")

headers_base = {
    "Content-Type": "application/json",
    "X-App-Id": CBE_APP_ID,
    "X-App-Version": CBE_APP_VERSION,
    "Authorization": f"Bearer {CBE_API_KEY}"
}

for i, class_name in enumerate(class_names, 1):
    payload = {
        "@class": class_name,
        "transactionId": "Txn_10036304012E",
        "amount": 0.05,
        "currency": "ETB",
        "beneficiary": "Tewodros Ayele Zeberga",
        "status": "COMPLETED",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    print(f"[Attempt {i}] Testing @class={class_name}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        resp = requests.post(
            CBE_URL,
            json=payload,
            headers=headers_base,
            timeout=10,
            verify=False
        )
        
        print(f"Status: HTTP {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
        print()
        
        if resp.status_code == 200:
            print(f"✅ SUCCESS with @class={class_name}")
            break
    except Exception as e:
        print(f"Error: {str(e)}\n")
