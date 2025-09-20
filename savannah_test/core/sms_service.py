import requests
import os
from django.conf import settings

def send_sms_notification(order_data):
    """Send SMS notification for new order"""
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
    import os
    
    # Skip SMS sending during testing
    if os.getenv('TESTING') == 'True':
        print(f"TEST MODE: Would send SMS to {phone_number}: {message}")
        return {"status": "test", "message": "SMS sent in test mode"}
    
    api_key = settings.AFRICAS_TALKING_API_KEY
    username = settings.AFRICAS_TALKING_USERNAME
    sandbox = settings.AFRICAS_TALKING_SANDBOX
    
    if not all([api_key, username]):
        print("SMS credentials not configured. Skipping SMS send.")
        return None
        
    base_url = "https://api.sandbox.africastalking.com" if sandbox else "https://api.africastalking.com"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "apiKey": api_key
    }
    
    data = {
        "username": username,
        "to": phone_number,
        "message": message,
        "from": "OrderService"
    }
    
    try:
        response = requests.post(
            f"{base_url}/version1/messaging",
            headers=headers,
            data=data
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Failed to send SMS: {e}")
        return None