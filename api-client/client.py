import requests
import json

class WalletAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
    
    def create_withdrawal_request(self, telegram_id, amount):
        """
        Create a withdrawal request
        
        Args:
            telegram_id (str): User's telegram ID
            amount (float): Amount to withdraw
            
        Returns:
            dict: Response from the API
        """
        url = f"{self.base_url}/withdrawal/request/"
        
        payload = {
            "telegram_id": telegram_id,
            "amount": amount
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": response.json() if response.content else "Unknown error",
                    "status_code": response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }

# Example usage
if __name__ == "__main__":
    # Initialize the client
    client = WalletAPIClient("https://bilenbingo.com/api/v1/wallet")
    
    # Create a withdrawal request
    result = client.create_withdrawal_request(
        telegram_id="1464395537",
        amount=50.0
    )
    print("result = ",result)
    
    if result["success"]:
        print("Withdrawal request created successfully:")
        print(result["data"])
    else:
        print("Failed to create withdrawal request:")
        print(result["error"])
