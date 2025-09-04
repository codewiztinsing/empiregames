from decouple import config 
import requests
import time

apiKey = config("ADDISPAY_API_KEY")
baseUrl = config("ADDISPAY_BASE_URL")


def generate_nonce():
    nonce = f"addispay{int(time.time())}"
    return nonce

def generate_tx_ref():
    tx_ref = f"addispay{int(time.time())}"
    return tx_ref

def create_session(amount, currency, email, first_name, last_name, phone_number, tx_ref, callback_url, return_url, customization):
    payment_data =  payment_data = {
    "data": {
        "redirect_url": "https://wowliyubingo.com",
        "cancel_url": "https://wowliyubingo.com/cancel",
        "success_url": "https://wowliyubingo.com/success",
        "error_url": "https://wowliyubingo.com",
        "order_reason": "Wow Bingo deposit",
        "currency": "ETB",
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "nonce": generate_nonce(),
        "order_detail": {
            "amount": amount,
            "description": "Wow Bingo deposit",
        },
        "phone_number": phone_number,
        "session_expired": "5000",
        "total_amount": f"{amount}",
        "tx_ref": tx_ref,
    },
    "message": "Wow Bingo deposit",
}
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Auth":apiKey
    }
    response = requests.post(f"{baseUrl}/create-order", json=payment_data, headers=headers)
    print("response = ",response.json())
    if response.status_code == 200:
        return {
                "status": "success",
                "status_code": response.status_code,
                "data": response.json()
            }
    else:
        return {
            "status": "error",
            "status_code": response.status_code,
            "data": "Unknown error"
        }


def withdraw_funds(amount, currency, email, first_name, last_name, phone_number, tx_ref, callback_url, return_url, customization):
    payout_payment_data = {
    "data": {
        "cancel_url": "https://wowliyubingo.com/cancel",
        "success_url": "https://example.com/success",
        "error_url": "https://example.com/error",
        "order_reason": "Wow Bingo withdrawal",
        "currency": "ETB",
        "customer_name": f"{first_name} {last_name}",
        "phone_number": phone_number,
        "nonce": f"payout{int(time.time())}",
        "payment_method": "telebirr",
        "total_amount": f"{amount}",
        "tx_ref": f"payout-{int(time.time())}",
    },
    "message": "Wow Bingo withdrawal",
}


    url = f"{baseUrl}/payment/direct-b2c"
    print("withdraw_funds url = ",url)
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Auth": apiKey,
    }

    try:
        response = requests.post(url, json=payout_payment_data, headers=headers)
        response.raise_for_status()  # Raise error if response is not 200
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error processing payout: {e}")
        raise

if __name__ == "__main__":
    print(create_session(100, "ETB", "test@gmail.com", "Abebe", "Kebede", "251921309013", generate_tx_ref(), "https://wowliyubingo.com/success", "https://wowliyubingo.com/cancel", {}))
    print(withdraw_funds(100, "ETB", "test@gmail.com", "Abebe", "Kebede", "251921309013", generate_tx_ref(), "https://wowliyubingo.com/success", "https://wowliyubingo.com/cancel", {}))

