import requests
import os
from django.conf import settings

def send_sms_notification(order_data):
    """Send SMS notification for new order using Mobile Sasa API"""
    phone_number = order_data.get('customer_phone')
    customer_name = order_data.get('customer_name')
    item = order_data.get('item')
    amount = order_data.get('amount')
    
    if not all([phone_number, customer_name, item, amount]):
        print("Missing order data for SMS notification")
        return None
    
    message = f"Hello {customer_name}! Your order for {item} worth KES {amount:.2f} has been received. Thank you!"
    
    return send_sms(phone_number, message)

def send_sms(phone_number, message):
    """Send SMS using Mobile Sasa API"""
    import os
    
    # Skip SMS sending during testing
    if os.getenv('TESTING') == 'True':
        print(f"TEST MODE: Would send SMS to {phone_number}: {message}")
        return {"status": "test", "message": "SMS sent in test mode"}
    
    # Mobile Sasa API configuration
    api_token = getattr(settings, 'MOBILE_SASA_API_TOKEN', None)
    sender_id = getattr(settings, 'MOBILE_SASA_SENDER_ID', 'MOBILESASA')
    
    if not api_token:
        print("Mobile Sasa API token not configured. Skipping SMS send.")
        return None
    
    # Mobile Sasa API endpoint
    api_url = "https://api.mobilesasa.com/v1/send/message"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    
    # Ensure phone number is in correct format (remove + if present)
    clean_phone = phone_number.replace('+', '')
    
    payload = {
        "senderID": sender_id,
        "message": message,
        "phone": clean_phone
    }
    
    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=payload
        )
        
        print(f"Mobile Sasa SMS Response: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"SMS sent successfully to {phone_number}")
            return result
        else:
            print(f"Failed to send SMS: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error sending SMS via Mobile Sasa: {e}")
        return None