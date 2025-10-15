import requests

class ManualCallbackClient:
    BASE_URL = "https://akerbingo.com/api/v1/wallet/manual/callback/cbe/success/"

    @staticmethod
    def post_success_callback(session_id, message="Transaction verified successfully", data=None, status="success"):
        """
        Posts a success callback for CBE manual payment.

        Args:
            session_id (str): The session ID to use in the payload.
            message (str): The message to send.
            data (dict): Payment data. If None, uses example data.
            status (str): Status value (default: "success").
        Returns:
            requests.Response: The response object from the post.
        """
        if data is None:
            data = {
                "Customer Name": "TINSAE ALAKO ABIYO",
                "Receiver": "AZEB BEHAILU MEKONEN",
                "Payer": "TINSAE ALAKO ABIYO",
                "Payment Date & Time": "10/15/2025, 11:49:00 AM",
                "Transferred Amount": "10.00 ETB",
                "VAT": "8 ETB",
                "Total Debited": "8 ETB",
                "VAT Receipt No:": "FT252888G5X9",
            }
        payload = {
            "session_id": session_id,
            "status": status,
            "message": message,
            "data": data,
        }
        response = requests.post(ManualCallbackClient.BASE_URL, json=payload)
        return response

# Example usage:
client = ManualCallbackClient()
resp = client.post_success_callback("95365bb4-2f91-404c-8ca7-90edecda0141")
print(resp.status_code, resp.text)
