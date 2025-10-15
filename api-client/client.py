import requests

def send_success_callback(session_id, customer_name, receiver, payer, payment_datetime, transferred_amount, vat, total_debited, vat_receipt_no):
    """
    Sends a POST request to the AkerBingo CBE wallet manual callback success endpoint
    with the specified payload.

    Args:
        session_id (str): Session ID of the transaction
        customer_name (str): Customer's name
        receiver (str): Receiver's name
        payer (str): Payer's name
        payment_datetime (str): Payment date and time
        transferred_amount (str): Amount transferred
        vat (str): VAT amount
        total_debited (str): Total debited amount
        vat_receipt_no (str): VAT receipt number

    Returns:
        requests.Response: Response object returned by the POST request
    """
    url = "https://akerbingo.com/api/v1/wallet/manual/callback/cbe/success/"
    payload = {
        "session_id": session_id,
        "status": "success",
        "message": "Transaction verified successfully",
        "data": {
            "Customer Name": customer_name,
            "Receiver": receiver,
            "Payer": payer,
            "Payment Date & Time": payment_datetime,
            "Transferred Amount": transferred_amount,
            "VAT": vat,
            "Total Debited": total_debited,
            "VAT Receipt No:": vat_receipt_no,
        }
    }
    response = requests.post(url, json=payload)
    return response


response = send_success_callback("5398ce5a-cb4d-48d0-bc6c-f222c3d0a8ec", "TINSAE ALAKO ABIYO", "AZEB BEHAILU MEKONEN", "TINSAE ALAKO ABIYO", "10/15/2025, 11:49:00 AM", "10.00 ETB", "8 ETB", "8 ETB", "FT252888G5X9")
print("Response:", response.status_code)
print("Response Body:", response.text)