import requests

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def post_telegram_auth(self, data, headers=None):
        """
        Send a POST request to /api/v1/users/telegram-auth

        :param data: The JSON data to send in the request body.
        :param headers: Optional dictionary of HTTP headers to send.
        :return: Response object from the requests library.
        """
        url = f"{self.base_url}/api/v1/users/telegram-auth"
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)
        response = requests.post(url, json=data, headers=default_headers)
        return response

# Example usage:
client = APIClient("http://localhost:8000")
payload = {"telegram_id": 123456789, "auth_code": "xyz123"}
resp = client.post_telegram_auth(payload)
print(resp.status_code, resp.json())
