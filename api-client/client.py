data = {
  "player": '1464395537',
  "win_amount": '10',
  "game_id": 1
  
}

import requests

url = "http://127.0.0.1:8000/api/v1/game/win-game/"
headers = {
  "Content-Type": "application/json",
  "Accept": "application/json"
}

response = requests.post(url, json=data, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")