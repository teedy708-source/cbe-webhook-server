#!/usr/bin/env python3
"""
EMV QR Code Decoder for CBE Transactions
Parses and displays structured data from EMV-format QR codes
"""

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

# EMV Tag meanings (based on CBE QR standard)
EMV_TAG_MEANINGS = {
    "00": "Payload Format Indicator",
    "01": "Point of Initiation Method",
    "28": "Merchant Account Information",
    "29": "Merchant Account Information",
    "52": "Merchant Category Code",
    "53": "Transaction Currency",
    "54": "Transaction Amount",
    "58": "Country Code",
    "59": "Merchant Name",
    "60": "Merchant City",
    "61": "Postal Code",
    "62": "Additional Data Field Template",
    "63": "CRC",
    "80": "Merchant Information Language Template",
    "81": "Merchant Information Language Template",
    "87": "Unreserved Templates",
}

if __name__ == "__main__":
    # Test QR code from your session
    qr_string = "00020101021128360003CBE0108CBETETAA0213100069863451452040000530323054128208750000.05802ET5922Tewodros Ayele Zeberga6011Addis Ababa87130003cbe01021280240008etswitch0108Txn_10036304012E"
    
    print("=" * 80)
    print("EMV QR CODE DECODER")
    print("=" * 80)
    print(f"\nRaw QR String ({len(qr_string)} chars):\n{qr_string}\n")
    
    parsed = parse_emv_qr(qr_string)
    
    print("Parsed Data:")
    print("-" * 80)
    
    for tag, value in sorted(parsed.items()):
        meaning = EMV_TAG_MEANINGS.get(tag, "Unknown Tag")
        print(f"Tag {tag}: {meaning}")
        print(f"  Value: {value}")
        print()
    
    print("=" * 80)
    print("KEY EXTRACTED FIELDS:")
    print("=" * 80)
    print(f"Transaction Amount (Tag 54): {parsed.get('54')} ETB")
    print(f"Merchant Name (Tag 59): {parsed.get('59')}")
    print(f"Merchant City (Tag 60): {parsed.get('60')}")
    print(f"Transaction ID (Tag 08 in Template 87): {parsed.get('87')}")
    print(f"Currency (Tag 53): {parsed.get('53')}")
    print(f"Country Code (Tag 58): {parsed.get('58')}")
