import requests
import json

def create_payment_receiver(base_url, phone_number=None, account_number=None):
    """
    Create a payment receiver
    
    Args:
        base_url (str): The base URL of the API
        phone_number (str, optional): Phone number of the receiver
        account_number (str, optional): Account number of the receiver
    
    Returns:
        dict: Response from the API
    """
    url = f"{base_url}/api/v1/payments/receivers"
    
    payload = {}
    if phone_number:
        payload['phoneNumber'] = phone_number
    if account_number:
        payload['accountNumber'] = account_number
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'message': f'Request failed: {str(e)}'
        }

def get_payment_receivers(base_url):
    """
    Get all payment receivers
    
    Args:
        base_url (str): The base URL of the API
    
    Returns:
        dict: Response from the API
    """
    url = f"{base_url}/api/v1/payments/receivers"

    try:
        response = requests.get(url)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'message': f'Request failed: {str(e)}'
        }

if __name__ == "__main__":
    base_url = "https://server.akerbingo.com"
    print(get_payment_receivers(base_url))
    print(create_payment_receiver(base_url, phone_number="0912345678", account_number="1234567890"))