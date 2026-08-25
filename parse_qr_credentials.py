#!/usr/bin/env python3
"""
Parse CBE EMV QR code to extract embedded credentials and transaction details
"""

import re

QR_DATA = "00020101021128360003CBE0108CBETETAA0213100069863451452040000530323054128208750000.05802ET5922Tewodros Ayele Zeberga6011Addis Ababa87130003cbe01021280240008etswitch0108Txn_10036304012E"

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
        value = qr_string[i+4:i+4+length]
        data[tag] = value
        i += 4 + length
    return data

def parse_constructed_data(data_str: str) -> dict:
    """Parse constructed/nested tag data"""
    result = {}
    i = 0
    while i + 4 <= len(data_str):
        tag = data_str[i:i+2]
        length_str = data_str[i+2:i+4]
        if not length_str.isdigit():
            break
        length = int(length_str)
        value = data_str[i+4:i+4+length]
        result[tag] = value
        i += 4 + length
    return result

print("=== CBE EMV QR Code Parser ===\n")
print(f"QR Code: {QR_DATA}\n")

# Parse top-level tags
parsed = parse_emv_qr(QR_DATA)

print("=== Top-Level Tags ===")
for tag, value in sorted(parsed.items()):
    print(f"Tag {tag}: {value}")

print("\n=== EMV Tag Meanings ===")
emv_tags = {
    "00": "Payload Format Indicator",
    "01": "Point of Initiation Method",
    "02": "Merchant Category Code",
    "03": "Transaction Currency",
    "04": "Transaction Amount",
    "05": "Tip or Convenience Fee",
    "06": "Convenience Fee Fixed",
    "07": "Convenience Fee Percentage",
    "08": "Country Code",
    "09": "Merchant Name",
    "10": "Merchant City",
    "11": "Postal Code",
    "12": "Alternate Payee Presentation Mode",
    "13": "Merchant Alternate Language Preference",
    "14": "Merchant Information Language Template",
    "15": "RFU",
    "16": "RFU",
    "17": "RFU",
    "18": "RFU",
    "19": "RFU",
    "20": "RFU",
    "21": "RFU",
    "22": "RFU",
    "23": "RFU",
    "24": "RFU",
    "25": "RFU",
    "26": "RFU",
    "27": "RFU",
    "28": "Merchant Account Information",
    "29": "Class Name",
    "30": "Class Name",
    "31": "Class Name",
    "32": "Class Name",
    "33": "Class Name",
    "34": "Class Name",
    "35": "Class Name",
    "36": "Class Name",
    "37": "Class Name",
    "38": "Class Name",
    "39": "Class Name",
    "40": "Additional Data Field Template",
    "41": "RFU",
    "42": "RFU",
    "43": "RFU",
    "44": "RFU",
    "45": "RFU",
    "46": "RFU",
    "47": "RFU",
    "48": "RFU",
    "49": "RFU",
    "50": "CRC",
    "51": "Merchant Type",
    "52": "Duplicate Transaction Indicator",
    "53": "Reference Label",
    "54": "Amount",
    "55": "Reference Number",
    "56": "Static/Dynamic QR",
    "57": "Beneficiary Account Information",
    "58": "Beneficiary Name",
    "59": "Receiver Account",
    "60": "Receiver Name",
    "61": "Authentication Method",
    "62": "Security Header",
    "63": "CRC",
}

for tag, value in sorted(parsed.items()):
    meaning = emv_tags.get(tag, "Unknown")
    # Try to parse constructed data
    try:
        if len(value) > 4:
            sub_data = parse_constructed_data(value)
            print(f"\nTag {tag} ({meaning}): {value}")
            print(f"  Sub-tags:")
            for sub_tag, sub_value in sorted(sub_data.items()):
                print(f"    {sub_tag}: {sub_value}")
        else:
            print(f"Tag {tag} ({meaning}): {value}")
    except:
        print(f"Tag {tag} ({meaning}): {value}")

print("\n=== Looking for UUIDs and Credentials ===")
# Look for UUID patterns
uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
uuids = re.findall(uuid_pattern, QR_DATA, re.IGNORECASE)
print(f"Found UUIDs: {uuids}")

# Look for hex patterns that might be IDs
hex_pattern = r'[0-9a-fA-F]{32,}'
hex_matches = re.findall(hex_pattern, QR_DATA)
print(f"Found hex strings: {hex_matches}")

# Extract transaction ID
txn_pattern = r'Txn_[A-Za-z0-9]+'
txn_matches = re.findall(txn_pattern, QR_DATA)
print(f"Transaction IDs: {txn_matches}")

# Look for wallet/bank identifiers
print(f"\nTag 28 (Merchant Account Info): {parsed.get('28', 'NOT FOUND')}")
if '28' in parsed:
    print("  This tag typically contains the merchant account identifier")
    sub_data = parse_constructed_data(parsed['28'])
    print(f"  Sub-data: {sub_data}")

print("\n=== Notes ===")
print("- The CBE_APP_ID and CBE_APP_VERSION should be provided by CBE")
print("- They are typically NOT embedded in the QR code")
print("- Check your CBE merchant dashboard or contact CBE support")
print("- You may need to use the merchant/wallet ID from tag 28")
