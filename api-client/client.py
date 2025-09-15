data = {
  "players": [
    { "playerId": '7707233947', "numberOfBoards": 1 },
    { "playerId": '7408361547', "numberOfBoards": 1 },
    { "playerId": '6415994768', "numberOfBoards": 1 }
  ],
  "bet_amount": '10',
  "game_id": 8407
}

import requests

url = "https://wowliyubingo.com/api/v1/game/join-game/"
headers = {
  "Content-Type": "application/json",
  "Accept": "application/json"
}

response = requests.post(url, json=data, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")