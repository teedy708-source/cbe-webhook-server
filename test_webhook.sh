#!/bin/bash
# Start webhook server and test it

echo "=== Killing old processes ==="
pkill -f webhook_server.py
sleep 1

echo "=== Starting webhook server ==="
python3 webhook_server.py > /tmp/webhook.log 2>&1 &
WEBHOOK_PID=$!
echo "Webhook PID: $WEBHOOK_PID"

echo "=== Waiting 3 seconds for server to start ==="
sleep 3

echo "=== Testing webhook endpoint ==="
curl -X POST http://127.0.0.1:5000/webhook/cbe \
  -H "Content-Type: text/plain" \
  -d "00020101021128360003CBE0108CBETETAA0213100069863451452040000530323054128208750000.05802ET5922Tewodros Ayele Zeberga6011Addis Ababa87130003cbe01021280240008etswitch0108Txn_10036304012E"

echo ""
echo "=== Webhook server logs ==="
tail -30 /tmp/webhook.log

echo ""
echo "=== Checking database response ==="
python3 -c "import sqlite3; conn = sqlite3.connect('/data/data/com.termux/files/home/ledger.db'); result = conn.execute('SELECT transaction_id, cbe_response FROM transactions ORDER BY created_at DESC LIMIT 1').fetchone(); print('Transaction:', result[0]); print('\nResponse:'); print(result[1][:500] if result[1] else 'NULL')"

echo ""
echo "=== Done ==="
