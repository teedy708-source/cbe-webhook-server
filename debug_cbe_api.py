#!/usr/bin/env python3
"""
CBE API Debugging Utility
Tests different request formats and methods against the CBE API
"""

import os
import requests
import json
from urllib.parse import urljoin

# Configuration
CBE_API_BASE = os.environ.get("CBE_API_BASE", "https://mb.cbe.com.et/api/v1")
CBE_APP_ID = os.environ.get("CBE_APP_ID", "3fa85f64-5717-4562-b3fc-2c963f66afa6")
CBE_APP_VERSION = os.environ.get("CBE_APP_VERSION", "123e4567-e89b-12d3-a456-426614174000")
TXN_ID = "Txn_10036304012E"

def test_get_request():
    """Test GET request to transaction detail endpoint"""
    url = f"{CBE_API_BASE}/transactions/public/transaction-detail/{TXN_ID}"
    headers = {
        "X-App-Id": CBE_APP_ID,
        "X-App-Version": CBE_APP_VERSION,
    }
    
    print("\n" + "="*80)
    print("TEST 1: GET Request")
    print("="*80)
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    
    try:
        resp = requests.get(url, headers=headers, timeout=10, verify=False)
        print(f"\nStatus: {resp.status_code}")
        print(f"Response:\n{resp.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

def test_post_request_empty():
    """Test POST request with empty body"""
    url = f"{CBE_API_BASE}/transactions/public/transaction-detail/{TXN_ID}"
    headers = {
        "X-App-Id": CBE_APP_ID,
        "X-App-Version": CBE_APP_VERSION,
        "Content-Type": "application/json",
    }
    
    print("\n" + "="*80)
    print("TEST 2: POST Request (Empty Body)")
    print("="*80)
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    
    try:
        resp = requests.post(url, headers=headers, json={}, timeout=10, verify=False)
        print(f"\nStatus: {resp.status_code}")
        print(f"Response:\n{resp.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

def test_post_request_with_payload():
    """Test POST request with transaction payload"""
    url = f"{CBE_API_BASE}/transactions/public/transaction-detail"
    headers = {
        "X-App-Id": CBE_APP_ID,
        "X-App-Version": CBE_APP_VERSION,
        "Content-Type": "application/json",
    }
    payload = {
        "transactionId": TXN_ID,
    }
    
    print("\n" + "="*80)
    print("TEST 3: POST Request (With Transaction Payload)")
    print("="*80)
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Body: {json.dumps(payload, indent=2)}")
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10, verify=False)
        print(f"\nStatus: {resp.status_code}")
        print(f"Response:\n{resp.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

def test_post_request_with_class():
    """Test POST request with @class property"""
    url = f"{CBE_API_BASE}/transactions/public/transaction-detail"
    headers = {
        "X-App-Id": CBE_APP_ID,
        "X-App-Version": CBE_APP_VERSION,
        "Content-Type": "application/json",
    }
    payload = {
        "@class": "com.cbe.transaction.dto.TransactionDetailRequest",
        "transactionId": TXN_ID,
    }
    
    print("\n" + "="*80)
    print("TEST 4: POST Request (With @class Property)")
    print("="*80)
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Body: {json.dumps(payload, indent=2)}")
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10, verify=False)
        print(f"\nStatus: {resp.status_code}")
        print(f"Response:\n{resp.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

def test_post_request_form_data():
    """Test POST request with form data"""
    url = f"{CBE_API_BASE}/transactions/public/transaction-detail"
    headers = {
        "X-App-Id": CBE_APP_ID,
        "X-App-Version": CBE_APP_VERSION,
    }
    data = {
        "transactionId": TXN_ID,
    }
    
    print("\n" + "="*80)
    print("TEST 5: POST Request (Form Data)")
    print("="*80)
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        resp = requests.post(url, headers=headers, data=data, timeout=10, verify=False)
        print(f"\nStatus: {resp.status_code}")
        print(f"Response:\n{resp.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("\n" + "🔍 CBE API DEBUGGING UTILITY")
    print(f"Base URL: {CBE_API_BASE}")
    print(f"Transaction ID: {TXN_ID}")
    
    # Run all tests
    test_get_request()
    test_post_request_empty()
    test_post_request_with_payload()
    test_post_request_with_class()
    test_post_request_form_data()
    
    print("\n" + "="*80)
    print("DEBUGGING COMPLETE")
    print("="*80)
    print("\nReview the responses above to determine which format works.")
    print("Update webhook_server.py with the working format.\n")
