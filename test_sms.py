#!/usr/bin/env python3
"""
Test script for Mobile Sasa SMS API credentials
Run this to verify your API token is working
"""

import requests
import json

def test_mobile_sasa_credentials():
    # Replace these with your actual credentials
    API_TOKEN = "***"  # Your Mobile Sasa API token
    SENDER_ID = "MOBILESASA"  # Your sender ID or use the default
    
    # Test phone number (use your own number for testing)
    TEST_PHONE = "254711000000"  # Replace with your phone number (without +)
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_TOKEN}"
    }
    
    payload = {
        "senderID": SENDER_ID,
        "message": "Test SMS from Savannah API using Mobile Sasa",
        "phone": TEST_PHONE
    }
    
    print(f"Testing Mobile Sasa SMS API with:")
    print(f"API Token: {API_TOKEN[:20]}...")
    print(f"Sender ID: {SENDER_ID}")
    print(f"Phone: {TEST_PHONE}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        response = requests.post(
            "https://api.mobilesasa.com/v1/send/message",
            headers=headers,
            json=payload
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        print()
        
        if response.status_code == 200:
            print("✅ SUCCESS: SMS sent successfully!")
            try:
                result = response.json()
                print(f"Response Data: {json.dumps(result, indent=2)}")
            except:
                print("Response is not JSON format")
        elif response.status_code == 401:
            print("❌ ERROR: Invalid authentication - check your API token")
        elif response.status_code == 400:
            print("❌ ERROR: Bad request - check your payload format")
        else:
            print(f"❌ ERROR: Unexpected status code {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_api_endpoint():
    """Test if the API endpoint is reachable"""
    try:
        response = requests.get("https://api.mobilesasa.com", timeout=10)
        print(f"✅ Mobile Sasa API endpoint is reachable (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Cannot reach Mobile Sasa API: {e}")

if __name__ == "__main__":
    print("=== Mobile Sasa SMS API Test ===\n")
    test_api_endpoint()
    print()
    test_mobile_sasa_credentials()