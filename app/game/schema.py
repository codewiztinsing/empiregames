from ninja import Schema
from .models import GameType

class PlayerSchema(Schema):
    playerId: int
    numberOfBoards: int




class BetSchema(Schema):
    players: list[PlayerSchema]
    game_id: int
    bet_amount: float
    total_players: int = None
    fake_players: int = None
  

    


class GameSchema(Schema):
    game_id: int
    bet_amount: int


class WinGameSchema(Schema):
    player: str  # Can be telegram_id (int as string) or "BOT_FAKE"
    game_id: int
    win_amount: float
    bet_amount: float = None  # Optional field sent from Node.js
    total_players: int = None  # Optional field sent from Node.js


class NextGameSchema(Schema):
    bet_amount: int




class GameSettingsSchema(Schema):
    game_speed: int
    count_down_time: int
    # Fake player settings
    max_fake_players: int
    calls_before_fake_winner: int
    real_players_threshold: int
    fake_players_can_win: bool
    

class GameType(Schema):
    bet_amount: int
    commission: int

class GameTypeSchema(Schema):
    game_types: list[GameType]
